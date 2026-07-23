---
description: Capture LinkedIn people-search results (keyword / location / degree, multi-page) into a normalized JSON file
allowed-tools: Bash, Read, Write, Edit, mcp__claude-in-chrome__tabs_context_mcp, mcp__claude-in-chrome__tabs_create_mcp, mcp__claude-in-chrome__navigate, mcp__claude-in-chrome__javascript_tool, mcp__claude-in-chrome__browser_batch
---

Run a LinkedIn people search and capture every result into a normalized JSON file.

Capture only. This command never writes to METIS, never sends a connection request, and
never messages anyone. Importing the resulting file is a separate command's job.

**Arguments:** `$ARGUMENTS`

```
"<keywords>" [--location "<name>"] [--degree 1st|2nd|3rd+] [--pages N] [--out <path>]
```

- `keywords` — free text; quote it. May be omitted **only** if `--location` is given.
- `--location` — place name, e.g. `"Lisbon, Portugal"`. Repeatable; multiple locations are OR'd.
- `--degree` — `1st`, `2nd`, or `3rd+`. Repeatable. Omit for all degrees.
- `--pages` — integer 1–10 (default `1`). LinkedIn caps every search at 10 pages.
- `--out` — output path (default `output/linkedin-search-<slug>-<YYYY-MM-DD>.json`).

If **both** `keywords` and `--location` are missing, stop and tell the user:

```
Usage: /linkedin-search-capture "<keywords>" [--location "<name>"] [--degree 1st|2nd|3rd+] [--pages N]
Example: /linkedin-search-capture "AI for good" --degree 2nd --pages 10
Example: /linkedin-search-capture --location "Philippines" --degree 1st --pages 2

At least one of <keywords> or --location is required — an unconstrained search would
capture an arbitrary 100 people.
```

> **Debug mode is ON.** If any step fails or returns an unexpected result, stop immediately
> and report the exact error to the user. Do NOT try fallbacks, alternative approaches, or
> workarounds.

---

## Output

A JSON array. One object per person:

| Field | Notes |
|---|---|
| `profile_url` | Canonical. No query string, no locale suffix. **The dedup key.** |
| `name` | Display name, degree marker removed |
| `degree` | `1st` / `2nd` / `3rd+` |
| `headline` | May be empty |
| `location` | **May be empty** — genuinely absent on some cards |
| `mutuals` | Free text, may be empty |
| `source_query` | The search URL that produced the row |
| `page` | Page number it came from |

This file is the handoff contract. Whatever imports it — a METIS push, a spreadsheet,
anything else — consumes this shape. Nothing in this command writes to any of them.

---

## Steps

### 0. Parse arguments

Build the search spec. Reject the run if neither `keywords` nor `--location` is present.

### 1. Get browser context

Call `mcp__claude-in-chrome__tabs_context_mcp`. Reuse an existing LinkedIn tab if the user
asked you to, otherwise `mcp__claude-in-chrome__tabs_create_mcp`. The user must already have
an active LinkedIn session — never attempt to log in or enter credentials.

### 2. Resolve each location name to a GeoID

`geoUrn` takes opaque numeric LinkedIn GeoIDs. A place name cannot be turned into one by
authoring a URL.

**First check the cache** — `automation/linkedin-automation/geo-ids.json`:

```bash
cat automation/linkedin-automation/geo-ids.json
```

On a **hit**, use the cached ID and skip to step 3. On a **miss**, resolve it through the
filter UI, then write the result back to the cache.

> Do **not** try `/voyager/api/typeahead/hitsV2` — it returns **404**. The live typeahead is
> a React-Server-Component action (`sduiid=com.linkedin.sdui.search.filters.requests.FiltersLocation…`)
> and is not usable outside the page.

Navigate to `https://www.linkedin.com/search/results/people/`, then:

```javascript
const sleep = ms => new Promise(r => setTimeout(r, ms));

// The pill is a div[role=button], NOT a <button>. Its label is "Locations" when empty
// and the place name (e.g. "Lisbon, Portugal") once a location is set — match both.
const pill = Array.from(document.querySelectorAll('[role="button"]'))
  .find(e => { const t = (e.innerText || '').trim();
               return t === 'Locations' || (t.length < 45 && /,/.test(t) && !/^People/.test(t)); });
if (!pill) throw new Error('locations pill not found');
pill.click();
await sleep(1300);

const inp = Array.from(document.querySelectorAll('input'))
  .find(i => i.placeholder === 'Add a location');
if (!inp) throw new Error('typeahead input not found');

// CRITICAL: type ONE CHARACTER AT A TIME.
// Setting inp.value in one shot fires NO suggestions, even with the native setter
// and an input event. The typeahead only responds to incremental input events.
const set = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
inp.focus();
set.call(inp, ''); inp.dispatchEvent(new Event('input', {bubbles: true}));
for (const ch of LOCATION_NAME) {
  set.call(inp, inp.value + ch);
  inp.dispatchEvent(new InputEvent('input', {bubbles: true, data: ch, inputType: 'insertText'}));
  await sleep(120);
}
await sleep(2500);

const lb = document.querySelector('[role="listbox"]');
if (!lb) throw new Error('no suggestions');
// Options are plain <span>s — they have no role="option".
[...new Set(Array.from(lb.querySelectorAll('span')).map(s => s.innerText.trim()).filter(Boolean))];
```

Show the suggestions. If none matches the requested name exactly, **stop** and ask the user
to pick — do not guess. Then select it and apply:

```javascript
const sleep = ms => new Promise(r => setTimeout(r, ms));
const lb = document.querySelector('[role="listbox"]');
Array.from(lb.querySelectorAll('span')).find(s => s.innerText.trim() === CHOSEN).click();
await sleep(1000);

// "Show results" is a bare <a><span> — no <button>, no role. Find it by text content.
const go = Array.from(document.querySelectorAll('a,button,[role="button"]'))
  .find(e => /show results/i.test(e.textContent || ''));
if (!go) throw new Error('no Show results control');
go.click();
await sleep(3500);

// Dedupe — the UI writes the id twice, e.g. ["102775852","102775852"]
const g = new URLSearchParams(location.search).get('geoUrn');
JSON.stringify({ geoUrn: g && [...new Set(JSON.parse(g))] });
```

Write the new name → ID pair into `geo-ids.json`. GeoIDs are stable, so each location costs
this dance exactly once, ever.

### 3. Author the search URL

Pure string construction — no browser interaction needed:

```
https://www.linkedin.com/search/results/people/
  ?keywords=<url-encoded>
  &network=<json array>   # ["F"]=1st  ["S"]=2nd  ["O"]=3rd+  — combinable, e.g. ["F","S"]
  &geoUrn=<json array>    # ["<id>", ...] — multiple locations OR together
  &page=<1..10>
```

Omit any parameter that wasn't requested. Both array params are JSON, URL-encoded:
`network=%5B%22F%22%5D`, `geoUrn=%5B%22102775852%22%5D`.

> Pagination is `page=N`. It is **not** `start=(N-1)*10` — that form is obsolete.

### 4. For each page 1..N — navigate, parse, flush

Batch the navigate and the parse together with `browser_batch` to halve the round-trips.

After navigating, wait ~3 s, then parse. Result cards are `a[href*="/in/"]` anchors whose
`innerText` contains a degree marker. The anchor wraps all of the card's text, so there is
**no need to walk up to a container element**.

```javascript
await new Promise(r => setTimeout(r, 3200));
const SKIP = /^(Message|Connect|Follow|Pending|View profile|Invite|Withdraw|View my services)$/i;
const DEG  = /^[•·]?\s*\d(?:st|nd|rd|th)\+?$/;

window.__rows = Array.from(document.querySelectorAll('a[href*="/in/"]'))
  .filter(a => /[•·]\s*\d(?:st|nd|rd|th)/.test(a.innerText))
  .map(a => {
    let p = a.innerText.split('\n').map(s => s.trim()).filter(Boolean).filter(s => !SKIP.test(s));

    // The degree token may be GLUED to the name ("Jane Doe • 1st") or sit on its OWN LINE
    // (verified-badge profiles render "Philipa Duthie" / "• 1st"). Handling only the glued
    // form silently shifts every later field down one — headline lands in location, etc.
    // This corrupts data without raising an error, so handle BOTH forms.
    let d = '';
    p = p.filter(s => { if (DEG.test(s)) { d = s.replace(/[^\da-z+]/gi, ''); return false; } return true; });
    let n = p.shift() || '';
    const g = n.match(/[•·]\s*(\d(?:st|nd|rd|th)\+?)/);
    if (g) { d = g[1]; n = n.replace(/\s*[•·].*$/, ''); }

    const rest = p.filter(s => !/followers?$/i.test(s) && !/^Current:/i.test(s) && !/^About:/i.test(s));
    const mu = rest.find(s => /mutual connection/i.test(s)) || '';
    const b  = rest.filter(s => s !== mu);

    // Canonicalise: drop the query string, then any trailing locale segment.
    // Seen in the wild: /in/mildred-hofkes/en , /in/theoalvesdacosta/en
    // Left unstripped these produce a DIFFERENT canonical URL for the same person,
    // which defeats METIS's contact.linkedin dedup and creates duplicate People.
    const slug = a.href.split('?')[0]
      .replace(/.*\/in\//, '')
      .replace(/\/(en|de|fr|es|pt|it|nl|ja|zh)$/, '')
      .replace(/\/$/, '');

    return { profile_url: 'https://www.linkedin.com/in/' + slug + '/',
             name: n.trim(), degree: d, headline: b[0] || '', location: b[1] || '', mutuals: mu };
  });
window.__rows.length;
```

**If the count is 0:**
- on page 1 → wait 2 s and retry once; if still 0, stop and report
- on page > 1 → normal end of results; stop and report how many pages were captured
- if a mid-run page suddenly returns 0 → LinkedIn may be rate limiting. Stop and report the
  last good page. The run resumes at that page via `page=` with no state to rebuild.

Then split the rows into character-budgeted chunks and read them back one chunk per call:

```javascript
window.__mkChunks = (budget = 700) => {
  const out = []; let cur = [], len = 0;
  for (const r of window.__rows) {
    const s = JSON.stringify(r);
    if (len + s.length > budget && cur.length) { out.push(cur.join('\n')); cur = []; len = 0; }
    cur.push(s); len += s.length + 1;
  }
  if (cur.length) out.push(cur.join('\n'));
  window.__chunks = out;
  return JSON.stringify({ rows: window.__rows.length, chunks: out.length,
                          longestRow: Math.max(...window.__rows.map(r => JSON.stringify(r).length)) });
};
window.__mkChunks();
```

Then read `window.__chunks[0]`, `window.__chunks[1]`, … one per call. These **can** be
combined in a single `browser_batch` — the size limit applies per item, not per batch.

> **Never return rows by slice count.** `javascript_tool` truncates at roughly **1000
> characters per call**, and a single rich row runs to ~450 characters — so even 5 rows per
> call loses data. The call succeeds and the tail is simply gone, with **no error**: during
> development this silently cost `location` and `headline` on 3 of 100 rows before it was
> noticed. Budget by characters, never by row count.

**Verify nothing was lost.** After writing a page's rows, compare the number written to the
`rows` count reported by `__mkChunks()`. If they differ, a chunk was truncated — stop and
report. Never report success on a count you did not check.

**Flush to the output file after every page.** Do not accumulate rows in the browser:
`window` is destroyed on navigation and anything stored there is lost. Append each page's
rows to the `--out` file, adding `source_query` and `page` as you write them.

### 5. Report

```
Captured {total} people over {pages} page(s).
Query: {search_url}
Output: {out_path}
```

If the run captured exactly 100 people across 10 pages, add:

```
⚠️  Hit LinkedIn's 100-result ceiling — this query has more results that were not returned.
    Narrow it with additional keywords or a location to reach the rest.
```

---

## Known limitations and caveats

- **100 results per query, hard.** Every search caps at 10 pages regardless of the URL.
  Wider coverage means slicing by keyword or location and unioning the results. Always tell
  the user when a slice hits the ceiling — silently returning 100 of 400 reads as complete.
- **No result total.** LinkedIn shows only a page count, so there is no way to know how many
  results a query has before walking it.
- **Location exists only on this surface.** The full connection list
  (`/mynetwork/invite-connect/connections/`) covers everyone but carries no location and no
  mutuals — only name, headline and connected-on date. Its "Search with filters" link just
  sends you back to this capped search. Do not treat it as a way to get filtered coverage.
- **`javascript_tool` output truncates at ~1000 characters per call**, silently. It is not
  2000, and it is measured per call — items inside a `browser_batch` each get their own
  budget. Any code path that returns bulk data must chunk by character count and verify the
  round-trip count afterwards.
- **`javascript_tool` blocks returning cookie or query-string data.** Returning
  `location.href`, or `href` attributes that still carry a query string, kills the call with
  `[BLOCKED: Cookie/query string data]`. Always `.split('?')[0]` before returning a URL.
  Reading `new URLSearchParams(location.search).get('geoUrn')` and returning just that value
  is fine.
- **`await` / `setTimeout` work here.** `javascript_tool` has REPL semantics with top-level
  `await`, so `await new Promise(r => setTimeout(r, N))` does wait. (The older
  `/search-to-sheet` command says otherwise; that note does not apply to this command.)
- **Blank locations are normal.** Some cards genuinely have none. Never treat `location` as
  required or drop a row for missing it.
- **Enrichment is not this command's job.** Location, about, education and current position
  are filled in on the METIS side via `download_profile` actions and
  `POST /eapi/v1/outreach/person/{id}/enrich`, from the real profile — more accurate than a
  search card anyway.

## Verified GeoIDs

Seeded in `automation/linkedin-automation/geo-ids.json`, confirmed live on 2026-07-23:

| Name | GeoID |
|---|---|
| Lisbon, Portugal | `102775852` |
| Berlin, Germany | `103035651` |
| Philippines | `103121230` |
