---
description: Send LinkedIn connection requests to every person in a Google Sheet who hasn't been contacted yet, then mark each row as sent
allowed-tools: Read, Bash, mcp__claude-in-chrome__tabs_context_mcp, mcp__claude-in-chrome__tabs_create_mcp, mcp__claude-in-chrome__navigate, mcp__claude-in-chrome__javascript_tool, mcp__claude-in-chrome__read_page
---

Send LinkedIn connection requests to people listed in a Google Sheet, then mark each row as "sent" in the sheet.

`$ARGUMENTS` may be:
- A Google Sheets URL (e.g. `https://docs.google.com/spreadsheets/d/<ID>/edit…`)
- A spreadsheet name (e.g. `Guy test outreach`)
- Optionally followed by a limit: `… 5` to process only the first N pending rows

## Expected sheet format

The sheet must have these columns (header row 1):

| Column | Name | Description |
|--------|------|-------------|
| A | url | Full LinkedIn profile URL, e.g. `https://www.linkedin.com/in/josephine-matthews/` |
| B | name | Person's display name (used for progress output only) |
| C–D | any | tagline, bio, or other data — ignored |
| E | connection requested | Status column — blank = not yet sent, `sent` = already done |

Rows where column E already contains any non-empty value are **skipped**.

## Setup

Ensure the sheet is shared with the service account:
`metis-sheets-bot@metis-pub.iam.gserviceaccount.com` (Editor access)

## Steps

### 1. Resolve the spreadsheet

**If given a URL**: extract the `<SPREADSHEET_ID>` from between `/d/` and `/edit`.

**If given a name**: search Google Drive to find it:
```
mcp__claude_ai_Google_Drive__search_files with query: title contains '<name>'
```
Use the `id` field from the first matching spreadsheet result.

### 2. Read the sheet

```bash
PY=automation/google-sheets/.venv/bin/python
$PY automation/google-sheets/sheets_cli.py \
  --spreadsheet-id "<ID>" \
  --worksheet "Sheet1" \
  read --range "A1:E100"
```

Parse the result as a list of rows. Row 1 is the header — skip it.
Build a work list of rows where:
- Column A (url) is non-empty
- Column E (connection requested) is empty or blank

If `$ARGUMENTS` includes a numeric limit N, take only the first N rows from the work list.

If the work list is empty, tell the user "No pending rows found — all connections already sent (or sheet is empty)." and stop.

### 3. Get a browser tab

Call `mcp__claude-in-chrome__tabs_context_mcp`. Use an existing LinkedIn tab if one is open, otherwise call `mcp__claude-in-chrome__tabs_create_mcp` to open a new one.

### 4. For each person in the work list

#### 4a. Extract the vanity name

Strip the vanity name from column A's LinkedIn URL:
- Remove trailing slash: `https://www.linkedin.com/in/josephine-matthews/` → `josephine-matthews`
- Handle `/en/` suffix: `https://www.linkedin.com/in/dr-marjolein-sterk-414b8a36/en/` → `dr-marjolein-sterk-414b8a36`
- Pattern: take the path segment immediately after `/in/`

#### 4b. Navigate to the invite URL

```
https://www.linkedin.com/preload/custom-invite/?vanityName=<vanityName>
```

This URL opens the profile and triggers LinkedIn's "Add a note?" invite modal automatically.

#### 4c. Wait for and dismiss the modal

Run this JavaScript (wait up to 5 seconds for the modal):

```javascript
await new Promise(r => setTimeout(r, 2000));
const modal = document.querySelector('[role="dialog"]');
if (modal) {
  const btn = Array.from(document.querySelectorAll('button'))
    .find(b => b.textContent.trim() === 'Send without a note');
  if (btn) {
    btn.click();
    await new Promise(r => setTimeout(r, 1000));
    'sent';
  } else {
    // Modal is open but "Send without a note" is missing — log button labels
    JSON.stringify(Array.from(document.querySelectorAll('button'))
      .map(b => b.textContent.trim()).filter(t => t && t.length < 40));
  }
} else {
  JSON.stringify({ noModal: true, url: window.location.href });
}
```

**If result is `'sent'`**: proceed to 4d.

**If result is `{ noModal: true }`**: the person may already be connected, or the profile URL is wrong. Skip and note it in the summary (do NOT mark as sent).

**If result is a list of button labels**: the modal opened but the expected button wasn't found. Stop and report the button list so the flow can be debugged.

#### 4d. Update the spreadsheet

```bash
$PY automation/google-sheets/sheets_cli.py \
  --spreadsheet-id "<ID>" \
  --worksheet "Sheet1" \
  update --range "E<rowNumber>" --values '[["sent"]]'
```

`<rowNumber>` is the 1-based sheet row (header is row 1, so the first data row is row 2).

#### 4e. Print progress

```
[{i}/{total}] ✓ Connection request sent to **{name}**
```

### 5. Final summary

After all rows are processed, print:

```
Done — sent {N} connection requests: {name1}, {name2}, …
Skipped (already connected or no modal): {skippedName1}, …   ← only if any were skipped
```

## Error handling

- **403 / PermissionError from sheets_cli**: the sheet isn't shared with the service account. Tell the user to share it with `metis-sheets-bot@metis-pub.iam.gserviceaccount.com`.
- **No modal and page redirected away from LinkedIn**: likely a rate-limit or login session expired. Stop, report, ask user to check the browser.
- **Any JS error**: stop immediately and report the exact error. Do not silently skip.
- **Empty vanity name after stripping**: skip the row and warn that the URL in column A is not a valid LinkedIn profile URL.
