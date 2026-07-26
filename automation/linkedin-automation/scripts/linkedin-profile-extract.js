'use strict';

/**
 * LinkedIn person-profile extractor.
 *
 * Ported from METIS's Chrome-extension profile parser (the copy kept at
 * `~/dev/METIS-specs/linkedin-about/code/`, itself extracted from
 * `extension/chrome/linkedin/` + `content.js`). That parser is the reliable
 * implementation; the hand-rolled extraction that previously lived inline in
 * `.claude/commands/linkedin-enrich-profile.md` kept missing About and other
 * sections, so this file replaces it.
 *
 * What came from where:
 *   - nameFromTitle                                   ← shared/title.js
 *   - firstText / findSectionById / findSectionByHeading /
 *     extractAboutText / buildDescription /
 *     getPersonCardContainer                          ← shared/dom.js
 *   - classify/isLinkedIn/normalise URL               ← shared/url.js
 *   - waitForContent + READINESS_SELECTORS            ← shared/readiness.js
 *   - connection count / current position / education ← content.js extractFullProfile
 *
 * What is local to this repo and deliberately kept (all of it earned by live
 * debugging — see the caveats in `.claude/commands/linkedin-enrich-profile.md`):
 *   - `MAIN#workspace` scrolling (`window.scrollTo` is a no-op on profiles) and
 *     the multi-pass hydration loop for virtualised sections.
 *   - The topcard walk-up that requires BOTH "Contact info" and a
 *     connections/followers count, which yields degree / company / school /
 *     followers / connections / mutuals — richer than the upstream
 *     "container with 4+ children" heuristic.
 *   - The opportunistic `other_info` scan over remaining h2 sections.
 *   - Throttle detection (missing fields AND collapsed structure) plus retry.
 *   - Scoped "…more" expansion only — never page-wide.
 *
 * Dual-mode, like the upstream files: works as a browser-injected script (sets
 * `window.LinkedInProfile`) and as a CommonJS module (for jsdom tests).
 */

(function (root) {
  // ---------------------------------------------------------------------------
  // shared/url.js
  // ---------------------------------------------------------------------------

  function classifyLinkedInSurface(url) {
    if (!url) return null;
    if (/linkedin\.com\/in\/[^/?#]+/.test(url))                   return 'person_profile';
    if (/linkedin\.com\/company\/[^/?#]+\/about(\/|$)/.test(url)) return 'company_about';
    if (/linkedin\.com\/company\/[^/?#]+/.test(url))              return 'company_overview';
    if (/linkedin\.com\/messaging(\/|$)/.test(url))               return 'messaging_thread';
    if (/linkedin\.com\/search\/results\/people/.test(url))       return 'search_people';
    return null;
  }

  function isLinkedInUrl(url) {
    if (!url) return false;
    try {
      const host = new URL(url).hostname.toLowerCase();
      return host === 'linkedin.com' || host.endsWith('.linkedin.com');
    } catch (e) {
      return false;
    }
  }

  /** https://www.linkedin.com/in/example/detail/contact-info/ → https://www.linkedin.com/in/example/ */
  function normaliseLinkedInUrl(url) {
    try {
      const u = new URL(url);
      const parts = u.pathname.replace(/^\//, '').replace(/\/$/, '').split('/');
      return 'https://www.linkedin.com/' + parts[0] + '/' + parts[1] + '/';
    } catch (e) {
      return url;
    }
  }

  function extractPersonSlug(url) {
    const m = (url || '').match(/linkedin\.com\/in\/([^/?#]+)/);
    return m ? m[1] : null;
  }

  // ---------------------------------------------------------------------------
  // shared/title.js
  // ---------------------------------------------------------------------------

  /** "(3) Ada Lovelace | LinkedIn" → "Ada Lovelace". '' if implausible. */
  function nameFromTitle(title) {
    if (!title) return '';
    let name = title.replace(/^\(\d+\)\s*/, '');
    name = name.replace(/\s*[|\-—]\s*LinkedIn.*$/i, '').trim();
    const sep = name.search(/\s+[|\-—:]/);
    const namePart = sep > 0 ? name.slice(0, sep).trim() : name;
    return namePart.length > 0 && namePart.length < 80 ? namePart : '';
  }

  // ---------------------------------------------------------------------------
  // shared/dom.js
  // ---------------------------------------------------------------------------

  function firstText(doc) {
    const selectors = [].slice.call(arguments, 1);
    for (const sel of selectors) {
      const el = doc.querySelector(sel);
      const text = el && el.textContent ? el.textContent.trim() : '';
      if (text) return text;
    }
    return '';
  }

  function findSectionById(doc, id) {
    const el = doc.getElementById(id);
    if (!el) return null;
    return el.closest('section') || el;
  }

  function findSectionByHeading(doc, text) {
    for (const h of doc.querySelectorAll('h2, h3')) {
      if (h.textContent.trim() === text) return h.closest('section') || h.parentElement;
    }
    return null;
  }

  /**
   * Walk up from a heading until the ancestor carries more than just the
   * heading itself. Used when a section has no id/aria-label/<section> wrapper,
   * which is the common case on the current profile layout.
   *
   * Checks `parentElement` in the loop condition *before* reassigning: if the
   * chain runs out before the threshold is met, `el` stays at the last real
   * element instead of becoming null and crashing the next read.
   */
  function sectionFromHeadingWalkUp(doc, headingText, minChars) {
    const h = [].slice.call(doc.querySelectorAll('h2, h3'))
      .find(x => (x.innerText || x.textContent || '').trim() === headingText);
    if (!h) return null;
    const floor = minChars !== undefined ? minChars : headingText.length + 20;
    let el = h;
    for (let i = 0; i < 6 && el.parentElement; i++) {
      el = el.parentElement;
      if (elText(el).trim().length > floor) break;
    }
    return el === h ? null : el;
  }

  /** innerText where available (browser), textContent otherwise (jsdom). */
  function elText(el) {
    if (!el) return '';
    return (el.innerText !== undefined && el.innerText !== null ? el.innerText : el.textContent) || '';
  }

  function findAboutSection(doc) {
    return (
      findSectionById(doc, 'about') ||
      doc.querySelector('section[aria-label="About"]') ||
      findSectionByHeading(doc, 'About') ||
      sectionFromHeadingWalkUp(doc, 'About', 200)
    );
  }

  /**
   * Longest text node inside a section. LinkedIn scrambles class names on every
   * deploy, so this looks at the structural candidates (aria-hidden spans are
   * where the real copy lives; `p` / `.break-words` cover older renders) and
   * takes the longest.
   */
  function longestTextIn(section) {
    if (!section) return '';
    const candidates = [].concat(
      [].slice.call(section.querySelectorAll('span[aria-hidden="true"]')),
      [].slice.call(section.querySelectorAll('p, .pv-about__summary-text, span.break-words'))
    );
    let best = '';
    for (const el of candidates) {
      // elText, not textContent: LinkedIn renders About as one span containing
      // <br>-separated paragraphs, and textContent welds them together
      // ("…to nature.After three decades…"). Measured live on a real profile.
      const t = elText(el).trim();
      if (t.length > best.length) best = t;
    }
    return best;
  }

  /** Upstream signature kept for compatibility: About text straight off a document. */
  function extractAboutText(doc) {
    const section = findAboutSection(doc);
    if (!section) return '';
    let best = longestTextIn(section);
    if (!best) {
      best = [].slice.call(section.childNodes)
        .filter(n => ['H1', 'H2', 'H3', 'H4'].indexOf(n.nodeName) === -1)
        .map(n => (n.textContent || '').trim())
        .join(' ')
        .trim();
    }
    return best.length > 20 ? best : '';
  }

  /** Strip a leading heading line and a trailing "…more" label from section text. */
  function cleanSectionText(text, heading) {
    let t = (text || '').trim();
    if (heading) {
      const escaped = heading.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      t = t.replace(new RegExp('^' + escaped + '\\s*\\n+'), '');
    }
    return t.replace(/\n*…\s*more$/i, '').trim();
  }

  function buildDescription(summary, about) {
    const s = (summary || '').trim();
    const a = (about || '').trim();
    if (s && a) return (s + '\n\n' + a).slice(0, 1000);
    return (s || a).slice(0, 1000);
  }

  /**
   * Upstream top-card locator: the h2 whose text is exactly the name, walked up
   * until a container has 4+ direct children. Used here only as a fallback —
   * `getTopcardContainer` below is stricter and yields more fields.
   */
  function getPersonCardContainer(doc, name) {
    if (!name) return null;
    const nameEl = [].slice.call(doc.querySelectorAll('h2'))
      .find(el => el.textContent.trim() === name);
    if (!nameEl) return null;
    let el = nameEl.parentElement;
    for (let i = 0; i < 10; i++) {
      if (!el) break;
      if (el.children.length >= 4) return el;
      el = el.parentElement;
    }
    return null;
  }

  /**
   * Repo-local top-card locator.
   *
   * Stopping at a bare `innerText.length > 150` lands on the container holding
   * name/headline/location/"Contact info" but NOT the connections/followers
   * count or the mutual-connections line, which live one ancestor further up
   * (measured 226 vs 311 chars on the same profile). So require both markers,
   * with a length cap to avoid drifting into page chrome.
   */
  /**
   * Loose name comparison for locating the top-card heading.
   *
   * A raw `startsWith(title.slice(0, 12))` breaks whenever the rendered heading
   * and the tab title disagree — measured live: `document.title` was
   * "Beatrice Ungard, Ph.D." while the on-page heading read
   * "Beatrice (Benne) Ungard, Ph.D.", so the probe "Beatrice Ung" never matched
   * "Beatrice (Ben", the container was never found, and EVERY top-card field
   * (degree, location, company, school, followers, connections, mutuals) came
   * back empty on an otherwise perfectly healthy profile. Nicknames in
   * parentheses are common, so strip them and compare on letters only.
   */
  function nameMatches(headingText, title) {
    const norm = s => (s || '')
      .replace(/\([^)]*\)/g, ' ')
      .replace(/[^\p{L}\p{N} ]/gu, ' ')
      .replace(/\s+/g, ' ')
      .trim()
      .toLowerCase();
    const h = norm(headingText);
    const t = norm(title);
    if (!h || !t) return false;
    const probe = Math.min(12, h.length, t.length);
    return h.startsWith(t.slice(0, probe)) || t.startsWith(h.slice(0, probe));
  }

  function getTopcardContainer(doc, title) {
    if (!title) return null;
    const nameH = [].slice.call(doc.querySelectorAll('h1, h2'))
      .find(h => nameMatches(elText(h).trim().split('\n')[0], title));
    if (!nameH) return null;
    let c = nameH;
    for (let i = 0; i < 10 && c.parentElement; i++) {
      c = c.parentElement;
      const t = elText(c);
      if (t.indexOf('Contact info') !== -1 && /[\d,]+\+?\s*(connections|followers)/.test(t)) break;
      if (t.length > 600) break;
    }
    return c === nameH ? null : c;
  }

  // ---------------------------------------------------------------------------
  // shared/readiness.js
  // ---------------------------------------------------------------------------

  const READINESS_SELECTORS = {
    person_profile:   ['main h1', 'main h2'],
    company_overview: ['.org-top-card-summary__title', 'main h1'],
    company_about:    ['.org-top-card-summary__title', 'main h1'],
    messaging_thread: ['.msg-convo-wrapper', '.msg-thread', '[data-test-id="msg-thread-list-item--active"]'],
    search_people:    ['main'],
    unknown:          [],
  };

  function waitForContent(doc, surface, deadlineMs) {
    const ms = deadlineMs !== undefined ? deadlineMs : 3000;
    const selectors = READINESS_SELECTORS[surface] || [];
    if (selectors.length === 0) return Promise.resolve();
    return new Promise(resolve => {
      const deadline = Date.now() + ms;
      const interval = surface === 'messaging_thread' ? 200 : 150;
      const check = () => {
        const ready = selectors.some(sel => !!doc.querySelector(sel));
        if (ready || Date.now() >= deadline) resolve();
        else setTimeout(check, interval);
      };
      check();
    });
  }

  // ---------------------------------------------------------------------------
  // Hydration (repo-local — profile sections are virtualised)
  // ---------------------------------------------------------------------------

  const sleep = ms => new Promise(r => setTimeout(r, ms));

  function scroller(doc) {
    doc = doc || document;
    return doc.getElementById('workspace') || doc.scrollingElement || doc.documentElement;
  }

  /**
   * `window.scrollTo` is a no-op on profile pages — the real scroll container is
   * `MAIN#workspace`. Sections unmount again once scrolled past, so walk down in
   * passes and stop as soon as About has rendered.
   *
   * Bounded by a wall-clock budget, not just a pass count: `scrollHeight` GROWS
   * as sections load, so `y < sc.scrollHeight` is a moving target and a rich
   * profile can scroll for minutes. That overran the browser tool's 45s
   * per-call CDP timeout on the first live run (`Runtime.evaluate timed out`),
   * which kills the call while the page keeps scrolling — so keep the default
   * budget comfortably under it and call hydrate again if `aboutFound` is still
   * false. Repeated calls resume where the last left off, since the page state
   * persists between them.
   */
  async function hydrate(doc, opts) {
    doc = doc || document;
    opts = opts || {};
    const passes = opts.passes !== undefined ? opts.passes : 3;
    const stepMs = opts.stepMs !== undefined ? opts.stepMs : 700;
    const maxMs  = opts.maxMs  !== undefined ? opts.maxMs  : 25000;
    const sc = scroller(doc);
    root.__sc = sc;
    const deadline = Date.now() + maxMs;
    let timedOut = false;

    for (let pass = 0; pass < passes && !timedOut; pass++) {
      for (let y = 0; y < sc.scrollHeight; y += Math.round(sc.clientHeight * 0.6)) {
        if (Date.now() > deadline) { timedOut = true; break; }
        sc.scrollTop = y;
        await sleep(stepMs);
      }
      if (findAboutSection(doc)) break;
    }
    sc.scrollTop = 0;
    return {
      scrollHeight: sc.scrollHeight,
      aboutFound: !!findAboutSection(doc),
      sections: visibleHeadings(doc).length,
      timedOut: timedOut,
    };
  }

  // ---------------------------------------------------------------------------
  // Section expansion
  // ---------------------------------------------------------------------------

  /**
   * Click a "…more" inside THIS section only. Never page-wide: recommendation
   * cards further down carry their own, and clicking one navigates away from the
   * profile and silently discards the extraction.
   *
   * Expansion is cosmetic — the full text is already in innerText, "…more" only
   * removes the truncation label (measured 1789 → 1781 chars on one profile).
   */
  async function expandSection(section) {
    if (!section || !section.querySelectorAll) return false;
    const btn = [].slice.call(section.querySelectorAll('button'))
      .find(b => /^(…\s*more|see more|\.\.\.more)$/i.test(elText(b).trim()));
    if (!btn) return false;
    btn.click();
    await sleep(700);
    return true;
  }

  // ---------------------------------------------------------------------------
  // Field extractors
  // ---------------------------------------------------------------------------

  function extractTopcard(doc, title, out) {
    const container = getTopcardContainer(doc, title) || getPersonCardContainer(doc, nameFromTitle(doc.title || ''));
    if (!container) return null;

    const text = elText(container);
    const L = text.split('\n').map(s => s.trim()).filter(s => s && s !== '·');
    out.name = L[0] || title;

    const di = L.findIndex(s => /^·?\s*\d(?:st|nd|rd|th)\+?$/.test(s));
    if (di >= 0) out.degree = L[di].replace(/[^\da-z+]/gi, '');

    const ci = L.findIndex(s => s === 'Contact info');
    const start = (di >= 0 ? di : 0) + 1;
    if (ci > start) {
      out.headline = L.slice(start, ci - 1).join(' ').trim();
      out.location = L[ci - 1];
    }

    // company/school sit between "Contact info" and whichever of
    // followers/connections comes first — a profile can show either or both.
    const fi = L.findIndex(s => /followers$/.test(s));
    const coni = L.findIndex(s => /connections?$/.test(s));
    const endi = [fi, coni].filter(x => x >= 0).sort((a, b) => a - b)[0];
    if (ci >= 0 && endi > ci) {
      const mid = L.slice(ci + 1, endi);
      out.company = mid[0] || '';
      out.school = mid[1] || '';
    }

    out.followers = ((text.match(/([\d,]+)\s+followers/) || [])[1]) || '';
    // "500+ connections" — keep the trailing "+" so it isn't truncated to "500".
    out.connections = ((text.match(/([\d,]+\+?)\s*connections/) || [])[1]) || '';
    out.mutuals = L.find(s => /mutual connection/i.test(s)) || '';
    return container;
  }

  /**
   * About text. Prefer the longest structural text node (clean: no heading, no
   * "…more" label); fall back to the section's own text when that node only
   * covers a fragment — which happens when LinkedIn splits the paragraph across
   * several spans.
   */
  async function extractAbout(doc) {
    const section = findAboutSection(doc);
    if (!section) return '';
    await expandSection(section);
    const candidate = longestTextIn(section);
    const whole = cleanSectionText(elText(section).replace(/^About\s*\n+/, ''), '');
    if (candidate && candidate.length >= whole.length * 0.5) return candidate.trim();
    return whole;
  }

  function extractPhotoUrl(doc) {
    const img = doc.querySelector(
      '.pv-top-card-profile-picture__image, img.presence-entity__image, .profile-photo-edit__preview img, img[class*="profile-photo"]'
    );
    // Always strip the query string: javascript_tool replaces a return value
    // containing one wholesale with "[BLOCKED: Cookie/query string data]".
    return ((img && img.src) || '').split('?')[0];
  }

  function extractConnectionCount(doc) {
    for (const el of doc.querySelectorAll('a[href*="connections"], span')) {
      const m = (el.textContent || '').match(/(\d[\d,]+)\+?\s*connections?/i);
      if (m) return parseInt(m[1].replace(/,/g, ''), 10);
    }
    return null;
  }

  function sectionByName(doc, heading, id) {
    return findSectionByHeading(doc, heading) || findSectionById(doc, id) || sectionFromHeadingWalkUp(doc, heading);
  }

  /**
   * The lines of one entry, most-prominent first.
   *
   * The upstream parser read `span[aria-hidden="true"]` inside each `li`, which
   * is how the old profile markup carried entry text. On the current layout that
   * yields NOTHING — measured live: a profile whose Experience and Education
   * sections were fully captured by the `other_info` text scan still produced
   * `current_position: null` and `education: []`, because the aria-hidden spans
   * aren't there any more. So try the spans first (older markup, cleanest), then
   * fall back to the entry's own rendered lines.
   */
  function entryLines(item) {
    const spans = [].slice.call(item.querySelectorAll('span[aria-hidden="true"]'))
      .map(s => (s.textContent || '').trim())
      .filter(Boolean);
    if (spans.length) return spans;
    return elText(item).split('\n').map(s => s.trim()).filter(Boolean);
  }

  // A date line — "1996 – 1997", "Sep 2019 - Present · 6 yrs 11 mos". Every real
  // Experience/Education entry has one, which makes it both an entry delimiter
  // and the way to tell a genuine entry from an `li` that holds something else.
  const DATE_LINE = /^[A-Z][a-z]{2}\s+\d{4}\s*[-–]|^\d{4}\s*[-–]|^\d{4}$/;

  /**
   * Entries of a section, as line arrays.
   *
   * `li` is NOT reliably the entry container. Measured live on two profiles: on
   * one, each `li` was a proper entry; on the other the only two `li`s in the
   * Experience section were nested media/sub-role items, so an li-only parser
   * returned title "Sr Software Engineer" with the company field filled by a
   * date range, while the real current role ("Founding Member" at "REGENiTECH
   * LLC · Contract") sat in the section's own text.
   *
   * So: use `li`s only when they actually look like entries (they contain a date
   * line), and otherwise split the section's rendered lines on date lines.
   */
  // Lines that are never an entry's title or organisation. The leading-bullet
  // case matters: an "Activities and societies:" blurb continues over several
  // "- …" lines, and without this they became their own education entries
  // ("- Member of several sports and leisure societies" as a school name).
  const NOISE_LINE = /^(…\s*more|see more|show credential|show all|activities and societies|grade:|skills?:|[-–—•*]\s)/i;

  function sectionEntryLines(sec, heading) {
    if (!sec) return [];

    // Old markup first, when present: `li`s carrying aria-hidden spans are an
    // unambiguous entry marker, and that layout has no date lines to split on.
    const spanItems = [].slice.call(sec.querySelectorAll('li'))
      .filter(li => li.querySelector('span[aria-hidden="true"]'))
      .map(entryLines)
      .filter(l => l.length);
    if (spanItems.length) return spanItems;

    // Otherwise rendered line order. It mirrors what a human sees, so entry 0 really
    // is the current role — whereas `li` order does not: measured live, a nested
    // media/sub-role `li` carrying its own date range sorted ahead of the actual
    // first entry and produced `{title: "Sr Software Engineer", company: ""}` for
    // someone whose current role is Founding Member at REGENiTECH LLC.
    const lines = elText(sec).split('\n').map(s => s.trim())
      .filter(l => l && l !== heading && !NOISE_LINE.test(l));
    const entries = [];
    let cur = [];
    for (const l of lines) {
      if (DATE_LINE.test(l)) {
        if (cur.length) entries.push(cur);
        cur = [];
      } else {
        cur.push(l);
      }
    }
    if (cur.length) entries.push(cur);
    if (entries.length) return entries;

    // Fallback for markup with no date lines at all (the older aria-hidden-span
    // layout the upstream parser was written against).
    return [].slice.call(sec.querySelectorAll('li'))
      .map(entryLines)
      .filter(l => l.length);
  }

  /** "Alluma · Full-time" / "Olive & Mimosa · Self-employed" → "Alluma" */
  function stripEmploymentType(s) {
    return (s || '').split('·')[0].trim();
  }

  function extractCurrentPosition(doc) {
    const sec = sectionByName(doc, 'Experience', 'experience');
    if (!sec) return null;
    const texts = sectionEntryLines(sec, 'Experience')[0];
    if (!texts || !texts.length) return null;
    const company = texts[1] && !DATE_LINE.test(texts[1]) ? stripEmploymentType(texts[1]) : '';
    return { title: texts[0], company: company };
  }

  function extractEducation(doc, limit) {
    const max = limit !== undefined ? limit : 3;
    const sec = sectionByName(doc, 'Education', 'education');
    const education = [];
    if (!sec) return education;
    for (const texts of sectionEntryLines(sec, 'Education')) {
      if (texts.length > 0) {
        // Cap the degree: entry lines include the free-text description that
        // follows an entry, and one live profile produced a 2,000-character
        // "degree" containing an entire Ph.D. dissertation abstract. A real
        // degree line is short; anything long is the description below it.
        const cand = texts[1] && !DATE_LINE.test(texts[1]) ? texts[1] : '';
        const degree = cand.length <= 120 ? cand : '';
        education.push({ school: texts[0], degree: degree });
        if (education.length >= max) break;
      }
    }
    return education;
  }

  const JUNK_HEADING = /notification|Ad Option|Don.t want|Explore Prem|People you|You might/i;

  function visibleHeadings(doc) {
    return [].slice.call(doc.querySelectorAll('h2'))
      .map(h => elText(h).trim().split('\n')[0])
      .filter(t => t && !JUNK_HEADING.test(t));
  }

  /**
   * Opportunistic scan of whatever else rendered — Featured, Services,
   * Recommendations, Highlights, Licenses & certifications. Different profiles
   * render a different subset, so there is no fixed list to hardcode and no
   * fixed shape to parse into; the output is one markdown heading per section.
   */
  async function extractOtherSections(doc, handledHeadings) {
    const handled = new Set(handledHeadings);
    const seen = new Set();
    const outSections = [];
    for (const h of [].slice.call(doc.querySelectorAll('h2'))) {
      const heading = elText(h).trim().split('\n')[0];
      if (!heading || JUNK_HEADING.test(heading)) continue;
      if (handled.has(heading) || seen.has(heading)) continue;
      seen.add(heading);

      let sec = h;
      for (let i = 0; i < 6 && sec.parentElement; i++) {
        sec = sec.parentElement;
        if (elText(sec).trim().length > heading.length + 20) break;
      }

      await expandSection(sec);
      const content = cleanSectionText(elText(sec), heading);
      // Bonus field, not the primary payload — cap it so a long Recommendations
      // list can't dominate the output.
      if (content) outSections.push({ heading: heading, content: content.slice(0, 1500) });
    }
    return outSections.map(s => '## ' + s.heading + '\n' + s.content).join('\n\n');
  }

  // ---------------------------------------------------------------------------
  // Main entry points
  // ---------------------------------------------------------------------------

  function emptyProfile() {
    return {
      name: '', degree: '', headline: '', location: '', company: '', school: '',
      followers: '', connections: '', mutuals: '', about: '', other_info: '',
      photo_url: '', connection_count: null, current_position: null, education: [],
      profile_url: '', slug: '', description: '',
      throttled: false, sections: [], body_sections: 0, scroll_height: 0,
    };
  }

  /**
   * Extract everything from an already-hydrated profile page.
   * Async because section expansion clicks "…more" and waits for the re-render.
   */
  async function extractProfile(doc) {
    doc = doc || document;
    const out = emptyProfile();

    const title = nameFromTitle(doc.title || '');
    out.name = title;

    const rawUrl = (doc.defaultView && doc.defaultView.location && doc.defaultView.location.href) || '';
    out.slug = extractPersonSlug(rawUrl) || '';
    out.profile_url = out.slug ? 'https://www.linkedin.com/in/' + out.slug + '/' : '';

    extractTopcard(doc, title, out);
    if (!out.headline) out.headline = firstText(doc, '.text-body-medium.break-words', '.text-body-medium');

    out.about = await extractAbout(doc);
    out.photo_url = extractPhotoUrl(doc);
    out.connection_count = extractConnectionCount(doc);
    out.current_position = extractCurrentPosition(doc);
    out.education = extractEducation(doc);
    out.description = buildDescription(out.headline, out.about);

    out.sections = visibleHeadings(doc);
    out.other_info = await extractOtherSections(doc, ['About', 'Activity', out.name, title]);

    // Throttle detection. A throttled page returns HTTP 200 with the right name
    // and headline but silently omits the body of the profile. Measured on one
    // profile in both states: healthy was scrollHeight ~3170-3200 with 5
    // sections, throttled was 1746 with only [name, Activity].
    //
    // Two signals, either of which is sufficient when the page has ALSO
    // collapsed structurally — a lone signal is not evidence, since a real
    // profile can have no About (common) or hide its counts (occasional):
    //
    //  a) counts missing too. The original rule.
    //  b) NO body sections at all. Added after a live run where (a) missed a
    //     plainly throttled page: two different profiles, minutes apart, both
    //     rendered a complete topcard *including* "500+ connections" and a
    //     follower count, and both had zero About / Experience / Education with
    //     scrollHeight pinned at 1270 and 1637 across reloads and scroll passes.
    //     Rule (a) scored both as healthy because the counts were present, so a
    //     caller would have recorded "no About, no experience, no education" as
    //     fact. A profile that shows a headline and 500+ connections but renders
    //     no body section whatsoever is a reduced render, not a sparse profile.
    const sc = root.__sc || scroller(doc);
    out.scroll_height = sc ? sc.scrollHeight : 0;
    const collapsedStructure = out.scroll_height < 2200 || out.sections.length <= 2;
    const missingCounts = !out.about && !out.followers && !out.connections;
    const bodySections = out.sections.filter(
      s => s !== out.name && s !== title && s !== 'Activity'
    ).length;
    const noBody = !out.about && !out.current_position && out.education.length === 0 && bodySections === 0;
    out.body_sections = bodySections;
    out.throttled = collapsedStructure && (missingCounts || noBody);

    root.__profile = out;
    return out;
  }

  /**
   * A first read of a perfectly healthy profile can look exactly like
   * throttling — confirmed live: scrollHeight 1270 with only [name, Activity],
   * then 4920 with 10 sections moments later, no re-navigation, purely because
   * hydration hadn't finished. Re-reading the DOM costs nothing over the
   * network, so always retry before believing `throttled`.
   */
  async function extractProfileWithRetry(doc, backoffs) {
    doc = doc || document;
    const waits = backoffs || [1500, 3000, 10000];
    let result = await extractProfile(doc);
    let attempt = 0;
    while (result.throttled && attempt < waits.length) {
      await sleep(waits[attempt]);
      const sc = root.__sc || scroller(doc);
      sc.scrollTop = Math.round(sc.scrollHeight * 0.3);
      await sleep(400);
      sc.scrollTop = 0;
      await sleep(400);
      result = await extractProfile(doc);
      attempt++;
    }
    result.attempts = attempt + 1;
    root.__profile = result;
    return result;
  }

  /** Short receipt safe to return through javascript_tool's 1000-char cap. */
  function receipt(p) {
    return {
      name: p.name, degree: p.degree, location: p.location, company: p.company,
      followers: p.followers, connections: p.connections,
      throttled: p.throttled, attempts: p.attempts || 1,
      sections: p.sections.length, bodySections: p.body_sections, scrollHeight: p.scroll_height,
      headlineChars: p.headline.length, aboutChars: p.about.length,
      otherInfoChars: p.other_info.length, education: p.education.length,
    };
  }

  const FIELD_ORDER = [
    ['NAME', 'name'], ['DEGREE', 'degree'], ['HEADLINE', 'headline'],
    ['LOCATION', 'location'], ['COMPANY', 'company'], ['SCHOOL', 'school'],
    ['FOLLOWERS', 'followers'], ['CONNECTIONS', 'connections'], ['MUTUALS', 'mutuals'],
    ['PROFILE_URL', 'profile_url'], ['PHOTO_URL', 'photo_url'],
    ['CURRENT_POSITION', 'current_position'], ['EDUCATION', 'education'],
    ['ABOUT', 'about'], ['OTHER_INFO', 'other_info'],
  ];

  function serialiseProfile(p) {
    let doc = '';
    for (const pair of FIELD_ORDER) {
      let v = p[pair[1]];
      if (v && typeof v === 'object') {
        v = Array.isArray(v)
          ? v.map(e => e.school ? (e.school + (e.degree ? ' — ' + e.degree : '')) : JSON.stringify(e)).join('\n')
          : (v.title || '') + (v.company ? ' @ ' + v.company : '');
      }
      if (v) doc += '<<<' + pair[0] + '>>>\n' + v + '\n';
    }
    return doc + '<<<END>>>';
  }

  /**
   * Write the payload into the DOM so `get_page_text` can read it back in one
   * call — `javascript_tool` silently truncates its return at exactly 1000
   * characters, and About plus other_info routinely exceed that.
   *
   * Destroys the rendered page, so call it last. Safe: the data is already on
   * `window.__profile` and the page can be reloaded. textContent, never
   * innerHTML — scraped profile text is untrusted input and must not be parsed
   * as markup. get_page_text prefers <article>, so a single <article> wins over
   * the site's own content.
   */
  function writePayloadToDom(doc, p) {
    doc = doc || document;
    const payload = serialiseProfile(p || root.__profile);
    const art = doc.createElement('article');
    art.textContent = payload;
    doc.body.innerHTML = '';
    doc.body.appendChild(art);
    return payload.length;
  }

  const api = {
    // url
    classifyLinkedInSurface, isLinkedInUrl, normaliseLinkedInUrl, extractPersonSlug,
    // title
    nameFromTitle,
    // dom
    firstText, findSectionById, findSectionByHeading, sectionFromHeadingWalkUp,
    findAboutSection, longestTextIn, extractAboutText, buildDescription,
    getPersonCardContainer, getTopcardContainer, nameMatches, cleanSectionText,
    // readiness + hydration
    READINESS_SELECTORS, waitForContent, hydrate, scroller,
    // fields
    extractTopcard, extractAbout, extractPhotoUrl, extractConnectionCount,
    extractCurrentPosition, extractEducation, extractOtherSections, visibleHeadings,
    // entry points
    extractProfile, extractProfileWithRetry, receipt, serialiseProfile, writePayloadToDom,
  };

  root.LinkedInProfile = api;
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
})(typeof window !== 'undefined' ? window : globalThis);
