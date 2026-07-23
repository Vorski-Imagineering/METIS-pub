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
| `/message-person <url>` | Send a message to one connection |
| `/message-connections N` | Message N existing connections who haven't been messaged yet |
| `/search-to-sheet <url>` | Extract LinkedIn people search results and save to CSV / Google Sheet |
| `/linkedin-search-capture "<keywords>"` | Search by keyword / location / degree and capture results to a JSON file |
| `/linkedin-find-person "Name \| Org \| Country"` | Find someone's profile URL by name |
| `/connect-from-sheet <sheet>` | Send connection requests to everyone in a spreadsheet |

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

**Capture a filtered search to a JSON file:**
```
/linkedin-search-capture "AI for good" --degree 2nd --pages 10
/linkedin-search-capture --location "Philippines" --degree 1st --pages 2
```
Filters by keyword, location and connection degree. Location names are resolved to LinkedIn's
internal location IDs and cached in `geo-ids.json`, so each place costs that lookup only once.

---

## Pacing — why runs take a while

**These commands deliberately go slowly.** Every workflow that loops over people or pages
waits a randomised amount of time between steps, drawn from an exponential distribution so
the rhythm resembles a person browsing rather than a script. Roughly:

| Action | typical gap |
|---|---|
| Next page of search results | ~12 s |
| Visiting a profile | ~45 s |
| Accepting an invitation | ~30 s |
| Sending a message | ~90 s |
| Sending a connection request | ~2 min |

Every 8–15 actions there is also a longer break of 2–10 minutes.

So `/connect-from-sheet` with 20 rows is a **45–60 minute job**, not a few seconds. Each
command tells you the expected duration before it starts, and announces every long break
with its length and where it has got to — a silent pause is never a hang. Short per-item
delays aren't announced, because the progress lines already show the run is alive.

Everything is written as it goes (the sheet, the log, the output file), so a run you stop —
or one that stops itself — picks up cleanly where it left off.

### Rate limiting is not an error

If you push LinkedIn too hard it doesn't return an error. It quietly serves a **reduced
profile page**: the right name, headline and location, but no About text, no follower count,
no company or school. Everything looks like it worked while most of the data is missing.

The commands detect this — a missing About *together with* a missing follower count means
throttled, since a genuine profile with no About still shows its follower count. When that
happens the run stops and tells you how far it got, rather than recording empty fields as if
they were real. Give it 15–30 minutes before trying again.

### Profile visits are visible

Reading a profile is not anonymous — the person is shown that you viewed them. A bulk
enrichment run over 100 people means 100 people see that. Worth deciding deliberately before
starting one.

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
- `output/linkedin-search-*.json` — auto-created when you run `/linkedin-search-capture`

These files are excluded from git (see `.gitignore`) so your personal data stays local.

One file that *is* committed: `automation/linkedin-automation/geo-ids.json`, the cache mapping
place names to LinkedIn's internal location IDs. It holds no personal data, and sharing it
means nobody has to redo the lookup for a place someone has already resolved.

---

## Troubleshooting

**Command not working / Claude seems confused**
- Make sure the Claude in Chrome extension is active on the LinkedIn tab
- Check that Chrome is open and you're logged into LinkedIn
- Try closing and reopening the LinkedIn tab, then run the command again

**LinkedIn page structure changed**
- LinkedIn periodically updates its DOM. If a command fails with "element not found" errors, open a GitHub issue in this repo describing what happened.

**A run stopped saying it was rate limited**
- This is working as intended. LinkedIn started serving reduced pages, and the command
  stopped rather than saving half-empty records. Wait 15–30 minutes and run it again — it
  resumes from where it stopped.
- If it happens repeatedly, leave it for the day. Nothing is lost; everything already
  captured has been written.

**A command seems to be doing nothing**
- Check whether it announced a break (`Taking a 6 min break…`). Pauses of 2–10 minutes are
  normal and deliberate — see [Pacing](#pacing--why-runs-take-a-while).
- Runs are meant to take minutes to hours. If you need a quick result, ask for fewer items
  rather than expecting it to go faster.

**Messages going to wrong people / duplicates**
- Check `messaged-log.txt` — it lists everyone you've already messaged
- The `/message-connections` command reads this file before sending anything
