# METIS Automation

Use Codex or Claude Code to work with METIS. Claude Code also has LinkedIn workflows.

## What's here

**[LinkedIn Automation](linkedin-automation/README.md)** — automate LinkedIn
connection management directly from Claude Code:
- List pending invitations
- Accept invitations and auto-send a welcome message
- Message existing connections (with duplicate tracking)
- Export people search results to Google Sheets

**[METIS API](metis/README.md)** — query the live METIS instance from Codex or Claude Code:
- Search people and holons
- Browse worklists and responsible items
- Record relationship notes and advance journey steps
- **→ [Full API reference](../docs-pub/api/v1-PLAYBOOK.md)**

**[Sola import](sola-import/README.md)**: re-scan the Sola event pages behind the
2024 Portugal experiences to fill in their times and attach matched facilitators.

**[Google Sheets](google-sheets/README.md)** — the CLI bridge the other modules use
to read/write spreadsheets.

---

## Get started in Codex

1. Open the repository folder as a local project in the Codex desktop app. Select **Local** and use the existing `main` checkout.
2. Follow the [METIS setup guide](metis/README.md#setup) to configure your credentials locally.
3. Type `$metis-start` for your worklist or `$metis find person named Alice` to look up a record.
4. Review and trust the project startup hook if you want Codex to check for incoming Git commits when you open a chat.

## Get started in Claude Code

1. Create a new folder and open it in your terminal
2. Start Claude Code inside that folder
3. Tell Claude Code (cut & paste the line below into claude code):
   > clone to this folder the repo https://github.com/Vorski-Imagineering/METIS-pub
4. Reopen Claude Code inside the checked-out folder.
5. Run `/metis-setup` for instructions and a local credential check.
6. Use `/metis` to access METIS.

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
Checks whether the required METIS keys are present in the local `.env` file.

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

The examples above use Claude Code slash commands. In Codex use `$metis` for METIS queries and updates, and `$metis-start` for the daily report.

LinkedIn tools use your live Chrome browser via Claude in Chrome. The METIS API tools run in the terminal.

---

## Issue tracking

This repo also tracks public issues for the METIS project. If you find a bug or want to request a feature, [open an issue](https://github.com/Vorski-Imagineering/METIS-pub/issues).
