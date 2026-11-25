'use strict';

/**
 * LinkedIn posts extractor: a person's or a company's posts, back to a cutoff date.
 *
 * Companion to linkedin-profile-extract.js, built the same way: browser-injected
 * (sets `window.LinkedInPosts`) and CommonJS (for the jsdom tests in
 * linkedin-posts-extract.test.js). Commands inject it; they never carry their own
 * parsing. Fix bugs here, with a test.
 *
 * Pages it reads (read-only; it never reacts, comments, follows or connects):
 *   person:  https://www.linkedin.com/in/<slug>/recent-activity/all/
 *   company: https://www.linkedin.com/company/<slug>/posts/?feedView=all
 *
 * How it finds posts, most reliable first:
 *   1. DOM: elements carrying data-urn="urn:li:activity:<id>" (also
 *      urn:li:share / urn:li:ugcPost). Each becomes one post.
 *   2. Text fallback: the activity page's innerText labels each card
 *      "Feed post number N" (the anchor the enrich-profile command relies on);
 *      the text is split on that label. No URN, so no exact date or URL.
 *
 * Dates: an activity id is a snowflake whose top 41 bits are milliseconds since
 * the Unix epoch, so `id >> 22` gives the exact post time. That beats the
 * relative age label ("3mo", "1yr"), which is kept as a cross-check and is the
 * only date the text fallback has.
 *
 * The feed is long and lazily loaded, and a long scroll can overrun the browser
 * tool's ~45s per-call timeout. `collect()` therefore has a wall-clock budget and
 * keeps its state on `window.__posts`; call it again to resume until it reports
 * `done: true`.
 *
 * NOT YET VALIDATED LIVE for company pages. The DOM mode is written against
 * LinkedIn's long-standing data-urn markup; confirm on a first real run and
 * record what was found in the command's caveats.
 */

(function (root) {
  const sleep = ms => new Promise(r => setTimeout(r, ms));

  // ---------------------------------------------------------------------------
  // URLs
  // ---------------------------------------------------------------------------

  /** Activity-feed URL for a profile or company URL; null if not one. */
  function activityUrl(url) {
    if (!url) return null;
    const clean = String(url).split('?')[0].split('#')[0];
    let m = clean.match(/^(https?:\/\/(?:[\w-]+\.)?linkedin\.com\/in\/[^/]+)/i);
    if (m) return m[1] + '/recent-activity/all/';
    m = clean.match(/^(https?:\/\/(?:[\w-]+\.)?linkedin\.com\/company\/[^/]+)/i);
    if (m) return m[1] + '/posts/?feedView=all';
    return null;
  }

  function postUrl(urn) {
    return urn ? 'https://www.linkedin.com/feed/update/' + urn + '/' : '';
  }

  // ---------------------------------------------------------------------------
  // Dates
  // ---------------------------------------------------------------------------

  /** Exact post time from an activity/share/ugcPost id, or null. */
  function dateFromUrn(urn) {
    const m = urn && String(urn).match(/urn:li:(?:activity|share|ugcPost):(\d{15,20})/);
    if (!m) return null;
    try {
      const ms = Number(BigInt(m[1]) >> 22n);
      // Sanity: LinkedIn ids decode to 2010 or later and not into the future.
      if (ms < Date.UTC(2010, 0, 1) || ms > Date.now() + 86400000) return null;
      return new Date(ms);
    } catch (e) {
      return null;
    }
  }

  /** Relative age label ("5d", "3mo", "1yr", "2 weeks") -> approximate age in days. */
  function ageToDays(label) {
    const m = label && String(label).trim().match(/^(\d+)\s*(s|m|h|d|w|mo|yr|y)\b|^(\d+)\s*(second|minute|hour|day|week|month|year)s?\b/i);
    if (!m) return null;
    const n = Number(m[1] || m[3]);
    const u = (m[2] || m[4]).toLowerCase();
    const per = {
      s: 0, second: 0, m: 0, minute: 0, h: 0, hour: 0,
      d: 1, day: 1, w: 7, week: 7, mo: 30, month: 30, yr: 365, y: 365, year: 365,
    };
    return n * per[u];
  }

  /** First age label in a block of text, e.g. "3mo • Edited •" -> "3mo". */
  function findAgeLabel(text) {
    const m = text && String(text).match(/(?:^|\s)(\d+\s*(?:mo|yr|w|d|h|m|s))\s*•/);
    return m ? m[1].replace(/\s+/g, '') : '';
  }

  function isoDay(d) {
    return d ? d.toISOString().slice(0, 10) : '';
  }

  // ---------------------------------------------------------------------------
  // DOM helpers
  // ---------------------------------------------------------------------------

  function elText(el) {
    if (!el) return '';
    return (el.innerText !== undefined ? el.innerText : el.textContent) || '';
  }

  function scroller(doc) {
    doc = doc || document;
    return doc.getElementById('workspace') || doc.scrollingElement || doc.documentElement;
  }

  const URN_SELECTOR = '[data-urn^="urn:li:activity:"], [data-urn^="urn:li:share:"], [data-urn^="urn:li:ugcPost:"]';

  const TEXT_SELECTORS = [
    '.update-components-text',
    '.feed-shared-inline-show-more-text',
    '.feed-shared-update-v2__description',
    '.feed-shared-text',
  ];

  const ACTOR_SELECTORS = [
    '.update-components-actor__title',
    '.update-components-actor__name',
    '.feed-shared-actor__name',
  ];

  /** Top-level post containers only (a repost nests the original's urn inside). */
  function postContainers(doc) {
    const all = [].slice.call((doc || document).querySelectorAll(URN_SELECTOR));
    return all.filter(el => !all.some(other => other !== el && other.contains(el)));
  }

  function firstMatchText(container, selectors) {
    for (const sel of selectors) {
      const found = [].slice.call(container.querySelectorAll(sel)).map(elText).map(s => s.trim()).filter(Boolean);
      if (found.length) return found.sort((a, b) => b.length - a.length)[0];
    }
    return '';
  }

  function cleanPostText(text) {
    return String(text || '')
      .replace(/(?:…|\.\.\.)\s*(?:see\s+)?more\s*$/i, '')
      .replace(/\n{3,}/g, '\n\n')
      .trim();
  }

  function countFrom(text, word) {
    const m = String(text || '').match(new RegExp('([\\d][\\d,.]*\\s*[KkMm]?)\\s+' + word, 'i'));
    return m ? m[1].replace(/\s+/g, '') : '';
  }

  /** Read one post container into a record. Pure: no clicks, no scrolling. */
  function parseContainer(container) {
    const urn = container.getAttribute('data-urn');
    const whole = elText(container);
    const head = whole.slice(0, 300);
    const date = dateFromUrn(urn);
    const age = findAgeLabel(whole);
    let text = firstMatchText(container, TEXT_SELECTORS);
    let textSource = 'selector';
    if (!text) {
      // Fallback: the card's text minus its first few header lines.
      text = whole.split('\n').slice(4).join('\n');
      textSource = 'card';
    }
    return {
      urn: urn,
      url: postUrl(urn),
      date: isoDay(date),
      date_source: date ? 'urn' : (age ? 'age' : ''),
      age: age,
      kind: /\breposted this\b/i.test(head) ? 'repost' : 'post',
      author: firstMatchText(container, ACTOR_SELECTORS).split('\n')[0],
      text: cleanPostText(text),
      text_source: textSource,
      reactions: countFrom(whole, 'reactions?'),
      comments: countFrom(whole, 'comments?'),
      reposts: countFrom(whole, 'reposts?'),
    };
  }

  /** Text fallback: split the page's innerText on "Feed post number N". */
  function parseFromText(text) {
    const parts = String(text || '').split(/Feed post number \d+/).slice(1);
    return parts.map(chunk => {
      const lines = chunk.split('\n').map(s => s.trim()).filter(Boolean);
      const head = lines.slice(0, 6).join('\n');
      return {
        urn: '', url: '', date: '', date_source: findAgeLabel(chunk) ? 'age' : '',
        age: findAgeLabel(chunk),
        kind: /\breposted this\b/i.test(head) ? 'repost' : 'post',
        author: lines[0] || '',
        text: cleanPostText(lines.slice(4).join('\n')),
        text_source: 'text',
        reactions: countFrom(chunk, 'reactions?'),
        comments: countFrom(chunk, 'comments?'),
        reposts: countFrom(chunk, 'reposts?'),
      };
    });
  }

  /** Click "…more" inside THIS post only; never page-wide (see enrich-profile caveats). */
  async function expandPost(container) {
    const btn = [].slice.call(container.querySelectorAll('button'))
      .find(b => /^(…\s*more|see more|\.\.\.more|\.\.\.\s*see more|…see more)$/i.test(elText(b).trim()));
    if (!btn) return false;
    btn.click();
    await sleep(300);
    return true;
  }

  /** The feed's own "Show more results" button at the bottom, if any. */
  function showMoreButton(doc) {
    return [].slice.call((doc || document).querySelectorAll('button'))
      .find(b => /^show more results$/i.test(elText(b).trim())) || null;
  }

  // ---------------------------------------------------------------------------
  // Collection
  // ---------------------------------------------------------------------------

  function cutoffDate(opts, now) {
    if (opts && opts.since) return new Date(opts.since + 'T00:00:00Z');
    const months = opts && opts.months !== undefined ? opts.months : 12;
    const d = new Date(now || Date.now());
    d.setUTCMonth(d.getUTCMonth() - months);
    return d;
  }

  function isOlderThan(post, cutoff, now) {
    if (post.date) return new Date(post.date + 'T00:00:00Z') < cutoff;
    const days = ageToDays(post.age);
    if (days === null) return false;
    const approx = new Date((now || Date.now()) - days * 86400000);
    return approx < cutoff;
  }

  function newState(opts, now) {
    return {
      cutoff: isoDay(cutoffDate(opts, now)),
      posts: {},           // key -> record, insertion-ordered
      order: [],
      mode: '',            // 'dom' | 'text'
      rounds: 0,
      stalls: 0,
      reachedCutoff: false,
      done: false,
      started: new Date(now || Date.now()).toISOString(),
    };
  }

  function addPost(state, post) {
    const key = post.urn || (post.author + '|' + post.age + '|' + post.text.slice(0, 80));
    if (state.posts[key]) return false;
    state.posts[key] = post;
    state.order.push(key);
    return true;
  }

  /** Read whatever posts are rendered now into state. Returns how many were new. */
  async function harvest(doc, state, opts) {
    const containers = postContainers(doc);
    let added = 0;
    if (containers.length) {
      state.mode = 'dom';
      for (const c of containers) {
        if (!opts || opts.expand !== false) await expandPost(c);
        if (addPost(state, parseContainer(c))) added++;
      }
    } else {
      state.mode = state.mode || 'text';
      for (const p of parseFromText(elText(doc.body))) if (addPost(state, p)) added++;
    }
    return added;
  }

  /**
   * Scroll the feed and collect posts until the cutoff is passed, the feed stops
   * growing, or the time budget runs out. Resumable: state lives on
   * root.__posts; pass { reset: true } to start over.
   */
  async function collect(doc, opts) {
    doc = doc || document;
    opts = opts || {};
    const maxMs = opts.maxMs !== undefined ? opts.maxMs : 30000;
    const stepMs = opts.stepMs !== undefined ? opts.stepMs : 1500;
    const maxStalls = opts.maxStalls !== undefined ? opts.maxStalls : 3;
    const now = opts.now;
    if (opts.reset || !root.__posts) root.__posts = newState(opts, now);
    const state = root.__posts;
    const cutoff = new Date(state.cutoff + 'T00:00:00Z');
    const deadline = Date.now() + maxMs;
    const sc = scroller(doc);

    while (!state.done && Date.now() < deadline) {
      state.rounds++;
      const added = await harvest(doc, state, opts);
      const all = state.order.map(k => state.posts[k]);
      // Reposts carry the original's date, so only the owner's own posts decide the cutoff.
      const own = all.filter(p => p.kind === 'post');
      const last = (own.length ? own : all).slice(-1)[0];
      if (last && isOlderThan(last, cutoff, now)) { state.reachedCutoff = true; state.done = true; break; }
      state.stalls = added ? 0 : state.stalls + 1;
      if (state.stalls >= maxStalls) { state.done = true; break; }
      const more = showMoreButton(doc);
      if (more) more.click();
      sc.scrollTop = sc.scrollHeight;
      await sleep(stepMs);
    }
    return receipt(state);
  }

  /** Posts kept: within the cutoff (reposts kept too, marked as such). */
  function keptPosts(state, now) {
    state = state || root.__posts;
    const cutoff = new Date(state.cutoff + 'T00:00:00Z');
    return state.order.map(k => state.posts[k]).filter(p => !isOlderThan(p, cutoff, now));
  }

  /** Short receipt safe to return through javascript_tool's 1000-char cap. */
  function receipt(state) {
    state = state || root.__posts;
    const all = state.order.map(k => state.posts[k]);
    const dated = all.filter(p => p.date).map(p => p.date).sort();
    return {
      mode: state.mode, rounds: state.rounds, found: all.length,
      kept: keptPosts(state).length,
      reposts: all.filter(p => p.kind === 'repost').length,
      newest: dated.slice(-1)[0] || '', oldest: dated[0] || '',
      undated: all.filter(p => !p.date).length,
      cutoff: state.cutoff, reachedCutoff: state.reachedCutoff, done: state.done,
      visibility: typeof document !== 'undefined' ? document.visibilityState : '',
    };
  }

  // ---------------------------------------------------------------------------
  // Payload out (same 3-call pattern as the profile extractor)
  // ---------------------------------------------------------------------------

  const FIELDS = [
    ['URL', 'url'], ['DATE', 'date'], ['AGE', 'age'], ['KIND', 'kind'], ['AUTHOR', 'author'],
    ['REACTIONS', 'reactions'], ['COMMENTS', 'comments'], ['REPOSTS', 'reposts'], ['TEXT', 'text'],
  ];

  function serialisePosts(posts) {
    let out = '';
    posts.forEach((p, i) => {
      out += '<<<POST ' + (i + 1) + '>>>\n';
      for (const f of FIELDS) if (p[f[1]]) out += '<<<' + f[0] + '>>>\n' + p[f[1]] + '\n';
    });
    return out + '<<<END ' + posts.length + '>>>';
  }

  /** Parse serialisePosts output back into records (used by the capture step and tests). */
  function parsePayload(payload) {
    const body = String(payload || '');
    const end = body.match(/<<<END (\d+)>>>\s*$/);
    if (!end) throw new Error('payload incomplete: END sentinel missing');
    const posts = body.split(/<<<POST \d+>>>\n/).slice(1).map(block => {
      const rec = {};
      const re = /<<<([A-Z]+)>>>\n([\s\S]*?)(?=\n<<<[A-Z]+(?: \d+)?>>>|$)/g;
      let m;
      while ((m = re.exec(block))) {
        const f = FIELDS.find(x => x[0] === m[1]);
        if (f) rec[f[1]] = m[2];
      }
      return rec;
    });
    if (posts.length !== Number(end[1])) throw new Error('payload incomplete: ' + posts.length + ' of ' + end[1]);
    return posts;
  }

  /**
   * Write kept posts into the DOM for get_page_text. Destroys the page; call last.
   * textContent, never innerHTML: post text is untrusted input. `from`/`count`
   * page through a large set if one get_page_text read is too big.
   */
  function writePayloadToDom(doc, opts) {
    doc = doc || document;
    opts = opts || {};
    const posts = keptPosts(root.__posts, opts.now);
    const from = opts.from || 0;
    const slice = posts.slice(from, opts.count ? from + opts.count : undefined);
    const payload = serialisePosts(slice);
    const art = doc.createElement('article');
    art.textContent = payload;
    doc.body.innerHTML = '';
    doc.body.appendChild(art);
    return { chars: payload.length, posts: slice.length, total: posts.length };
  }

  const api = {
    activityUrl, postUrl, dateFromUrn, ageToDays, findAgeLabel, isoDay,
    scroller, postContainers, parseContainer, parseFromText, expandPost, showMoreButton,
    cutoffDate, isOlderThan, newState, addPost, harvest, collect, keptPosts, receipt,
    serialisePosts, parsePayload, writePayloadToDom,
  };

  root.LinkedInPosts = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
