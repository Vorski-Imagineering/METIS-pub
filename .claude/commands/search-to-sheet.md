---
description: Extract LinkedIn people search results (one or more pages) and append them to a Google Sheet
allowed-tools: Bash, Read, Write, mcp__claude-in-chrome__tabs_context_mcp, mcp__claude-in-chrome__tabs_create_mcp, mcp__claude-in-chrome__navigate, mcp__claude-in-chrome__javascript_tool, mcp__claude-in-chrome__get_page_text, mcp__claude-in-chrome__read_page
---

Extract LinkedIn people search results and append them to a Google Sheet, one page at a time.

**Arguments:** `$ARGUMENTS`

Expected format:
```
<linkedin-search-url> <google-sheets-url> [pages]
```

- `linkedin-search-url` — a LinkedIn people search URL (e.g. `https://www.linkedin.com/search/results/people/?keywords=...`)
- `google-sheets-url` — a Google Sheets URL (e.g. `https://docs.google.com/spreadsheets/d/<ID>/edit...`)
- `pages` — optional integer, number of pages to process (default: 1; max: as many as LinkedIn shows)

If either URL is missing, stop and tell the user:
```
Usage: /search-to-sheet <linkedin-url> <google-sheets-url> [pages]
Example: /search-to-sheet "https://www.linkedin.com/search/results/people/?keywords=regenerative+leadership" "https://docs.google.com/spreadsheets/d/1XQx4.../edit" 3
```

> **Debug mode is ON.** If any step fails or returns an unexpected result, stop immediately and report the exact error to the user. Do NOT try fallbacks, alternative approaches, or workarounds.

---

## Sheet format

The command appends rows with four columns, writing a header if the sheet is empty:

| A | B | C | D |
|---|---|---|---|
| url | name | tagline | bio |

- **url** — canonical profile URL, no query string (e.g. `https://www.linkedin.com/in/janedoe/`)
- **name** — display name as shown on LinkedIn
- **tagline** — professional headline
- **bio** — location + degree indicator + mutual connections (e.g. `Amsterdam, Netherlands • 2nd • Victor Vorski and 2 other mutual connections`)

The sheet must be shared with the service account `metis-sheets-bot@metis-pub.iam.gserviceaccount.com` (Editor). If writes fail with a 403/PermissionError, that is why.

---

## Steps

### 0. Parse arguments

Split `$ARGUMENTS` on whitespace:
- First token → `linkedin_url`
- Second token → `sheets_url`
- Third token (optional) → `pages` (integer, default `1`)

Extract the spreadsheet ID from `sheets_url`: the path segment between `/d/` and `/edit` (or the next `/`).

### 1. Get browser context

Call `mcp__claude-in-chrome__tabs_context_mcp`. Use an existing LinkedIn tab if one is open, otherwise call `mcp__claude-in-chrome__tabs_create_mcp`.

### 2. Add header row if sheet is empty

Read the first row of the sheet:

```bash
PY=automation/google-sheets/.venv/bin/python
$PY automation/google-sheets/sheets_cli.py \
  --spreadsheet-id "<SPREADSHEET_ID>" \
  --worksheet "Sheet1" \
  read --range "A1:D1"
```

If the result is empty (no rows returned), write the header:

```bash
$PY automation/google-sheets/sheets_cli.py \
  --spreadsheet-id "<SPREADSHEET_ID>" \
  --worksheet "Sheet1" \
  append --row '["url","name","tagline","bio"]'
```

### 3. For each page (repeat `pages` times)

#### 3a. Navigate to the page

For **page 1**, navigate to `linkedin_url`.

For **page N > 1**, construct the page URL. LinkedIn search uses a `page` parameter:
- `page=1` → page 1 (or omit it)
- `page=2` → page 2
- `page=3` → page 3

Append `&page=<N>` to the base URL, or replace an existing `page=` parameter.

> The older `start=(pageNumber - 1) * 10` form is **obsolete** and no longer paginates —
> it is silently ignored, so every page returns the same first 10 results.

**Before navigating to each page after the first**, wait a randomised delay so page turns
don't look mechanical:

```javascript
const humanDelay = (meanMs, minMs, maxMs) => {
  // Shifted exponential. Do NOT clamp at the minimum instead: clamping puts ~30%
  // of draws on the exact same value, which is itself a machine fingerprint.
  const scale = Math.max(1, (meanMs - minMs) / 1.2);
  let d = minMs - scale * Math.log(1 - Math.random());
  if (Math.random() < 0.1) d += -scale * 2 * Math.log(1 - Math.random());  // distracted
  return Math.min(maxMs, Math.round(d));
};
await new Promise(r => setTimeout(r, humanDelay(12000, 5000, 90000)));  // 12 s mean
```

Tell the user up front that a multi-page run takes a couple of minutes. See the **Pacing**
section of `.claude/skills/linkedin-automation/SKILL.md`.

After navigating, wait 3 seconds for the page to load before extracting.

> **Important:** LinkedIn's page title or URL does not always confirm the page number. Trust your own URL construction.

#### 3b. Count results on the page

Use `javascript_tool` to count how many profile links with degree markers are visible:

```javascript
Array.from(document.querySelectorAll('a[href*="/in/"]'))
  .filter(a => /[•·]\s*\d(?:st|nd|rd|th)/.test(a.innerText)).length;
```

If `0`, wait 2 more seconds and retry once. If still `0`, stop and report: "No results found on page N — the search may have run out of results or the page did not load correctly."

#### 3c. Extract results in batches of 5

LinkedIn result cards are identified by `<a href="/in/...">` links that contain a degree marker (• 2nd, • 3rd) in their innerText. **Do not use action buttons (Connect/Follow/Message) as anchors** — LinkedIn does not render them for every card.

Use this extraction function. Define it, then collect every result into the DOM in one pass
(see below) — calling it a few indices at a time and returning the text directly would hit
`javascript_tool`'s silent 1000-character truncation:

```javascript
// Define the function first
const fn = i => {
  const link = Array.from(document.querySelectorAll('a[href*="/in/"]'))
    .filter(a => /[•·]\s*\d(?:st|nd|rd|th)/.test(a.innerText))[i];
  if (!link) return '(none)';

  const profileUrl = link.href.split('?')[0];
  const name = (link.innerText.split('\n')[0] || '').replace(/\s*[•·].*$/, '').trim();
  const degree = ((link.innerText.match(/[•·]\s*(\d(?:st|nd|rd|th))/) || [])[1]) || '';

  // Walk up the DOM (up to 12 levels) to find the card container
  let card = link;
  for (let j = 0; j < 12; j++) {
    card = card.parentElement;
    if (!card) break;
    if (card.innerText.includes('mutual') || card.innerText.includes('Connect')) break;
  }

  const cl = (card ? card.innerText : '').split('\n').map(l => l.trim()).filter(l => l);

  // Patterns to skip: action buttons, section labels, follower counts
  const skip = /^(Connect|Follow|Message|Pending|Summary:|Current:|mutual|\d+\s*(follower|connection))/i;
  // Location pattern — add cities/countries as needed for your target region
  const loc = /Portugal|Spain|France|Netherlands|Germany|United Kingdom|Belgium|Ireland|Italy|Switzerland|Sweden|Denmark|Austria|Norway|Czech|Poland|London|Lisbon|Amsterdam|Berlin|Paris|Madrid|Barcelona|Porto|Area/i;

  const ni = cl.findIndex(l => l.startsWith(name));
  const h = cl.slice(ni + 1).find(l => !skip.test(l) && !loc.test(l) && !/[•·]/.test(l) && l.length > 5) || '';
  const lc = cl.find(l => loc.test(l) && l.length < 60 && !l.includes('linkedin')) || '';
  const mu = cl.find(l => /mutual/i.test(l)) || '';

  return [profileUrl, name, h, lc + (degree ? ' • ' + degree : '') + (mu ? ' • ' + mu : '')].join('|');
};
```

Then call for each index individually (not in a loop — the loop won't survive between tool calls):

```javascript
// Batch 1: indices 0-4
// Collect every row, then write the payload into the DOM. Do NOT return the rows
// from javascript_tool: it truncates at exactly 1000 characters, silently, and a
// page of results runs well past that. get_page_text has no such cap.
const rows = [];
for (let i = 0; i < 10; i++) { const r = fn(i); if (r !== '(none)') rows.push(r); }
const payload = rows.join('\n') + '\n<<<END ' + rows.length + '>>>';
const art = document.createElement('article');
art.textContent = payload;         // textContent, never innerHTML — scraped page text
document.body.innerHTML = '';      // is untrusted and must not be parsed as markup
document.body.appendChild(art);
'payload written: ' + rows.length + ' rows, ' + payload.length + ' chars';
```

Then call `mcp__claude-in-chrome__get_page_text` **once** to retrieve them all.

Parse each returned line by splitting on `|`:
- Field 0 → url
- Field 1 → name  
- Field 2 → tagline
- Field 3 → bio

**Check the `<<<END n>>>` sentinel is present and `n` matches the rows you parsed.** It is
written last, so if it is missing the payload was truncated and the page is incomplete — stop
and report rather than writing partial data to the sheet.

Destroying the page body here is safe: the rows are already extracted, and the next step
navigates away anyway.

#### 3d. Write the page's results to the sheet immediately

**Do not accumulate results across pages.** Write after each page before navigating away — the browser window object resets on navigation and any stored state is lost.

Use the Python gspread library directly (faster than `sheets_cli.py` for multi-row appends):

```bash
automation/google-sheets/.venv/bin/python3 - << 'PYEOF'
import os, base64, json, warnings
warnings.filterwarnings('ignore')
from dotenv import load_dotenv
load_dotenv(dotenv_path='.env')
import gspread
from google.oauth2.service_account import Credentials

b64 = os.environ['GOOGLE_SERVICE_ACCOUNT_B64']
key = json.loads(base64.b64decode(b64))
creds = Credentials.from_service_account_info(key, scopes=[
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
])
gc = gspread.authorize(creds)
ws = gc.open_by_key('<SPREADSHEET_ID>').get_worksheet_by_id(0)

rows = [
  # One list per result: [url, name, tagline, bio]
  ["https://www.linkedin.com/in/example/", "Jane Doe", "Regenerative leadership coach", "Amsterdam • 2nd • 3 mutual connections"],
  # ... add all extracted rows here
]

ws.append_rows(rows, value_input_option='RAW')
total = len(ws.get_all_values())
print(f"Wrote {len(rows)} rows. Sheet now has {total} rows (including header).")
PYEOF
```

Replace `<SPREADSHEET_ID>` with the actual ID and fill in `rows` with the extracted data. Use `get_worksheet_by_id(0)` to target the first tab (works regardless of tab name).

#### 3e. Report progress

After each page: `Page {N}: extracted {count} results, wrote to sheet.`

### 4. Final summary

```
Done — processed {N} pages, wrote {total_rows} results.
Sheet: <sheets_url>
Columns: url | name | tagline | bio
```

---

## Known limitations and caveats

- **Location regex is Europe-focused.** If your search targets other regions, you'll need to add city/country names to the `loc` pattern in step 3c, or the location field will be blank.
- **Some profiles have no visible headline.** LinkedIn doesn't always render a headline for every card. Those entries will have an empty `tagline` — this is expected.
- **Tool output truncation.** `javascript_tool` output is capped at **exactly 1000 characters**
  — measured, not estimated: a 1000-char return arrives intact, a 1001-char return loses its
  last character to `[TRUNCATED]`, with no error. It is **not** 2000, as this file previously
  claimed; five rich result rows run to ~1666 chars and silently lost their tail under the old
  advice. This is why results are now written into the DOM and read back with a single
  `get_page_text` call, which has no such cap (measured intact at 11,211 characters). Always
  check the `<<<END n>>>` sentinel rather than trusting that a page came back whole.
- **LinkedIn rate limiting.** If pages start returning 0 results mid-run, LinkedIn may be throttling. Stop, wait a few minutes, then resume from where you left off by using the `page=` parameter directly.
- **Page 10+ may not exist.** LinkedIn caps most people searches at ~100 results (10 pages). If a page returns 0 results and you haven't reached that cap, the search is exhausted.
- **`await` / `setTimeout` in `javascript_tool`.** Promises with `setTimeout` inside `javascript_tool` do not await correctly. All extraction is synchronous. Do not use `await new Promise(r => setTimeout(r, N))` — it returns immediately.
