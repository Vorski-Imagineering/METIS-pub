---
description: Scrape the newest N LinkedIn connections and load them into a METIS Outreach candidate list
allowed-tools: Bash, Read, mcp__claude-in-chrome__tabs_context_mcp, mcp__claude-in-chrome__tabs_create_mcp, mcp__claude-in-chrome__navigate, mcp__claude-in-chrome__javascript_tool, mcp__claude-in-chrome__get_page_text, mcp__claude-in-chrome__computer
---

Scrape the most recently added rows off `/mynetwork/invite-connect/connections/` and load
them into a new METIS Outreach candidate list.

**Arguments:** `$ARGUMENTS`

```
["<name>"] [count]
```

- `name` — free text; quote it. **Optional** — defaults to the caller's own METIS Person name
  (the `person.name` field returned by the `/api/v1/auth/login` response, e.g. `"Victor
  Vorski"`). Never ask the user for this before checking who they are logged in as — you
  always know the managed account from the login call you make anyway.
- `count` — how many newest connections to pull (default `200`).
- **Parsing rule:** a lone purely-numeric argument is always `count`, never `name` — e.g.
  `/linkedin-newest-connections 50` means count=50 with the default name, not a name of "50".
  If two arguments are given, the first (quoted) is `name` and the second (numeric) is `count`.

List name is always `<name> newest connections-<YYYY-MM-DD>` (today's date).

Read `.claude/skills/metis/SKILL.md` and `.claude/skills/linkedin-automation/SKILL.md`
(**Pacing** section) before starting.

---

## Steps

### 0. Resolve `name` and `count`

Run the METIS auth flow (`.claude/commands/metis.md`) first regardless of whether `name` was
given — you need the token either way, and its response's `person.name` is the default `name`.
Use an explicit quoted argument if the user gave one; otherwise use `person.name` unmodified.
`count` defaults to `200` if omitted.

### 1. Get browser context

Call `mcp__claude-in-chrome__tabs_context_mcp`. Reuse an existing LinkedIn tab if the user
points you at one, otherwise create one. The user must already have an active LinkedIn
session — never attempt to log in.

Navigate to `https://www.linkedin.com/mynetwork/invite-connect/connections/`. This page is
sorted **Recently added** by default — verify with a screenshot before scraping; if it isn't,
stop and ask the user to set that sort rather than silently scraping an arbitrary order.

### 2. Scroll-load until `count` unique rows are captured, or until it plateaus

This page is **infinite scroll on the `<main>` element**, not `window`/`document.body` — those
never move (`window.scrollY` stays `0`). It also has **no "Show more" button** and **no
`page=N` query parameter** — do not try either.

**Hard requirements, not just this run's choices:** every retrigger technique here must be
**JS-only, via `javascript_tool`** — never the `computer` tool's native scroll/wheel actions
or screenshots, even for debugging a stuck cycle. And every cycle must be separated by
`linkedin-automation`'s `humanDelay` (the "search results page → next page" class: 12s/5s/90s
mean/min/max) — never a fixed or short sleep, even while iterating on the technique itself.
Both were explicit corrections during live testing on 2026-08-28; treat them as fixed rules
for this skill, not conveniences to skip under time pressure.

**Two different waits are involved — don't conflate them.** The ~2.8s wait inside each snippet
below is a *technical* wait for LinkedIn's async loader to render the new rows; it is not the
pacing wait and must stay short and fixed. The `humanDelay` pacing wait is separate: compute it
in the **agent loop**, outside `javascript_tool` (Python `human_delay(12000, 5000, 90000)` then
`Bash({command: "sleep <seconds>", run_in_background: true})`, exactly as `linkedin-automation`
and `linkedin-search-capture.md`'s page-turn step do), and run it *before* each scroll cycle —
never substitute it with a longer in-page `setTimeout`, which is exactly the "constant interval
inside one JS call" pattern the account was previously throttled for.

**Verified live 2026-08-28 — plateau is real and expected, plan for it.** A plain
`main.scrollTop = main.scrollHeight` + ~2.8s technical wait reliably grows the row count for the
first couple of cycles (25 → 45 → 85 raw anchors were observed), then plateaus — further
identical cycles add nothing. Each of the following also reliably triggers **at most one**
additional batch load, then itself plateaus on repetition, even when the agent-loop `humanDelay`
pacing wait above precedes every attempt:

```javascript
const main = document.querySelector('main');
main.scrollTop = main.scrollHeight;
await new Promise(r => setTimeout(r, 2800));  // technical render wait only — NOT the pacing wait
```

```javascript
// scrollIntoView on the last anchor — try this if plain scrollTop stops growing the count
const anchors = document.querySelectorAll('a[href*="/in/"]');
anchors[anchors.length - 1].scrollIntoView({block: 'end'});
await new Promise(r => setTimeout(r, 2800));  // technical render wait only — NOT the pacing wait
```

```javascript
// synthetic wheel event + scrollTop — try this if scrollIntoView also stops working
const main = document.querySelector('main');
main.dispatchEvent(new WheelEvent('wheel', {deltaY: 800, bubbles: true, cancelable: true}));
main.scrollTop += 800;
await new Promise(r => setTimeout(r, 2800));  // technical render wait only — NOT the pacing wait
```

Rotate through these three (in this order) across cycles rather than repeating one — each can
unstick the loader once even after another has plateaued. Put the agent-loop `humanDelay` wait
before each of these snippets, every cycle. Track the raw `a[href*="/in/"]` count between
cycles.

**Stop condition — do not hammer past a genuine plateau.** Stop scrolling once the number of
unique profile URLs (dedupe by href, `.split('?')[0]`) reaches `count`, OR once **two
consecutive paced cycles** (using different techniques from the rotation above) produce zero
growth in the raw anchor count. **This is not evidence of a real ceiling on the page — LinkedIn
imposes no fixed limit on connections shown here.** In the 2026-08-28 test, exhausting all
three techniques across several paced cycles plateaued at 85 raw anchors (44 unique people),
well short of the default `count` of 200; the most likely explanation is a session-level soft
throttle from this account's own prior heavy testing that day (this account has been throttled
before from sustained rapid activity — see `linkedin-automation`'s detection guidance), not a
per-page cap. A run on a quieter session, or one that takes a full burst break
(`humanDelay(300000, 120000, 600000)`, 2–10 min) before retrying past the plateau, may well
reach much closer to `count`. Don't treat a plateau in one sitting as proof of a hard maximum —
take the burst break once, retry, and only if it plateaus again after that should you stop and
report the shortfall in step 7 rather than continuing indefinitely.

### 3. Extract name + profile URL + connected date

Do this once, after scrolling is done, not per-cycle — it's cheap and avoids re-parsing rows
you already have. Card markup is inconsistent between rows (verified live 2026-08-28); try each
extraction path in order and fall back:

```javascript
const links = [...document.querySelectorAll('a[href*="/in/"]')];
const map = new Map();
links.forEach(a => {
  const href = a.getAttribute('href').split('?')[0];
  if (map.has(href)) return;
  let name = '';
  const img = a.querySelector('img[alt]');
  if (img) name = img.getAttribute('alt').replace(/’s profile picture.*$/i, '').trim();
  if (!name) {
    const span = a.querySelector('span[aria-hidden="true"]');
    name = span ? span.textContent.trim() : '';
  }
  if (!name) {
    const text = a.textContent.trim();
    name = text.split('•')[0].trim();
  }
  if (!name) return;
  map.set(href, name);
});
window.__conn = [...map.entries()].map(([href, name]) => ({name, href}));
window.__conn.length;
```

Cap the result at `count` entries (scrolling may have overshot).

**Connected-on date:** each row's text contains a `"Connected on <date>"` line — extract it
per-row if you need it for the candidate `note` field, but it is not required by the list API
and is easy to skip if it complicates extraction.

### 4. Serialize and read back in one call

Never return the array directly from `javascript_tool` — even a moderate list blows the
1000-character-per-call cap. Use the DOM-serialize pattern:

```javascript
document.body.innerHTML = '';
const art = document.createElement('article');
art.textContent = JSON.stringify(window.__conn) + '\n<<<END ' + window.__conn.length + '>>>';
document.body.appendChild(art);
'written';
```

Then one `mcp__claude-in-chrome__get_page_text` call. Verify the `<<<END n>>>` sentinel's `n`
matches `window.__conn.length` before trusting the payload — a short sentinel means it was cut
and the batch is incomplete.

### 5. Find-or-create the METIS Outreach list

List creation is **not idempotent** — always check first:

```bash
curl -s "$METIS_URL/api/v1/outreach/lists" -H "Authorization: Bearer $METIS_TOKEN"
```

Look for an exact `name` match on `"<name> newest connections-<YYYY-MM-DD>"`. Only create if
none exists:

```bash
curl -s -X POST "$METIS_URL/api/v1/outreach/lists" \
  -H "Authorization: Bearer $METIS_TOKEN" -H "Content-Type: application/json" \
  --data '{"name": "<name> newest connections-<date>", "description": "Newest LinkedIn connections, scraped from /mynetwork/invite-connect/connections/."}'
```

### 6. Bulk-add candidates

The API caps this endpoint at **500 items per call**. This command's default `count` of 200
fits in one call, but if the user requested a larger `count`, chunk the scraped list into
batches of 500 and issue one `candidates:bulk-add` call per chunk (same list, same `LIST_ID`),
summing `created`/`already_present`/`errors` across chunks for the step 7 report:

```bash
curl -s -X POST "$METIS_URL/api/v1/outreach/lists/$LIST_ID/candidates:bulk-add" \
  -H "Authorization: Bearer $METIS_TOKEN" -H "Content-Type: application/json" \
  --data '{"items": [{"name": "...", "linkedin": "https://www.linkedin.com/in/..."}]}'
```

Every item needs a `linkedin` (or `email`) — a name-only row is unmatchable and comes back
`no_contact_channel`. That never happens here since every scraped row has a profile URL.

### 7. Report

```
Scraped {n} newest connections.
List: {list name} (id {list_id})
Candidates: {created} created, {already_present} already present, {errors} errors.
```

If `errors > 0`, list the failing rows and their `error.code`.

---

## Known limitations

- **No location, no mutuals, no keyword snippet on this page** — unlike LinkedIn people-search
  cards (`linkedin-search-capture.md`), the connections list only ever carries name, profile
  URL, and a connected-on date.
- **This loads a candidate list, not the real LinkedIn Network journey.** METIS has no API
  write path to `outreach-linkedin-network` (import-only, CSV via the web UI) — see
  [METIS-pub#308](https://github.com/Vorski-Imagineering/METIS-pub/issues/308). A candidate
  list is the correct, safe target given that constraint; it is not a workaround to fix later.
- **Re-scrolling past people already on a prior list is fine.** Candidate matching is by
  LinkedIn URL, so a re-run with a larger `count` against the same `<name>`/date is safe —
  it creates a fresh list (new date) with its own fresh `already_present` accounting; it does
  not touch or duplicate anyone on an earlier list.
