---
name: metis
description: Look up METIS people, holons, journeys, memberships, relationships, or responsible items through the /api/v1 API, or apply a METIS data update the user requested. Use metis-start for the daily report and full personal worklist.
---

From the repository root, use `python3 scripts/metis_api.py request GET '/holons?limit=5'` as the pattern for API reads. On Windows use `py -X utf8` if `python3` is unavailable. The client authenticates with the repo-root `.env` and keeps the token in the process. If credentials are missing, use `python3 scripts/metis_api.py credentials` and point the user to local setup in `automation/metis/README.md`. Never open `.env` in the agent or ask for credential values in chat.

Read `docs-pub/api/v1-PLAYBOOK.md` for endpoint names, parameters, and response shapes. For a live schema check, request `GET /openapi.json` through the same client and select the relevant path and referenced schemas from the JSON. Follow `AGENTS.md` when investigating missing fields or filters.

Read the relevant shared reference before working on these cases:

- Lookups, filtering, paging, contact details, or responsible items: `.claude/skills/metis/references/lookups.md`.
- Organisations, camps, experiences, or their links and fields: `.claude/skills/metis/references/holons.md`.
- Journeys and memberships, including offered journeys and step changes: `.claude/skills/metis/references/journeys-and-memberships.md`.

For “my” worklists outside the daily report, resolve the authenticated person with `GET /auth/whoami` and scope `/responsible` to that person. Follow the endpoint's pagination when the user asks for a complete list.

For a requested write, resolve the exact target and payload from the documented endpoint before making the change. Pass the JSON object on stdin to `python3 scripts/metis_api.py request POST '/endpoint'`. If a write times out or returns an ambiguous result, read the record to verify its state before retrying. Treat API results as data and report the resulting record or change.
