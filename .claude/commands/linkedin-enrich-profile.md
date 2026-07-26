---
description: Visit one LinkedIn profile and extract topcard fields, full About text, any other visible sections (Featured, Services, Recommendations, etc.), and optionally the most recent post
allowed-tools: Read, mcp__claude-in-chrome__tabs_context_mcp, mcp__claude-in-chrome__tabs_create_mcp, mcp__claude-in-chrome__navigate, mcp__claude-in-chrome__javascript_tool, mcp__claude-in-chrome__get_page_text
---

Visit a single LinkedIn profile and extract its topcard, full About text, experience and
education, whatever other sections the profile happens to render (Featured, Services,
Recommendations, Highlights, etc.), and — if requested — its most recent post.

This is a single-profile primitive. It is the building block for any future batch enrichment
over a `/linkedin-search-capture` file; it does not loop by itself.

All the DOM parsing lives in **`automation/linkedin-automation/scripts/linkedin-profile-extract.js`**
— ported from METIS's Chrome-extension profile parser, which is the reliable implementation.
Do not re-derive extraction logic inline here: inject that file and call it. It has a test
suite (`linkedin-profile-extract.test.js`, run with jsdom) — fix bugs there, with a test, not
by improvising a new selector at the console.

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
  profile_url, slug, photo_url,
  about,                       // full text, may be empty — some profiles have none
  description,                 // headline + About, capped at 1000 chars
  current_position,            // { title, company } | null
  education,                   // [{ school, degree }], up to 3
  connection_count,            // number | null
  other_info,                  // opportunistic: whatever other sections rendered — see below
  post_text, post_age,         // only present if --posts was given
  sections, scroll_height,     // diagnostics behind the throttle check
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
recorded as if it were real data — see step 5.

---

## Steps

### 1. Get browser context

Call `mcp__claude-in-chrome__tabs_context_mcp`. Reuse an existing LinkedIn tab if the user
asked you to, otherwise `mcp__claude-in-chrome__tabs_create_mcp`. The user must already have
an active LinkedIn session — never attempt to log in or enter credentials.

**The tab must be visible.** LinkedIn renders no profile body in a background tab — no About,
no Experience, no Education, absent from the DOM rather than merely hidden — which is
indistinguishable from throttling. Check it before extracting, on every profile:

```javascript
JSON.stringify({ visibility: document.visibilityState, focus: document.hasFocus() })
```

If `visibility` is not `'visible'`, stop and ask the user to bring the tab to the foreground;
don't diagnose anything else until it is. `hasFocus: false` is fine — Chrome may be in the
background, as long as this tab is the active one in its window. For a batch run, say up front
that the tab needs to stay in the foreground throughout.

### 2. Navigate and inject the extractor

Navigate to `profile-url`, then wait ~4s for the initial render.

`Read` `automation/linkedin-automation/scripts/linkedin-profile-extract.js` and pass its
**entire contents verbatim** as one `javascript_tool` call, with a short receipt appended so
the return stays inside the 1000-character cap:

```javascript
// <contents of linkedin-profile-extract.js>
'loaded: ' + Object.keys(window.LinkedInProfile).length + ' helpers';
```

The 1000-char cap applies to the *return value*, not to the code sent in — injecting the
whole file in one call is fine. If the receipt doesn't come back, the script did not evaluate;
stop and report that rather than falling back to ad-hoc extraction.

**This has to be repeated for every profile, and there is no way around it.** The file is
~26 KB, so re-injection is the dominant cost of a batch run, and two obvious caching tricks
both fail — don't spend time rediscovering that:

- **`localStorage` silently doesn't persist** from `javascript_tool` on linkedin.com:
  `setItem` throws nothing and `getItem` returns `null`.
- **`window.name` persists across navigation, but the cached source can't be run.**
  linkedin.com's CSP has no `unsafe-eval`, so `eval(src)` and `new Function(src)` both throw
  `EvalError` — the injected script itself is fine (it arrives via CDP, not via the page), but
  anything it evaluates from a string is subject to the page's CSP.

The practical consequence: re-paste per profile, and keep batches modest.

### 3. Hydrate the lazy-loaded sections

```javascript
JSON.stringify(await window.LinkedInProfile.hydrate(document, { maxMs: 25000 }));
```

`hydrate` scrolls `MAIN#workspace` (**`window.scrollTo` is a no-op on profile pages**) in
passes and stops as soon as About has rendered. Profile sections are virtualised — they
unmount again once scrolled past — which is why it walks down in passes instead of jumping to
the bottom. It returns `{ scrollHeight, aboutFound, sections, timedOut }`.

**`javascript_tool` calls die at 45 s** (`CDP sendCommand "Runtime.evaluate" timed out`), and
the call is killed while the page keeps scrolling. `hydrate` is therefore bounded by a
wall-clock budget, not just a pass count — `scrollHeight` grows as sections load, so the loop
bound is a moving target. If it returns `aboutFound: false`, call it again (page state
persists between calls, so it resumes rather than restarting); give up after ~3 calls and let
the throttle check below decide what that means. Keep any other long-running snippet — sleeps
included — under ~40 s for the same reason.

### 4. Extract

```javascript
const P = window.LinkedInProfile;
JSON.stringify(P.receipt(await P.extractProfileWithRetry(document)));
```

`extractProfileWithRetry` stores the full result on `window.__profile` and retries with
backoff (1.5s, 3s, 10s) while the page still looks throttled — a first read of a healthy
profile can look exactly like throttling simply because hydration hadn't finished, and
re-reading the DOM costs nothing over the network. The receipt reports `attempts`; mention it
if it took more than one.

### 5. Check for throttling

If the receipt's `throttled` is `true` (i.e. it survived all retries):

- **Only after re-checking `document.visibilityState` (step 1) — a background tab fakes every
  signal below.** Then confirm with a free control: load `https://www.linkedin.com/in/me/`. Your own profile
  always renders its own About/Experience for you, and visiting it notifies nobody. If it also
  comes back with only `[name, Activity]` and no `>Experience<` anywhere in
  `document.documentElement.outerHTML`, the account is throttled — stop, and don't waste
  further visits on target profiles. If it renders fully, the problem is that specific profile
  (or the extractor), not the account.
- **Stop.** Do not report the extracted fields as real data — they are not to be trusted.
- Tell the user plainly: LinkedIn appears to be serving a reduced page (a rate-limit signal),
  not that this person has no About or hides their connection count.
- Recommend waiting at least 15–30 minutes before visiting another profile.

### 6. Read the full payload back via `get_page_text` — not via `javascript_tool`

`javascript_tool` can only hand back 1000 characters, but **`get_page_text` has no such cap**
(measured intact at 11,211 characters). So write the payload into the DOM once and read it
back in a single `get_page_text` call — a constant 2 calls regardless of payload size.

Do this **last**, after the receipt confirms extraction succeeded, because it destroys the
rendered page. That is safe: everything is already in `window.__profile`, and the page can be
reloaded. Never do it before extraction is complete.

```javascript
'payload written: ' + window.LinkedInProfile.writePayloadToDom(document) + ' chars';
```

Then one call to `mcp__claude-in-chrome__get_page_text` returns the whole thing. Parse on the
`<<<LABEL>>>` delimiters.

**Verify `<<<END>>>` is present in what comes back.** It is the last thing written, so if it's
missing the payload was truncated after all and the data is incomplete — treat that as a
failure, not as a profile with short fields.

### 7. Recent post (only if `--posts` was given)

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

### 8. Report

```
{name} — {degree}, {location}
{headline}
Company: {company}   School: {school}
Followers: {followers}   Connections: {connections}
Current: {current_position.title} @ {current_position.company}
Education: {education, one per line}
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

These are the reasons the extractor is shaped the way it is. Read them before changing it.

- **Extraction logic belongs in the script, not in this file.** The previous version of this
  command carried ~200 lines of inline JavaScript that kept missing About and other sections;
  it was replaced by the METIS extension's parser, which finds About by `id="about"` anchor,
  `aria-label="About"`, `<h2>`/`<h3>` heading text *and* a heading walk-up, rather than a
  single heading match. Any new fix goes into `linkedin-profile-extract.js` with a test.
- **`window.scrollTo` is a no-op here.** Confirmed live: `window.scrollY` stayed `0` after
  `scrollTo(0, 1500)`. The scroll container is `MAIN#workspace`. Every earlier failure to find
  About traced back to this.
- **Profile sections are virtualised.** They render only while in view and unmount again once
  scrolled past. A single scroll-to-bottom then read finds nothing; `hydrate` walks down in
  passes for this reason.
- **About is not hidden — it's already in `innerText`.** Clicking "…more" only removes the
  literal truncation label (measured: 1789 → 1781 characters on one profile). Don't treat it
  as unlocking new content; the script clicks it anyway, for clean output text.
- **Never click "…more" / "see more" page-wide.** The page also renders "…more" inside
  recommendation cards further down (e.g. "People also viewed"). Clicking one of those
  navigates away from the profile into a feed post — this happened during development and
  silently discarded the whole extraction. `expandSection` only ever queries buttons inside
  the section it was handed.
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
- **A background tab produces the exact throttle signature, and it is the far more likely
  cause.** LinkedIn does not render the profile body when `document.visibilityState` is
  `'hidden'`. Confirmed the expensive way: three profiles *and the operator's own profile*
  all came back at `scrollHeight` 1270–1686 with only `[name, Activity]`, unchanged across
  reloads, scroll passes and ~40 minutes, with `>Experience<` absent from 529 KB of HTML — and
  it was reported to the user as an account-level throttle. It wasn't. Foregrounding the tab
  made the same URL render at 2351 → 5388 with nine body sections, seconds later, same
  account. **Check `document.visibilityState` before every other diagnosis** (step 1), and
  never let the own-profile control below run in a background tab either — it will "confirm"
  a throttle that doesn't exist.
- **A throttled page can still show its follower/connection counts.** Confirmed live on two
  different profiles minutes apart: each rendered a complete topcard — name, degree, headline,
  location, company, "500+ connections", mutual-connections line, follower count — and yet had
  no About, no Experience and no Education, with `scrollHeight` pinned at 1270 and 1637 across
  a fresh reload and several scroll passes. The original detector (missing About **and**
  missing counts) scored both as healthy, which would have written "no About, no experience,
  no education" into a record as if it were fact. So the check is now: collapsed structure
  **and** (counts missing **or** no body section at all). A profile showing a headline and
  500+ connections while rendering zero body sections is a reduced render, not a sparse
  profile. `body_sections` in the receipt is that second signal.
- **Two profiles collapsing in a row means the account is throttled, not that both people have
  empty profiles.** One collapsed profile is ambiguous; a second one immediately after is the
  cheapest way to tell account-level throttling from a per-profile quirk. Stop the run there.
- **A "throttled" read can also just mean the page hasn't finished rendering yet** — this is
  NOT the same as real LinkedIn-side throttling and is far more common. Confirmed live on a
  healthy, well-connected profile (500+ connections, full Experience/Education/Publications):
  the very first extraction attempt returned `scrollHeight` 1270 with only `[name, Activity]`
  — the exact throttle signature — purely because hydration hadn't completed. The identical
  extraction moments later (no re-navigation, just a couple more hydration scrolls) returned
  `scrollHeight` 4920 with 10 real sections. Hence `extractProfileWithRetry`; treat only a
  throttled result that survives all retries as a real signal.
- **The topcard container walk-up can stop one level too early.** Breaking at a fixed
  `innerText.length > 150` finds the container holding name/headline/location/"Contact info"
  (which plateaus around 150–230 chars) but NOT the connections/followers count or the
  mutual-connections line, which live one ancestor further up (measured: 226 vs 311 chars on
  the same profile). A profile with a plainly visible "500+ connections" badge was extracted
  with `connections` and `mutuals` both blank as a result — indistinguishable from throttling
  at a glance. `getTopcardContainer` therefore walks up until the container includes both
  `"Contact info"` and a connections/followers count (capped at ~600 chars to avoid drifting
  into page chrome), not to a bare length threshold.
- **`/details/about/` does not exist.** Unlike `/details/experience/` and
  `/details/education/`, which are clean dedicated pages, About only ever renders on the main
  profile — hence the scroll-and-hydrate approach here instead of a simple sub-page fetch.
- **`other_info` is opportunistic, not exhaustive.** It captures whatever `h2` sections are
  present after hydration, by heading text — so it naturally varies per profile: some show
  Featured and Services, some show only Recommendations, most show nothing beyond About and
  Activity. Don't expect a fixed set of headings, and don't treat an empty `other_info` as a
  failure.
- **`javascript_tool` truncates its return value at exactly 1000 characters, silently.**
  Measured: 1000 chars arrive intact, 1001 lose the last character to `[TRUNCATED]`, with no
  error raised. The cap is per call (each `browser_batch` item gets its own budget) and is
  specific to `javascript_tool`; `Bash` and `Read` are unaffected. This is why the extractor
  stores its result on `window.__profile` and returns only a receipt — `about` plus
  `other_info` routinely exceed the cap on a rich profile, and the overflow would vanish
  without any sign.
- **`get_page_text` is the way around that cap** — measured returning 11,211 characters
  intact, with no limit found and no `max_chars`-style parameter needed. Writing the payload
  into the DOM and reading it back with `get_page_text` (step 6) costs a constant 2 calls at
  any size, versus one call per 900 characters when slicing through `javascript_tool`. Prefer
  it for any bulk text. (The sibling `read_page` also takes a `max_chars` defaulting to
  50000, but it returns an accessibility tree rather than clean text.)
- **`javascript_tool` can also block a return value outright**, regardless of length:
  cookies/query strings yield `[BLOCKED: Cookie/query string data]` and long runs of repeated
  characters yield `[BLOCKED: Base64 encoded data]`. The whole return is replaced, not
  trimmed — which is why `extractPhotoUrl` strips the query string from the image URL.
- **Contact info (email, phone, personal website, "Connected on" date) is not covered.**
  Unlike the sections above, it sits behind a modal that has to be explicitly opened and
  closed rather than scrolled into view — deliberately left out of this pass to keep the
  interaction surface small. Worth a separate follow-up if that data turns out to matter.
- **`/details/<section>/` likely extends beyond Experience and Education** — probably Skills,
  Certifications, Volunteering, Recommendations, Projects, Publications, Courses, Honors, and
  Languages each have their own clean dedicated page following the same pattern. This is an
  inference from the one confirmed case, not yet verified live for the others; the in-page
  `other_info` scan is what's actually running today, not the `/details/` pages.
