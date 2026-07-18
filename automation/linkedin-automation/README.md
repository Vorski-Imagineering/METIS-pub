# LinkedIn Automation

Automate your LinkedIn connection workflow directly from Claude Code. Accept pending invitations, send outreach messages, and export people search results to a Google Sheet — all by typing a slash command.

No coding required after setup.

---

## What this does

| Command | What it does |
|---|---|
| `/invites` | List all your pending connection invitations |
| `/accept-one` | Accept the next pending invitation and send your message template |
| `/accept-many N` | Accept the next N invitations and message each one |
| `/message-connections N` | Message N existing connections who haven't been messaged yet |
| `/search-to-sheet <url>` | Extract LinkedIn people search results and save to CSV / Google Sheet |

---

## Prerequisites

Before using any of these commands, you need:

1. **Claude Code** installed — [get it here](https://claude.ai/code)
2. **Claude in Chrome** browser extension — install it from the Chrome Web Store, then grant it access to `linkedin.com`
3. **Chrome** open and logged into LinkedIn
4. A Google Sheet (only needed for `/search-to-sheet`)

---

## Setup

### Step 1 — Create your message template

This is the message that gets sent automatically after you accept an invitation.

1. Copy the example file:
   ```
   cp automation/linkedin-automation/setup/accept-invite.txt.example texts/accept-invite.txt
   ```
2. Open `texts/accept-invite.txt` in any text editor and write your message. Keep it under ~500 characters.

### Step 2 — Set up Google Sheets (only for `/search-to-sheet`)

Skip this step if you don't plan to use `/search-to-sheet`.

1. Open a new Google Sheet
2. Click **Extensions → Apps Script**
3. Delete the default code and paste the contents of `automation/linkedin-automation/scripts/append-rows.gs`
4. Click **Deploy → New deployment → Web app**
   - Execute as: **Me**
   - Who has access: **Anyone**
5. Click **Deploy** and copy the Web App URL
6. Copy the config example file and fill in your URL:
   ```
   cp automation/linkedin-automation/setup/config.json.example config.json
   ```
7. Open `config.json` and replace `YOUR_GOOGLE_SHEETS_WEB_APP_URL_HERE` with your URL

### Step 3 — Open this folder in Claude Code

Open the METIS-pub folder in Claude Code. The slash commands will be available automatically.

---

## Using the commands

**Check your pending invitations:**
```
/invites
```

**Accept one invitation (and send your message):**
```
/accept-one
```

**Accept 5 invitations at once:**
```
/accept-many 5
```

**Message 10 existing connections:**
```
/message-connections 10
```
This skips anyone you've already messaged (tracked in `messaged-log.txt`).

**Export a LinkedIn search to Google Sheet:**
```
/search-to-sheet https://www.linkedin.com/search/results/people/?keywords=...
```

---

## How it works

Each command is a markdown file in `.claude/commands/`. When you type `/accept-one`, Claude Code reads that file and follows the step-by-step instructions — navigating your Chrome browser, clicking buttons, reading page content, and sending messages, all using the Claude in Chrome extension.

You don't need to understand any of this to use it. Just type the command.

---

## Files created automatically

- `texts/accept-invite.txt` — your message template (you create this in setup)
- `config.json` — your Google Sheets URL (you create this in setup)
- `messaged-log.txt` — auto-created, tracks who you've already messaged so you don't duplicate
- `output/search-results.csv` — auto-created when you run `/search-to-sheet`

These files are excluded from git (see `.gitignore`) so your personal data stays local.

---

## Troubleshooting

**Command not working / Claude seems confused**
- Make sure the Claude in Chrome extension is active on the LinkedIn tab
- Check that Chrome is open and you're logged into LinkedIn
- Try closing and reopening the LinkedIn tab, then run the command again

**LinkedIn page structure changed**
- LinkedIn periodically updates its DOM. If a command fails with "element not found" errors, open a GitHub issue in this repo describing what happened.

**Messages going to wrong people / duplicates**
- Check `messaged-log.txt` — it lists everyone you've already messaged
- The `/message-connections` command reads this file before sending anything
