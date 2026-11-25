---
name: gathering-camp
description: >
  Use when creating a camp for a gathering in METIS, or updating an existing camp — its leader,
  its host organisation, its name/description/links/logo/fields, or moving it along its camp
  journey (publish, cancel). Trigger on: "create a camp", "new camp for <gathering>", "add a camp
  leader", "change the camp's organisation", "publish/cancel camp X", "update camp X".
---

# Gathering camps

A camp is a holon under a gathering (`local_gathering`). **Every camp needs both:**

| Part | How it's stored | Journey / step |
|---|---|---|
| **Leader** (a person) | membership of the person on the camp | `team` → `active` ("Member": public on the camp page, can manage the camp) |
| **Organisation** | relationship camp → org | `org-camp-leader` → `leading-camp` ("Camp Organiser" / "Leading Camp", public) |
| Camp ↔ gathering | relationship camp → gathering, made by `POST /camps` | the gathering's camp journey (below) |

This is the Mexico 2026 setup (`2026 México`, holon 224), the reference for how camps are done.

**API client:** `bash .claude/skills/gathering-camp/scripts/metis_api.sh GET|POST <path> [json]`.
It handles login from `.env`. Parse output with `json.loads(raw.decode('utf-8','replace'), strict=False)`.
Full API reference: `docs-pub/api/v1-PLAYBOOK.md`.

## Creating a camp

### 1. Ask for what's missing

Ask in one message for anything the user didn't give:
- **gathering** (resolve with `GET /holons?class=local_gathering&q=…`)
- **camp name** (+ optional description, website, source link)
- **leader**: name, plus email or LinkedIn URL if they may be new to METIS
- **organisation**: name, plus website if it may be new
- **starting step** of the camp journey (see step 2: tell them which steps are public)

### 2. Resolve everything (reads only)

- **Camp journey:** `GET /holons/{gathering}/journeys?object_kind=holon`. Use the gathering's
  own camp lifecycle: `mx-2026-camp` on Mexico 2026; `pt-2026-camps` ("Camp") on gatherings with
  the generic Local Gathering setup (all the 2027 ones). If it isn't clear which journey is the
  camp lifecycle, list them and ask. Read its steps with `GET /journeys/{slug}`: a step whose
  `config_flags` include `public-visible` **puts the camp on the public site**. Tell the user
  which steps those are before they choose.
- **Duplicate camp:** `GET /holons?class=camp&parent={gathering}&q={name}`. If it exists, switch to
  *Updating* below instead of creating.
- **Leader:** `GET /people?q={name}` (and `GET /search?q={email}&types=person` if you have an
  email). One clear match → use its id. Several → show them (name, description) and ask. None → it
  will be created in step 3.
- **Organisation:** `GET /holons?class=organisation&q={name}`. Same rule: one, ask, or create.

### 3. Dry run, then write

Show the user the plan: gathering, camp name, journey + step (public or not), leader (existing id
or "new person" with contact), organisation (existing id or "new org"), and the calls below. **Write
nothing until they say yes.** Then, in order:

1. **Camp:** `POST /camps` `{"parent_id", "name", "journey", "step", "description"?, "links"?}`.
   Omit `metis_class`: the gathering's class picks its camp class (e.g. `camp_mx2026`). `409` =
   a camp with that name/link already exists: stop and report the `existing_holon_ids`.
2. **Organisation, if new:** `POST /holons` `{"name", "links": {"website": …}}`. `409` → reuse
   `existing_holon_ids[0]` after telling the user.
3. **Leader:**
   - existing person → `POST /holons/{camp}/memberships:bulk-add`
     `{"journey":"team","items":[{"person_id":…,"step_slug":"active","note":"Camp leader"}]}`
   - new person → `POST /people` `{"name", "contact":{"email"|"linkedin":…},
     "membership":{"holon_id":camp,"journey":"team","step_slug":"active"}, "note":"Camp leader"}`.
     `409` = the email/LinkedIn belongs to `existing_person_ids`: use that person with bulk-add.
4. **Organisation link:** `POST /holons/{camp}/relationships:bulk-add`
   `{"journey":"org-camp-leader","items":[{"to_holon_id":org,"step_slug":"leading-camp","note":"Host organisation"}]}`.
   Camp Organiser is on the base `camp` class, so every camp class offers it.

Bulk-add results are per item: check each `outcome` (`created`, `already_present`, `error`), not
just the HTTP status.

### 4. Verify and report

`GET /holons/{camp}`, `/holons/{camp}/memberships`, `/holons/{camp}/relationships`. Report the camp
id, its journey step, leader and organisation, and the public page if it's on a public step:
`https://view.the-gathering.earth/<gathering-slug>/<camp-slug>/`.

## Updating a camp

Find it first (`GET /holons?class=camp&parent={gathering}&q=…`), show the current value, confirm
the change, write, then re-read to verify.

| Change | Call |
|---|---|
| Name, description, info fields | `POST /holons/{camp}/update` (partial) |
| Links | same call, but **`links` replaces the whole set**: read, merge, send all |
| Logo | `POST /holons/{camp}/logo`, multipart field `logo` (jpeg/png/gif/webp ≤5 MB) |
| Step on the camp journey (publish, cancel) | find the camp→gathering `relationship_id` in `/holons/{camp}/relationships`, then `POST /relationships/{id}/update` `{"step_slug", "note"}` |
| Add a leader | as step 3.3 above |
| Add an organisation | as step 3.4 above |
| Replace a leader or organisation | add the new one, then tell the user the old one must be removed in the web app: `team` has no active step to retire to, and `org-camp-leader` has only one step |

Cancelling = the journey's cancel step (`canceled` on `mx-2026-camp`, `cancelled` on
`pt-2026-camps`). It takes the camp and its experiences off the public site. There is no delete.

## Common mistakes

- **Using another leader journey.** Some Mexico camps also show `mx-2026-person-camp-leader`. New
  leaders go on `team`/`active`, never on both journeys.
- **Using `26-camp-lead` ("'26 Org Camp Lead") for the org.** Older camps have it, but the
  generic `camp` class doesn't offer it, so it's refused on 2027 camps. Use `org-camp-leader`.
- **Creating a person or org that already exists.** Always search first. Names aren't identity,
  so ask when unsure.
- **Sending only the new link** on update. That wipes the other links.
- **METIS autolinks `word.Word`** in descriptions: keep a space after each full stop.
