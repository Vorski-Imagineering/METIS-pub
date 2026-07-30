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
- **Full `/api/v1/` reference** (endpoints, params, response shapes, error codes, access model): `docs-pub/api/API.md`
  — **not** `PLAYBOOK.md`, which documents the separate `/api/` surface (agents, chat, webhooks) and has
  no mention of holons/people/memberships at all. Grepping the wrong file for a term like "holon" will
  silently return nothing and look like the feature doesn't exist — always read `API.md` for `/api/v1/` questions.
- **Live schema** (requires auth): `https://app.the-gathering.earth/api/v1/openapi.json`

## General notes

- Credentials live in `.env` (`API_LOGIN_SECRET`, `METIS_EMAIL`, `METIS_PASSWORD`); the session token lasts 24 hours.
- The API is read-mostly. Besides the update endpoints (`POST /relationships/{id}/update`,
  `POST /memberships/{id}/update`, `POST /holons/{id}/update` — each requires a non-empty
  `note` where applicable), it can also create records: `POST /people` (a Person, optionally
  with one initial Membership + note) and `POST /experiences` (an Experience holon, but only
  as a child of an existing Camp/Gathering). See PLAYBOOK.md for the per-kind id semantics.
- **There is no endpoint to create a top-level Holon** (e.g. a new Organisation or Camp) —
  confirmed by enumerating every path in the live `/api/v1/openapi.json`. That has to happen
  in the METIS web app by a human. Tracked as [METIS-pub#240](https://github.com/Vorski-Imagineering/METIS-pub/issues/240).
  Don't waste a turn re-discovering this — check the issue for status before assuming it's still true.
- **The live schema can change mid-session.** It's the authoritative source, not the docs in
  this repo — if a field the docs describe (e.g. `journeys` on a class) seems to be missing,
  re-fetch `/api/v1/openapi.json` before concluding it doesn't exist.
- **Adding a Person to two holons at once:** `POST /people`'s `membership` field only accepts
  one holon. Create the Person with the primary membership + note, then call
  `POST /holons/{other_holon_id}/memberships:bulk-add` for the same `person_id` to add the second.
- **Checking whether a journey is valid on a given holon, without side effects:** call
  `memberships:bulk-add` with a bogus `person_id` (e.g. `999999999`). The response
  distinguishes cleanly: `"Journey is not allowed on this Holon"` (journey invalid there) vs
  `"Person not found"` (journey is fine, your real person_id will work). Much faster than
  guessing and creating throwaway records.
- **Moving a person to a different Journey on the same Holon** (e.g. "move everyone on
  Journey A to Journey B"): `memberships:bulk-add` only *creates* new memberships — it is
  not a move and leaves the old membership in place. The actual move is
  `POST /memberships/{membership_id}/update` with `journey_slug` + `step_slug` set (mutually
  exclusive with `advance_step`). This reassigns the existing membership in place — no
  duplicate row, no separate delete step needed. `step_slug` must be an active step on the
  *target* journey (fetch via `GET /journeys/{slug}` to pick one); the call 400s if the person
  already has another membership on that target journey for the same holon.
- **`curl` vs Python for these calls:** use `curl`, not Python's `urllib`/`requests` with default
  headers — the site's Cloudflare WAF blocks the default Python User-Agent with a `403` whose
  body is an HTML/Cloudflare "error code: 1010" page, not a JSON API error. That 403 looks like
  a permission_denied response but isn't one; don't diagnose it as a permissions/scope problem
  before checking whether the same call works via `curl`.
