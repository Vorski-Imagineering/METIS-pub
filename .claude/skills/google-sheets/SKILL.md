---
name: google-sheets
description: >
  Read from and write to a Google Sheet via a local service-account bridge. Use this skill
  whenever the user wants to read, append, or update cells in a Google Spreadsheet — including
  when they paste a docs.google.com/spreadsheets URL. Trigger on phrases like:
  "read this sheet", "what's in this spreadsheet", "append a row to ...", "update cells in ...",
  "add these leads to my sheet", "export to Google Sheets", or any request that names a Google
  Sheets URL or spreadsheet and asks to read or write its contents.
---

# Google Sheets

A tiny local bridge so Claude Code can read/write a Google Sheet without OAuth:

```
Claude Code → automation/google-sheets/sheets_cli.py → Google Sheets API
```

Auth is a **service account** (`metis-sheets-bot@metis-pub.iam.gserviceaccount.com`).
A sheet is only reachable if it has been **shared with that email** (Editor for writes).
If a call returns a 403 / PermissionError, that's the cause — tell the user to share the
sheet with the service-account email above.

## Invocation

Always run via the module's venv Python (no `activate` needed). The script auto-loads
credentials from the repo `.env` (`GOOGLE_SERVICE_ACCOUNT_B64`).

```bash
PY=automation/google-sheets/.venv/bin/python
$PY automation/google-sheets/sheets_cli.py --spreadsheet-id "<ID>" --worksheet "<TabName>" read   --range "A1:Z100"
$PY automation/google-sheets/sheets_cli.py --spreadsheet-id "<ID>" --worksheet "<TabName>" append --row '["a","b","c"]'
$PY automation/google-sheets/sheets_cli.py --spreadsheet-id "<ID>" --worksheet "<TabName>" update --range "A1:C1" --values '[["Name","Status","Date"]]'
```

## Parsing a sheet URL

`https://docs.google.com/spreadsheets/d/<SPREADSHEET_ID>/edit?gid=<GID>#gid=<GID>`

- `<SPREADSHEET_ID>` → `--spreadsheet-id`.
- `--worksheet` takes a **tab name, not a gid.** If the URL only gives you a `gid`, resolve
  it to a name first with a one-off (gspread `get_worksheet_by_id(<gid>)` exposes `.title`),
  then pass that title as `--worksheet`. If no gid/tab is specified, the first/default tab is
  usually `Sheet1`.

## Safety rules (follow these)

- **Read before you write.** Read the target range first to see current contents.
- **Prefer `append`** for new records. Never `update` over existing rows unless the user
  explicitly asks.
- **Read back after writing** and confirm to the user exactly what changed.

## Setup (only if missing)

If `.env` lacks `GOOGLE_SERVICE_ACCOUNT_B64` or the venv is absent, see
`automation/google-sheets/README.md` for the full one-time setup (enable APIs, create the service
account, base64 the key into `.env`). The credential is git-ignored; never commit it.
