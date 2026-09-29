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

## General notes

- Credentials live in `.env` (`API_LOGIN_SECRET`, `METIS_EMAIL`, `METIS_PASSWORD`); the session token lasts 24 hours.
- The API is read-mostly. Besides the update endpoints (`POST /relationships/{id}/update`,
  `POST /memberships/{id}/update`, `POST /holons/{id}/update` — each requires a non-empty
  `note` where applicable), it can also create records: `POST /people` (a Person, optionally
  with one initial Membership + note), `POST /holons` (a top-level Organisation only),
  `POST /camps` (a Camp under a gathering) and `POST /experiences` (an Experience holon, but
  only as a child of an existing Camp/Gathering). See `v1-PLAYBOOK.md` for the per-kind id semantics.
- **Holon class for a "gathering":** there is no `gathering` class — `GET /holons?class=...`
  rejects it with a `validation_error` listing valid slugs. A top-level gathering event (e.g.
  "2026 USA California") is class `local_gathering`. Use `GET /holons?class=local_gathering`
  (optionally with `q=...`) to find one; `GET /classes?object_kind=holon` lists all valid slugs
  if a class guess like this one gets rejected again in the future.
- **Creating holons: Organisations, Camps and Experiences.** A Local Gathering or any other
  class still needs a human in the METIS web app. Before telling the user a type can't be
  created, re-check the `POST` paths in the live `/api/v1/openapi.json` — this has changed twice.
  - `POST /holons` creates a top-level **Organisation** (`name` required). A name or link that
    already exists returns `409` naming the existing ids and writes nothing (#240).
  - `POST /camps` creates a **Camp** under `parent_id`. **`journey` is required at runtime even
    though the schema doesn't mark it** — for a 2026 gathering it's `pt-2026-camps` (step
    `selling` for a published camp; `GET /holons/{parent}/journeys?object_kind=holon` lists what's
    offered). Same name or same link under the same parent → `409` (#488).
  - `POST /experiences` creates an **Experience** under an existing Camp/Gathering. It takes
    `links` but does **not** refuse duplicates: look up first.
- **Finding a holon by an external source:** `GET /holons?class=…&parent=…&link=<url>&link_key=source`
  matches a link value exactly (the `#fragment` counts). Store the source URL in `links.source`
  when creating. `links` on `/holons/{id}/update` is a **full replace** — merge into the existing
  links, or you delete ones a human added.
- **Logos:** `POST /holons/{id}/logo`, multipart file field `logo` (jpeg/png/gif/webp, ≤5 MB).
  No URL form: download the image first.
- **Removing a camp or experience from the public site:** move its relationship to the
  `cancelled` step (`POST /relationships/{id}/update` with `step_slug` + `note`). Both the
  `pt-2026-camps` (Camp) and `experience-programme` journeys have one, not public. Moving back to
  a public step restores it. There is no delete.
- **Host orgs of a camp:** relationship camp → org on `26-camp-lead`, step `active`, via
  `POST /holons/{camp_id}/relationships:bulk-add` (safe to re-run: an existing pair returns
  `already_present`).
- **METIS autolinks `word.Word` in descriptions** (e.g. "world.In" became a link to
  `http://world.In`). Put a space after sentence ends in text you send, and compare
  descriptions as text, not HTML, since METIS adds markup on save.
- **The journey editor's Add Step form sends nothing while the browser tab is in the
  background** (`document.hidden`; htmx logs "Transition was aborted") but still clears the
  input, so it looks like it worked. Verify with `GET /journeys/{slug}` afterwards.
- **Listing a holon's children:** `GET /holons?parent=<id>` alone 400s ("At least one of q or
  class must be provided") — add a class, e.g. `class=camp&parent=2` or `class=holon&parent=2`
  for every child. `limit` max is 100 (422 above that).
- **Relationship list shape:** `GET /holons/{id}/relationships` items use `relationship_id`,
  `from_holon`, `to_holon`, `journey_name`, `step_title` (not `source`/`target`/`journey_slug`).
  Org↔camp links are relationships between the two holons, not memberships.
- **`relationships:bulk-add` → `journey_not_offered`:** holon journeys are offered by *class*
  (`GET /holons/{id}/journeys?object_kind=holon` shows `offered_by`). Holons of the same
  gathering can carry different classes (e.g. 2022 Portugal camps are split between
  `camp_pt_legacy` and `camp`), so a journey used on sibling links may be refused. The API
  can't change a holon's class — that's a web-app fix. Don't substitute another journey, and
  don't use `journey_ids` on `/holons/{id}/update` as a workaround: it's a full replace, and
  journey PKs aren't exposed.
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
- **Parsing responses in Python:** list responses (e.g. `GET /holons`) can contain invalid
  UTF-8 bytes and raw control characters inside strings, so a plain `json.load` fails with
  `UnicodeDecodeError` or `Invalid control character`. Decode with
  `json.loads(raw.decode('utf-8', 'replace'), strict=False)`. Save `curl` output with `-o file`
  rather than `r=$(curl …); echo "$r" | python3`, since the shell round-trip mangles it too.
  A working client (login, get/post with a browser User-Agent) is `Metis` in
  `automation/sola-import/sola_scan.py`.
- **"People for outreach" means the `To Contact` step only, not the whole Outreach journey.**
  When the user asks how many people are "for outreach" / "awaiting outreach" on a holon
  without naming a step, filter `GET /holons/{holon_id}/memberships` results (or count) down
  to `step_slug=to_contact` on the `person-outreach` journey. Other steps on that journey
  (`Personal Message`, `Invited`, `In Conversation`, etc.) are people already in progress, not
  waiting to be contacted — including them inflates the count and the "first N" list with
  people who shouldn't be messaged again.
