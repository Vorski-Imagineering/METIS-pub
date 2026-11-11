---
name: metis
description: >
  Query the METIS Read API — search people and holons, browse responsible worklists,
  read notes and memberships, and record relationship/membership updates. Use this skill
  whenever the user wants to look something up in METIS or update it. Trigger on phrases like:
  "who should I contact today", "show my overdue items", "find person named ...",
  "list members of the ... holon", "get holon by slug", "add a note to relationship ...",
  "advance ... to the next step", or any request involving METIS people, holons, journeys,
  memberships, relationships, or follow-up worklists.
---

# METIS

This skill connects Claude Code to the live METIS instance at `https://app.the-gathering.earth`
via the `/api/v1/` Read API. It handles a two-step Bearer-token auth flow, then makes
authenticated `curl` calls. No browser needed.

## Routing

1. **First-time / setup** ("set up METIS", "save my credentials") → run the `/metis-setup` command.
2. **Help / what can I ask** ("what can I do with METIS", "metis help") → run the `/metis-help` command.
3. **Any actual query or update** → run the `/metis` command, which performs the auth flow and the API call.

Read the relevant command file in `.claude/commands/` before starting work.

## References

- **Setup & usage guide**: `automation/metis/README.md`
- **Full `/api/v1/` reference** (endpoints, params, response shapes, error codes, access model): `docs-pub/api/v1-PLAYBOOK.md`
  — **not** `docs-pub/api/API.md`, which is just a one-page index pointing at the per-surface playbooks
  and has no endpoint/param detail itself, and **not** `docs-pub/api/PLAYBOOK.md` (no `v1-` prefix),
  which documents the separate `/api/` surface (agents, chat, webhooks) and has no mention of
  holons/people/memberships at all. Three similarly-named files, only one has what you need — always
  read `v1-PLAYBOOK.md` for `/api/v1/` questions.
- **Live schema** (requires auth): `https://app.the-gathering.earth/api/v1/openapi.json`

## Before you call: read the reference for your task

The gotchas are split by task so you only load what applies. Read the matching file
(more than one if the task spans them) **before** making calls:

| Task | Read |
|---|---|
| Finding/listing holons, people, relationships; "who's for outreach" counts | `references/lookups.md` |
| Creating or editing Organisations, Camps, Experiences; links, logos, cancelling, host orgs, descriptions | `references/holons.md` |
| Creating journeys, offering a journey on a holon, moving people between journeys, `journey_not_offered`, adding a person to two holons, class list in the web app | `references/journeys-and-memberships.md` |

When you learn a new gotcha, add it to the matching reference file, not here. Only notes
that apply to *every* METIS call belong in this file.

## Always-on notes

- Credentials live in `.env` (`API_LOGIN_SECRET`, `METIS_EMAIL`, `METIS_PASSWORD`); the session token lasts 24 hours.
- The API is read-mostly. Besides the update endpoints (`POST /relationships/{id}/update`,
  `POST /memberships/{id}/update`, `POST /holons/{id}/update` — each requires a non-empty
  `note` where applicable), it can also create records: `POST /people` (a Person, optionally
  with one initial Membership + note), `POST /holons` (a top-level Organisation only),
  `POST /camps` (a Camp under a gathering) and `POST /experiences` (an Experience holon, but
  only as a child of an existing Camp/Gathering). See `v1-PLAYBOOK.md` for the per-kind id semantics.
- **The live schema can change mid-session.** It's the authoritative source, not the docs in
  this repo — if a field the docs describe (e.g. `journeys` on a class) seems to be missing,
  re-fetch `/api/v1/openapi.json` before concluding it doesn't exist.
- **`info_fields` are per-class admin config, not API schema.** They're set on each class in
  admin and change without a deploy, so neither the docs nor `openapi.json` list them — read
  the full `config.info_field_groups` of every relevant class from `GET /api/v1/classes`
  (don't grep a few lines of it). A missing field is an admin config change, not a backend
  feature request. Fields can also change **mid-run**, so a long batch job should expect a
  sudden `400` on a field it was writing fine a minute ago. Example: on 2026-09-28 both
  `experience` classes switched to `start_date`, `start_time` and `length` (a `duration`:
  integer minutes, with end = start + length on the clock face), and `end_date` was removed.
  Local timezone lives on the parent `local_gathering`'s `timezone` field.
- **`curl` vs Python for these calls:** use `curl`, not Python's `urllib`/`requests` with default
  headers — the site's Cloudflare WAF blocks the default Python User-Agent with a `403` whose
  body is an HTML/Cloudflare "error code: 1010" page, not a JSON API error. That 403 looks like
  a permission_denied response but isn't one; don't diagnose it as a permissions/scope problem
  before checking whether the same call works via `curl`.
- **Parsing responses in Python:** list responses (e.g. `GET /holons`) can contain invalid
  UTF-8 bytes and raw control characters inside strings, so a plain `json.load` fails with
  `UnicodeDecodeError` or `Invalid control character`. Decode with
  `json.loads(raw.decode('utf-8', 'replace'), strict=False)`. Save `curl` output with `-o file`
  rather than `r=$(curl …); echo "$r" | python3`, since the shell round-trip mangles it too.
  A working client (login, get/post with a browser User-Agent) is `Metis` in
  `automation/sola-import/sola_scan.py`.
