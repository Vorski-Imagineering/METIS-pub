# METIS API

Query the METIS API from Codex or Claude Code. Use natural language to search people and holons, browse worklists, and record relationship updates through `/api/v1/`.

---

## What this does

The `$metis` skill in Codex and `/metis` command in Claude Code connect to the live METIS instance at `https://app.the-gathering.earth`. Once authenticated, you can ask for these tasks.

- "Find everyone named Alice in METIS"
- "Show me my overdue responsible items"
- "List the members of the Borderland 2026 holon"
- "Add a note to relationship 42 and advance its step"

The local client handles authentication and API calls.

---

## Prerequisites

- Codex or Claude Code, and Python 3.9 or newer
- A METIS account with a linked Person record
- The shared `API_LOGIN_SECRET` for the instance (ask your METIS admin)

---

## Setup

If the repo root has no `.env` file, create it from the example. On macOS or Linux, run this from the repository root.

```bash
(umask 077 && cp .env.example .env)
```

Open `.env` in your editor and enter these values locally. Use the literal values without quotes, and keep the file gitignored.

```
API_LOGIN_SECRET=your_shared_secret_here
METIS_EMAIL=your_metis_account_email
METIS_PASSWORD=your_metis_account_password
```

Check whether the keys are present with `python3 scripts/metis_api.py credentials`. The check displays only key names and whether each is present. To verify authentication, run `python3 scripts/metis_api.py request GET /auth/whoami`. On Windows you can use `py -X utf8` in place of `python3`.

---

## Usage

In Codex, use a skill by name or describe what you need.

```text
$metis-start
$metis-start 10
$metis-start all
$metis find person named "Alice"
$metis get holon by slug borderland-2026
```

In Claude Code, use slash commands.

```
/metis find person named "Alice"
/metis show my overdue items
/metis get holon by slug borderland-2026
/metis add note to relationship 42: "Had a great call, following up next week"
```

---

## API reference

Full endpoint documentation: [docs-pub/api/v1-PLAYBOOK.md](../../docs-pub/api/v1-PLAYBOOK.md)
(`docs-pub/api/PLAYBOOK.md`, without the `v1-` prefix, documents the separate `/api/` surface —
agents, chat, webhooks — not this one.)

Live schema (requires auth): `https://app.the-gathering.earth/api/v1/openapi.json`  
Swagger UI (requires auth): `https://app.the-gathering.earth/api/v1/docs`
