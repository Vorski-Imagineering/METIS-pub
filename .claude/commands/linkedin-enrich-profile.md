---
description: Visit one LinkedIn profile and extract topcard fields, full About text, any other visible sections (Featured, Services, Recommendations, etc.), and optionally the most recent post
allowed-tools: Read, mcp__claude-in-chrome__tabs_context_mcp, mcp__claude-in-chrome__tabs_create_mcp, mcp__claude-in-chrome__navigate, mcp__claude-in-chrome__javascript_tool, mcp__claude-in-chrome__get_page_text
---

Visit a single LinkedIn profile and extract its topcard, full About text, whatever other
sections the profile happens to render (Featured, Services, Recommendations, Highlights,
etc.), and — if requested — its most recent post.

This is a single-profile primitive. It is the building block for any future batch enrichment
over a `/linkedin-search-capture` file; it does not loop by itself.

**Arguments:** `$ARGUMENTS`

```
<profile-url> [--posts]
```

- `profile-url` — required, e.g. `https://www.linkedin.com/in/priyathachadi/`
- `--posts` — optional. Adds a second page load (`/recent-activity/all/`) to capture the most
  recent post's text and age. Omit for topcard + About only.

If `profile-url` is missing, stop and tell the user:

```
Usage: /linkedin-enrich-profile <profile-url> [--posts]
Example: /linkedin-enrich-profile https://www.linkedin.com/in/priyathachadi/
Example: /linkedin-enrich-profile https://www.linkedin.com/in/priyathachadi/ --posts
```

> **Debug mode is ON.** If any step fails or returns an unexpected result, stop immediately
> and report the exact error to the user. Do NOT try fallbacks, alternative approaches, or
> workarounds.

---

## Output

```
{
  name, degree, headline, location,
  company, school,             // from the topcard's featured links, may be blank
  followers, connections,      // may be blank — some profiles hide these
  mutuals,
  about,                       // full text, may be empty — some profiles have none
  other_info,                  // opportunistic: whatever other sections rendered — see below
  post_text, post_age,         // only present if --posts was given
  throttled: false             // true means the fields above are NOT to be trusted
}
```

`other_info` is a single string, not a structured object — different profiles render a
different subset of sections (Featured, Services, Recommendations, Highlights, Licenses &
certifications, …), so there's no fixed shape to parse into. It's formatted as one heading
per section found, followed by that section's text, separated by blank lines:

```
## Featured
<content>

## Services
<content>
```

Empty string if the profile renders no sections beyond the topcard, About and Activity — this
is common and not a sign of a problem. Note that **Highlights**, when present, describes
things relative to the *viewing* account (shared school, shared employer, mutual skills) —
it is not a fixed property of the target person, so treat it differently from the rest if you
use it for anything beyond a human-readable summary.

If `throttled` is `true`, every other field should be treated as unreliable and **not**
recorded as if it were real data — see step 4.

---

## Steps

### 1. Get browser context

Call `mcp__claude-in-chrome__tabs_context_mcp`. Reuse an existing LinkedIn tab if the user
asked you to, otherwise `mcp__claude-in-chrome__tabs_create_mcp`. The user must already have
an active LinkedIn session — never attempt to log in or enter credentials.

### 2. Navigate and hydrate

Navigate to `profile-url`. Then hydrate the lazy-loaded sections:

```javascript
const sleep = ms => new Promise(r => setTimeout(r, ms));
await sleep(4000);   // initial render

// CRITICAL: window.scrollTo is a NO-OP on this page. The real scroll container
// is MAIN#workspace. Scrolling `window` silently does nothing, which reads as
// "the page has no About section" when it's actually just never rendered.
// Store on window — a plain `const` here does not survive into the next
// javascript_tool call, even though it's the same page.
window.__sc = document.getElementById('workspace') || document.scrollingElement;
const sc = window.__sc;

// Profile sections are virtualised — they unmount again once scrolled past — so
// hydrate by walking down in passes, checking for About after each pass, rather
// than jumping straight to the bottom.
for (let pass = 0; pass < 3; pass++) {
  for (let y = 0; y < sc.scrollHeight; y += Math.round(sc.clientHeight * 0.6)) {
    sc.scrollTop = y;
    await sleep(800);
  }
  if (Array.from(document.querySelectorAll('h2')).some(h => h.innerText.trim() === 'About')) break;
}
```

### 3. Extract topcard, About, and any other sections present

```javascript
window.__extract = async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const title = (document.title || '').replace(/\s*\|\s*LinkedIn.*$/, '')
                                       .replace(/^\(\d+\)\s*/, '').trim();
  const out = { name: title, degree: '', headline: '', location: '', company: '', school: '',
                followers: '', connections: '', mutuals: '', about: '', throttled: false };

  const nameH = Array.from(document.querySelectorAll('h2'))
    .find(h => h.innerText.trim().startsWith(title.slice(0, 12)));
  if (nameH) {
    // Walk up to the card that actually contains "Contact info" — a fixed ancestor
    // depth is unreliable across profile layouts. Loop condition checks
    // `c.parentElement` BEFORE reassigning: if the chain runs out before the
    // length threshold is met, `c` stays at the last real element instead of
    // becoming null and crashing the next iteration's `c.parentElement` read.
    //
    // CRITICAL: breaking at innerText.length > 150 stops ONE LEVEL TOO EARLY.
    // Confirmed live: the container holding name/headline/location/"Contact info"
    // plateaus around 150-230 chars, but the connections/followers count and the
    // mutual-connections line live in the NEXT ancestor up (measured: 226 chars
    // at the old break point vs 311 chars one level up, where "500+ connections"
    // and "Alexander, Nicolás and 407 other mutual connections" actually appear).
    // A profile with a real "500+ connections" badge visible on-screen was
    // extracted with connections/mutuals both blank because of this — it looked
    // exactly like a throttled/empty response but wasn't. Require the container
    // to include BOTH "Contact info" and a connections/followers count before
    // stopping; a plain length cap (600) guards against walking too far up into
    // unrelated page chrome.
    let c = nameH;
    for (let i = 0; i < 10 && c.parentElement; i++) {
      c = c.parentElement;
      const t = c.innerText;
      if (t.includes('Contact info') && /[\d,]+\+?\s*(connections|followers)/.test(t)) break;
      if (t.length > 600) break;
    }
    const L = c.innerText.split('\n').map(s => s.trim()).filter(s => s && s !== '·');
    out.name = L[0] || title;

    const di = L.findIndex(s => /^·?\s*\d(?:st|nd|rd|th)\+?$/.test(s));
    if (di >= 0) out.degree = L[di].replace(/[^\da-z+]/gi, '');

    const ci = L.findIndex(s => s === 'Contact info');
    const start = (di >= 0 ? di : 0) + 1;
    if (ci > start) { out.headline = L.slice(start, ci - 1).join(' ').trim(); out.location = L[ci - 1]; }

    // End boundary for company/school is whichever of followers/connections comes
    // first — a profile can show either or both, in either order.
    const fi = L.findIndex(s => /followers$/.test(s));
    const coni = L.findIndex(s => /connections?$/.test(s));
    const endi = [fi, coni].filter(x => x >= 0).sort((a, b) => a - b)[0];
    if (ci >= 0 && endi > ci) { const mid = L.slice(ci + 1, endi); out.company = mid[0] || ''; out.school = mid[1] || ''; }

    out.followers = ((c.innerText.match(/([\d,]+)\s+followers/) || [])[1]) || '';
    // Connections shows as "500+ connections" (no space before the count in some
    // renders) — capture the trailing "+" so "500+" isn't truncated to "500".
    out.connections = ((c.innerText.match(/([\d,]+\+?)\s*connections/) || [])[1]) || '';
    out.mutuals = L.find(s => /mutual connection/i.test(s)) || '';
  }

  const ah = Array.from(document.querySelectorAll('h2')).find(h => h.innerText.trim() === 'About');
  if (ah) {
    let sec = ah;
    // Same null-guard as the topcard walk-up above: check `parentElement` before
    // reassigning, so a short chain leaves `sec` at the last real element instead
    // of going null and crashing the next iteration.
    for (let i = 0; i < 6 && sec.parentElement; i++) {
      sec = sec.parentElement;
      if (sec.innerText.trim().length > 200) break;
    }
    // The full text is already in innerText — "…more" only strips the truncation
    // label, it does not reveal hidden content. Still click it: scoped to THIS
    // section only, never page-wide (see step 3 note below).
    const btn = Array.from(sec.querySelectorAll('button'))
      .find(b => /^(…\s*more|see more)$/i.test((b.innerText || '').trim()));
    if (btn) { btn.click(); await sleep(900); }
    out.about = sec.innerText.trim().replace(/^About\s*\n+/, '').replace(/\n*…\s*more$/i, '').trim();
  }

  const h2Elements = Array.from(document.querySelectorAll('h2'));
  const JUNK_HEADING = /notification|Ad Option|Don.t want|Explore Prem|People you|You might/i;
  const sections = h2Elements
    .map(h => (h.innerText || '').trim().split('\n')[0])
    .filter(t => t && !JUNK_HEADING.test(t));

  // Opportunistic "other sections" scan. Featured, Services, Recommendations,
  // Highlights, Licenses & certifications — different profiles render a different
  // subset of these, and there is no fixed list to hardcode, so grab whatever h2
  // headings are actually present instead. Skip what's already parsed above
  // (topcard, About) and skip Activity (posts have their own handling, step 5).
  const HANDLED_HEADINGS = new Set(['About', 'Activity', out.name]);
  const seenHeadings = new Set();
  const otherSections = [];
  for (const h of h2Elements) {
    const heading = (h.innerText || '').trim().split('\n')[0];
    if (!heading || JUNK_HEADING.test(heading)) continue;
    if (HANDLED_HEADINGS.has(heading) || seenHeadings.has(heading)) continue;
    seenHeadings.add(heading);

    let sec = h;
    // This exact bug was caught by a mocked-DOM test before ever touching a real
    // page: a short section (e.g. heading 8 chars + two brief lines) can land
    // exactly at the length threshold, and if the ancestor chain also runs out,
    // the old form of this loop (`sec = sec.parentElement` unconditionally, then
    // check) sets `sec` to null and crashes on the next iteration's read. Checking
    // `sec.parentElement` in the loop condition instead prevents `sec` ever
    // becoming null.
    for (let i = 0; i < 6 && sec.parentElement; i++) {
      sec = sec.parentElement;
      if (sec.innerText.trim().length > heading.length + 20) break;
    }

    // Scoped expansion only — never page-wide. A page-wide "…more" click can hit
    // one inside an unrelated card and navigate away (see the note after this block).
    const moreBtn = Array.from(sec.querySelectorAll('button'))
      .find(b => /^(…\s*more|see more)$/i.test((b.innerText || '').trim()));
    if (moreBtn) { moreBtn.click(); await sleep(700); }

    const escapedHeading = heading.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const content = sec.innerText.trim()
      .replace(new RegExp('^' + escapedHeading + '\\s*\\n+'), '')
      .replace(/\n*…\s*more$/i, '').trim();
    // Cap per-section length — some sections (e.g. a long Recommendations list)
    // can run very long; this is a bonus field, not the primary payload.
    if (content) otherSections.push({ heading, content: content.slice(0, 1500) });
  }
  out.other_info = otherSections.map(s => `## ${s.heading}\n${s.content}`).join('\n\n');

  // Throttle detection. A throttled page returns HTTP 200 with the right name and
  // headline but silently omits About AND the follower/connection counts. Missing
  // fields ALONE is not enough evidence — a genuine profile can have no About
  // (common) or hide its counts (occasional). What confirms throttling is a
  // SECOND, independent signal: the page also collapses structurally. Confirmed
  // twice live, on the same profile, in both a known-good and a known-throttled
  // state: healthy scrollHeight was ~3170-3200 with sections
  // [name, Highlights, About, Featured, Activity]; throttled was 1746 both times,
  // with only [name, Activity]. Requiring both signals together is what lets this
  // tell "rate limited" apart from "this person just has a sparse profile".
  const sc = window.__sc || document.getElementById('workspace') || document.scrollingElement;
  const collapsedStructure = sc.scrollHeight < 2200 || sections.length <= 2;
  const missingFields = !out.about && !out.followers && !out.connections;
  out.throttled = missingFields && collapsedStructure;

  // Store, do NOT return, the full object. javascript_tool truncates its return
  // value at EXACTLY 1000 characters, silently — and `about` alone can approach
  // that, with `other_info` running to several thousand. Returning `out` directly
  // would quietly drop most of the payload on precisely the rich profiles worth
  // enriching. Return a short receipt instead; read the long fields back in
  // slices below.
  window.__profile = out;
  return JSON.stringify({ name: out.name, degree: out.degree, location: out.location,
                          throttled: out.throttled, headlineChars: out.headline.length,
                          aboutChars: out.about.length, otherInfoChars: out.other_info.length });
};
await window.__extract();
```

### 3b. Read the full payload back via `get_page_text` — not via `javascript_tool`

`javascript_tool` can only hand back 1000 characters, but **`get_page_text` has no such cap**
(measured intact at 11,211 characters). So instead of slicing the payload into a dozen
`javascript_tool` round trips, write it into the DOM once and read it back in a single
`get_page_text` call — a constant 2 calls regardless of payload size.

Do this **last**, after the receipt above confirms extraction succeeded, because it destroys
the rendered page. That is safe: everything is already captured in `window.__profile`, and
the page can be reloaded if needed. Never do it before extraction is complete.

```javascript
// Serialise the captured profile into the DOM as plain text.
// get_page_text prefers <article>, so replacing the body with a single <article>
// makes it pick this payload rather than the site's own content.
const p = window.__profile;
const field = (label, v) => v ? '<<<' + label + '>>>\n' + v + '\n' : '';
const doc =
  field('NAME', p.name) + field('DEGREE', p.degree) + field('HEADLINE', p.headline) +
  field('LOCATION', p.location) + field('COMPANY', p.company) + field('SCHOOL', p.school) +
  field('FOLLOWERS', p.followers) + field('CONNECTIONS', p.connections) +
  field('MUTUALS', p.mutuals) + field('ABOUT', p.about) + field('OTHER_INFO', p.other_info) +
  '<<<END>>>';
const art = document.createElement('article');
art.textContent = doc;                    // textContent, not innerHTML — profile text is
document.body.innerHTML = '';             // untrusted input and must never be parsed as HTML
document.body.appendChild(art);
'payload written: ' + doc.length + ' chars';
```

Then one call to `mcp__claude-in-chrome__get_page_text` returns the whole thing. Parse on the
`<<<LABEL>>>` delimiters.

**Verify `<<<END>>>` is present in what comes back.** It is the last thing written, so if it's
missing the payload was truncated after all and the data is incomplete — treat that as a
failure, not as a profile with short fields.

> **Never click "…more" / "see more" page-wide.** The page also renders "…more" inside
> recommendation cards further down (e.g. "People also viewed"). Clicking one of those
> navigates away from the profile into a feed post — this happened during development and
> silently discarded the whole extraction. The code above only ever queries buttons inside
> the About section's own container.

### 3b. Retry before trusting a `throttled: true` result

**A single extraction attempt right after hydration can look identical to real
throttling — but isn't.** Confirmed live: the very first read of a normal, fully
healthy profile (500+ connections, full Experience/Education/Publications) came
back with `scrollHeight` 1270 and only `[name, Activity]` rendered — the exact
throttle signature — simply because the page hadn't finished rendering yet when
step 3 ran. Reloading the same extraction moments later, with no re-navigation
and no extra wait beyond a couple of re-hydration scrolls, produced `scrollHeight`
4920 and 10 real sections. Nothing about the network changed; the DOM just needed
more time.

Re-reading the already-loaded DOM costs nothing over the network — it's a pure
client-side re-parse — so retry a few times with backoff before ever reporting
throttling:

```javascript
window.__extractWithRetry = async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const backoffs = [1500, 3000, 10000];  // slow browser/network can need real time
  let result = await window.__extract();
  let attempt = 0;
  while (result.throttled && attempt < backoffs.length) {
    await sleep(backoffs[attempt]);
    // Nudge the virtualised sections to re-render, same idea as step 2's hydration.
    const sc = window.__sc || document.getElementById('workspace') || document.scrollingElement;
    sc.scrollTop = Math.round(sc.scrollHeight * 0.3);
    await sleep(400);
    sc.scrollTop = 0;
    await sleep(400);
    result = await window.__extract();
    attempt++;
  }
  return result;
};
await window.__extractWithRetry();
```

Only a `throttled: true` that survives all three retries (still collapsed after
~14.5s of backoff and re-hydration attempts) is trustworthy evidence of an actual
LinkedIn-side rate limit. Report retry count if it took more than one attempt —
a profile that needed retries but came back healthy is a signal the browser/network
was just slow that moment, not that anything is wrong.

### 4. Check for throttling

If `out.throttled` is `true`:

- **Stop.** Do not report the extracted fields as real data — they are not to be trusted.
- Tell the user plainly: LinkedIn appears to be serving a reduced page (a rate-limit signal),
  not that this person has no About or hides their connection count.
- Recommend waiting at least 15–30 minutes before visiting another profile.

### 5. Recent post (only if `--posts` was given)

Navigate to `<profile-url>/recent-activity/all/` (append `recent-activity/all/` after the
trailing slash). Wait ~4s, then:

```javascript
const t = document.body.innerText;
const i = t.indexOf('Feed post number 1');
const chunk = i >= 0 ? t.slice(i, i + 900) : '';
// The post body sits after the headline/age line; age looks like "3mo • Edited •"
const ageMatch = chunk.match(/(\d+\s*(?:s|m|h|d|w|mo|yr)s?)\s*•/);
JSON.stringify({
  post_age: ageMatch ? ageMatch[1] : '',
  post_text: chunk ? chunk.split('\n').slice(4).join('\n').split('…more')[0].trim().slice(0, 600) : ''
});
```

If no posts are found (`chunk` is empty), leave `post_text` and `post_age` blank — this is
normal for a profile with no public activity, not an error.

### 6. Report

```
{name} — {degree}, {location}
{headline}
Company: {company}   School: {school}
Followers: {followers}   Connections: {connections}
About: {about, or "(none)"}
{if other_info non-empty} Other info:
{other_info}
{if --posts} Most recent post ({post_age}): {post_text}
```

If throttled, report only: `Throttled — stopping. Try again in 15-30 minutes. ({name}, {degree}, {location} were still readable; everything else was not.)`

---

## Pacing

A single call needs no delay of its own. **If this command is being run in a loop** — the
expected use once a batch wrapper exists — pace every visit per the **Pacing** section of
`.claude/skills/linkedin-automation/SKILL.md` (profile visits: ~45s mean). Do not loop this
command manually without that delay.

Remember also: **visiting a profile is visible to that person.** Before enriching several
profiles in a row, say how many will be visited and that each visit is visible to them.

## Known limitations and caveats

- **`window.scrollTo` is a no-op here.** Confirmed live: `window.scrollY` stayed `0` after
  `scrollTo(0, 1500)`. The scroll container is `MAIN#workspace`. Every earlier failure to find
  About traced back to this.
- **Profile sections are virtualised.** They render only while in view and unmount again once
  scrolled past. A single scroll-to-bottom then read finds nothing; hydrate in passes.
- **About is not hidden — it's already in `innerText`.** Clicking "…more" only removes the
  literal truncation label (measured: 1789 → 1781 characters on one profile). Don't treat it
  as unlocking new content; do click it anyway, for clean output text.
- **Every field is optional.** Confirmed across real profiles: some have no About, some hide
  follower/connection counts, some have neither company nor school on the topcard. Never
  treat a blank field as a bug.
- **Throttling is silent and looks identical to an empty/private profile** unless you check
  two independent signals together — missing fields alone is not enough evidence, since a
  real profile can legitimately have no About or hidden counts. Confirmed on the same
  profile in both states: healthy was `scrollHeight` ~3170–3200 with 5 sections
  (Highlights/About/Featured/Activity); throttled was `scrollHeight` 1746 with only 2
  sections (name/Activity) — reproduced identically on two separate visits roughly half an
  hour apart, with the account still throttled both times. Structure collapsing alongside
  the missing fields is what distinguishes "rate limited" from "this profile is just sparse
  or private".
- **A "throttled" read can also just mean the page hasn't finished rendering yet** — this is
  NOT the same as real LinkedIn-side throttling and is far more common. Confirmed live on a
  healthy, well-connected profile (500+ connections, full Experience/Education/Publications):
  the very first extraction attempt returned `scrollHeight` 1270 with only `[name, Activity]`
  — the exact throttle signature — purely because hydration hadn't completed. The identical
  extraction moments later (no re-navigation, just a couple more hydration scrolls) returned
  `scrollHeight` 4920 with 10 real sections. Since re-reading the DOM has no network cost,
  **always retry with backoff (1.5s, 3s, 10s) before reporting `throttled: true`** — see step
  3b's `__extractWithRetry`. Treat only a throttled result that survives all retries as a real
  signal.
- **The topcard container walk-up can stop one level too early.** Breaking at a fixed
  `innerText.length > 150` finds the container holding name/headline/location/"Contact info"
  (which plateaus around 150–230 chars) but NOT the connections/followers count or the
  mutual-connections line, which live one ancestor further up (measured: 226 vs 311 chars on
  the same profile). A profile with a plainly visible "500+ connections" badge was extracted
  with `connections` and `mutuals` both blank as a result — indistinguishable from throttling
  at a glance. Walk up until the container includes both `"Contact info"` and a
  connections/followers count match (capped at ~600 chars to avoid drifting into page chrome),
  not a bare length threshold.
- **`/details/about/` does not exist.** Unlike `/details/experience/` and
  `/details/education/`, which are clean dedicated pages, About only ever renders on the main
  profile — hence the scroll-and-hydrate approach here instead of a simple sub-page fetch.
- **`other_info` is opportunistic, not exhaustive.** It captures whatever `h2` sections are
  present after hydration, by heading text — so it naturally varies per profile: some show
  Featured and Services, some show only Recommendations, most show nothing beyond About and
  Activity. Don't expect a fixed set of headings, and don't treat an empty `other_info` as a
  failure.
- **Every `other_info` section gets the same scoped-expansion treatment as About** — only its
  own "…more" button, never a page-wide click — for the same reason: a page-wide click can
  land on an unrelated card and navigate away entirely.
- **Contact info (email, phone, personal website, "Connected on" date) is not covered.**
  Unlike the sections above, it sits behind a modal that has to be explicitly opened and
  closed rather than scrolled into view — deliberately left out of this pass to keep the
  interaction surface small. Worth a separate follow-up if that data turns out to matter.
- **`javascript_tool` truncates its return value at exactly 1000 characters, silently.**
  Measured: 1000 chars arrive intact, 1001 lose the last character to `[TRUNCATED]`, with no
  error raised. The cap is per call (each `browser_batch` item gets its own budget) and is
  specific to `javascript_tool`; `Bash` and `Read` are unaffected. This is why the extractor
  stores its result on `window` and returns only a receipt — `about` plus `other_info`
  routinely exceed the cap on a rich profile, and the overflow would vanish without any sign.
- **`get_page_text` is the way around that cap** — measured returning 11,211 characters
  intact, with no limit found and no `max_chars`-style parameter needed. Writing the payload
  into the DOM and reading it back with `get_page_text` (step 3b) costs a constant 2 calls at
  any size, versus one call per 900 characters when slicing through `javascript_tool`. Prefer
  it for any bulk text. (The sibling `read_page` also takes a `max_chars` defaulting to
  50000, but it returns an accessibility tree rather than clean text.)
- **`javascript_tool` can also block a return value outright**, regardless of length:
  cookies/query strings yield `[BLOCKED: Cookie/query string data]` and long runs of repeated
  characters yield `[BLOCKED: Base64 encoded data]`. The whole return is replaced, not
  trimmed — always `.split('?')[0]` a URL before returning it.
- **`/details/<section>/` likely extends beyond Experience and Education** — probably Skills,
  Certifications, Volunteering, Recommendations, Projects, Publications, Courses, Honors, and
  Languages each have their own clean dedicated page following the same pattern. This is an
  inference from the one confirmed case, not yet verified live for the others; the in-page
  `other_info` scan above is what's actually running today, not the `/details/` pages.
