# METIS API

Query the METIS Read API from Claude Code. Search people and holons, browse worklists, and record relationship updates — all via natural language backed by the `/api/v1/` endpoint.

---

## What this does

The `/metis` skill connects Claude Code to the live METIS instance at `https://app.the-gathering.earth`. Once authenticated, you can ask things like:

- "Find everyone named Alice in METIS"
- "Show me my overdue responsible items"
- "List the members of the Borderland 2026 holon"
- "Add a note to relationship 42 and advance its step"

Claude handles the auth flow and API calls — you just describe what you want.

---

## Prerequisites

- Claude Code installed
- A METIS account with a linked Person record
- The shared `API_LOGIN_SECRET` for the instance (ask your METIS admin)

---

## Setup

Create a `.env` file in the repo root (it's gitignored):

```bash
cp .env.example .env
```

Open `.env` and fill in:

```
API_LOGIN_SECRET=your_shared_secret_here
```

You'll be prompted for your METIS email and password when you first run a query. The session token lasts 24 hours.

---

## Usage

Just describe what you want to do with METIS data. Examples:

```
/metis find person named "Alice"
/metis show my overdue items
/metis get holon by slug borderland-2026
/metis add note to relationship 42: "Had a great call, following up next week"
```

---

## API reference

Full endpoint documentation: [docs-pub/api/PLAYBOOK.md](../../docs-pub/api/PLAYBOOK.md)

Live schema (requires auth): `https://app.the-gathering.earth/api/v1/openapi.json`  
Swagger UI (requires auth): `https://app.the-gathering.earth/api/v1/docs`
