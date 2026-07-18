# METIS-pub

A public collection of automation tools and workflows built around the METIS ecosystem.

📖 **[Full docs site: docs.the-gathering.earth](https://docs.the-gathering.earth/)**

## What's here

This repo covers two different things — don't confuse them:

### 📚 METIS Docs

The user- and integrator-facing manual for the METIS platform itself (core concepts, apps,
API reference). Synced automatically from the METIS source repo — not edited here.

**→ [docs-pub/README.md](docs-pub/README.md)**

### 🤖 Automation (built in this repo)

Claude Code slash commands and skills that automate work *using* METIS and LinkedIn — built
and maintained in this repo, independent of the METIS docs above.

**[LinkedIn Automation](automation/linkedin-automation/README.md)** — automate LinkedIn
connection management directly from Claude Code:
- List pending invitations
- Accept invitations and auto-send a welcome message
- Message existing connections (with duplicate tracking)
- Export people search results to Google Sheets

**[METIS API](automation/metis/README.md)** — query the live METIS instance from Claude Code
using natural language:
- Search people and holons
- Browse worklists and responsible items
- Record relationship notes and advance journey steps
- **→ [Full API reference](docs-pub/api/PLAYBOOK.md)**

**[Google Sheets](automation/google-sheets/README.md)** — the CLI bridge the other modules use
to read/write spreadsheets.

---

## Getting Started in claude code

1. Create a new folder and open it in your terminal
2. Start Claude Code inside that folder
3. Tell Claude Code (cut & paste the line below into claude code):
   > clone to this folder the repo https://github.com/Vorski-Imagineering/METIS-pub
6. Once it's done, exit Claude and re-open it — make sure you are now inside the checked-out folder
7. Run `/metis-setup` — it will ask for your email, password, and API key; enter them
8. You're ready — use `/metis` to access METIS

---

These tools are designed for people using [Claude Code](https://claude.ai/code) who want to automate repetitive work — no programming background required.

---

## Suggested usage

```
/metis who should I contact today?
```
Shows your overdue and due-today responsible items — people and organisations — sorted by urgency. A good daily starting point.

```
/metis show me my overdue items
/metis find person named "Alice"
/metis list members of the Borderland 2026 holon
/metis add note to relationship 42: "Had a great call, following up next week"
```

```
/metis-setup
```
First-time setup: saves your METIS email, password, and API key to `.env` so you don't have to re-enter them.

```
/metis-help
```
Shows available commands and more example queries.

```
/invites
/accept-one
/accept-many 5
/message-connections 10
```
LinkedIn connection management — list pending invitations, accept them with a personalised message, and reach out to existing connections.

---

## Using these tools

All automations run as Claude Code slash commands. Open this folder in Claude Code, follow the setup guide for the module you want, and type `/command-name` to run it.

LinkedIn tools use your live Chrome browser (via the [Claude in Chrome](https://chromewebstore.google.com) extension). METIS API tools use `curl` via the terminal — no browser needed.

---

## Issue tracking

This repo also tracks public issues for the METIS project. If you find a bug or want to request a feature, [open an issue](../../issues).
