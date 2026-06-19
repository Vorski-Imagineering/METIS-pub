---
description: Show how to connect Claude Code to a Google Sheet
---

# Google Sheets — Quick Setup Guide

Claude Code can read and write Google Sheets directly from the terminal.

---

## Reading a public sheet (no setup needed)

If your sheet is shared as **Anyone with the link can view** (or edit), Claude can
read it immediately — no credentials required.

Just share the spreadsheet URL and ask Claude to read it.

---

## Writing to a sheet (or reading a private sheet)

Writing requires a service-account key. Two steps:

### Step 1 — Share your sheet with the bot

Open your Google Sheet → **Share** → add this email as **Editor**:

```
metis-sheets-bot@metis-pub.iam.gserviceaccount.com
```

### Step 2 — Get the magic key from Victor

Ask Victor for the `GOOGLE_SERVICE_ACCOUNT_B64` value, then add it to your `.env`:

```
GOOGLE_SERVICE_ACCOUNT_B64=<paste value here>
```

The `.env` file is git-ignored, so the key is never committed.

---

## That's it

Once the key is in `.env`, share your sheet URL with Claude and say what you want
to read or write. The `google-sheets` skill handles the rest.

**Troubleshooting:** if Claude reports a 403 / permission error, double-check that
the sheet is shared with the bot email above (Editor access).
