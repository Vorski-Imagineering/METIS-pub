# Google Sheets connector

A tiny local bridge so Claude Code can read and write a Google Sheet:

```
Claude Code → automation/google-sheets/sheets_cli.py → Google Sheets API
```

It uses a **service account** (a bot Google identity) instead of OAuth, so there's
no browser login dance. You create the service account once, share your sheet with
its email, and the script does the rest.

## One-time setup

### 1. Create a Google service account (Google Cloud Console)

These steps happen in your browser — they can't be automated.

1. Go to <https://console.cloud.google.com/> and create or select a project.
2. Enable both APIs (search each by name in the console):
   - **Google Sheets API**
   - **Google Drive API**
3. Go to **APIs & Services → Credentials → Create credentials → Service account**.
4. Give it a name, create it, then open it and go to the **Keys** tab.
5. **Add key → Create new key → JSON**, and download the file.
6. Copy the service account's email — it looks like
   `something@your-project.iam.gserviceaccount.com`.

### 2. Install the key (into `.env`)

The connector reads the key straight from the project `.env` (alongside the METIS
secrets). Because a service-account JSON contains newlines, store it **base64-encoded**
on a single line:

```bash
echo "GOOGLE_SERVICE_ACCOUNT_B64=$(base64 -i ~/Downloads/YOUR_SERVICE_ACCOUNT_FILE.json | tr -d '\n')" >> .env
```

`.env` is git-ignored, so the key is never committed. Done — you can delete the
downloaded JSON afterwards if you like.

**Alternatives** (the script tries these in order): `GOOGLE_SERVICE_ACCOUNT_B64`,
then a raw JSON string in `GOOGLE_SERVICE_ACCOUNT_JSON`, then a file at
`GOOGLE_SERVICE_ACCOUNT_FILE` (default `~/.config/gspread/service_account.json`).

### 3. Share your sheet with the service account

Open your Google Sheet → **Share** → paste the service account email →
give it **Editor** access. Without this the script gets a permission error.

### 4. Python dependencies

Already installed into `automation/google-sheets/.venv` during setup. To recreate:

```bash
python3 -m venv automation/google-sheets/.venv
automation/google-sheets/.venv/bin/pip install -r automation/google-sheets/requirements.txt
```

## Getting your Spreadsheet ID

From the sheet URL:

```
https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
                                       ^^^^^^^^^^^^^^
```

## Usage

Run via the venv's Python (no need to `activate`):

```bash
PY=automation/google-sheets/.venv/bin/python

# Read a range
$PY automation/google-sheets/sheets_cli.py \
  --spreadsheet-id "YOUR_SPREADSHEET_ID" --worksheet "Sheet1" \
  read --range "A1:D10"

# Append a row
$PY automation/google-sheets/sheets_cli.py \
  --spreadsheet-id "YOUR_SPREADSHEET_ID" --worksheet "Sheet1" \
  append --row '["Victor", "new lead", "2026-06-18"]'

# Update cells
$PY automation/google-sheets/sheets_cli.py \
  --spreadsheet-id "YOUR_SPREADSHEET_ID" --worksheet "Sheet1" \
  update --range "A1:C1" --values '[["Name", "Status", "Date"]]'
```

To point at a key in a non-default location, set `GOOGLE_SERVICE_ACCOUNT_FILE`.

## Guidance for Claude

- Before writing, always read the relevant range first.
- Never overwrite existing rows unless explicitly asked.
- Prefer `append` for new records.
- After writing, read back the changed range and confirm what changed.
