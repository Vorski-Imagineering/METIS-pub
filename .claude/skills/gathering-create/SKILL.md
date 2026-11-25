---
name: gathering-create
description: >
  Use when creating a new local gathering (an edition of The Gathering) in METIS, e.g. "create
  the Holon MX 2027", "new gathering for 2027 Iceland", "set up <country> <year> so we can add
  leads", or when copying an earlier edition's details and team to a new year.
---

# Creating a local gathering

A local gathering is a holon under **The Gathering (holon 1)**. Create it through the API with
`POST /holons`. **Don't use the web form** (`/app/gathering/gathering/create/`): it posts a fixed
`local_gathering` class, so the new gathering misses the shared journeys of its year's class. A
holon's class can't be changed afterwards.

**API client:** `bash .claude/skills/gathering-camp/scripts/metis_api.sh GET|POST <path> [json]`
(logs in from `.env`). Call it directly or wrap it in a shell function. In zsh, a variable
such as `A="bash … GET"; $A /holons` fails, because zsh doesn't split words. Parse with `json.loads(raw.decode('utf-8','replace'), strict=False)`.
Full reference: `docs-pub/api/v1-PLAYBOOK.md`. Camps under the gathering: `gathering-camp` skill.

## 1. Ask for what's missing (one message)

- **Name**: the convention is `<year> <Country>`, e.g. `2027 México`. If the request uses another
  name ("Holon MX 2027"), say which you'll use.
- **Earlier edition to copy from**, if any (e.g. 2026 México, holon 224).
- **Timezone** (required, IANA `Area/City`), **place**, **dates**, if known.
- **Local team**: who manages it.

## 2. Read (no writes)

| What | Call | Look for |
|---|---|---|
| Which class | `GET /holons/1/creatable` | The year's shared class, e.g. **`the-gathering-2027`** ("Gathering 2027"). Use it over plain `local_gathering` and over per-country classes (`the-gathering-mexico-2026`). Note its `journeys`/`default_step` and which `info_fields` are `required`. |
| What the class offers | `GET /classes/holon/{class}` | `journeys`: the shared pipeline (`2027-person`), Outreach, TG Team, Camp, etc. (`steps` come back empty here: use `GET /journeys/{slug}` for step slugs) |
| Duplicate | `GET /holons?class=local_gathering&q=<country>` and `q=<year>` | Subclasses are included. An existing edition for that year means stop and ask. |
| Earlier edition | `GET /holons/{old}` | `info_fields`, `links`, `logo_url`, `description` |
| Team | `GET /holons/{old}/memberships?journey=tg-local-team-2026` | The person ids **and their current step** (`commit`, `active`, `retired`) |

If no class for the year exists, ask the user. Don't fall back to `local_gathering` without
asking: picking a year's class is an admin decision (`metis-admin`).

### What to copy from an earlier edition

Copy only values that exist. If the earlier edition has few or none, tell the user and send just
what they gave you. Don't pad the request. The earlier edition may be on another class (e.g.
plain `local_gathering`): the new one still uses the year's class.


| Copy | Don't copy |
|---|---|
| `timezone`, `tagline`, `place` if confirmed | `start_date`, `end_date`, `tickets` (they belong to that year) |
| Lasting links: email, website, YouTube, LinkedIn, X, Instagram | Event-specific links: a Facebook **event**, a year-named Telegram group |
| Logo | `description` if it holds that year's prices or programme |
| TG Team members, on the step they hold now. Promoting `commit` → `active` is the user's call. | Camps, experiences, org relationships, the old year's leads |

## 3. Dry run, then write

Show the exact request bodies below, plus the names of the people being added. **Write nothing
until the user says yes.**

1. **Create:**
   ```json
   POST /holons
   {"metis_class": "the-gathering-2027", "parent_id": 1, "name": "2027 México",
    "journey": "gathering-public-site", "step": "not-public",
    "info_fields": {"timezone": "America/Merida", "tagline": "…"},
    "links": {"email": "…", "website": "…"}}
   ```
   `not-public` keeps it off the public site. Response: `{"holon": {...}}`. Note `holon.id`.
   - **`409` with `match_field`** means a link value (often the email) already belongs to the
     earlier edition. Copied lasting links always hit this. Tell the user which links are shared.
     On their yes, resend with `"allow_duplicate": true`. A `409` on the **name** is a real
     duplicate, so stop.
2. **Logo**: logos are per-country branding. Reuse one only from the **same country's** earlier
   edition. Otherwise ask the user for a file, or skip it. Upload is multipart, so it doesn't go
   through `metis_api.sh`. Download the old one into the
   scratchpad, then upload it:
   ```bash
   curl -s -A "Mozilla/5.0" -o "$S/logo.png" "https://app.the-gathering.earth<logo_url>"
   T=$(cat "${TMPDIR:-/tmp}/metis_token_$(id -u)")   # cached by metis_api.sh
   curl -s -A "Mozilla/5.0 (Macintosh) Chrome/130" -H "Authorization: Bearer $T" \
     -F "logo=@$S/logo.png;type=image/png" https://app.the-gathering.earth/api/v1/holons/{id}/logo
   ```
3. **Team:**
   ```json
   POST /holons/{id}/memberships:bulk-add
   {"journey": "tg-local-team-2026",
    "items": [{"person_id": 3, "step_slug": "active", "note": "Local team, <name>"}]}
   ```
   Check each item's `outcome` (`created`, `already_present`, `error`). TG Team `active` gives
   them team-member and manage-people rights, so they can add leads and people themselves.

## 4. Verify and report

- `GET /holons/{id}`: check `type`, `parent_id`, `info_fields`, `links`, `logo_url`, and
  `lifecycle.step_slug` = `not-public`.
- `GET /holons/{id}/journeys?object_kind=person`: the year's pipeline (`2027-person`) shows
  `offered_by: "class"`.
- `GET /holons/{id}/memberships`: the team is active.

Report the id, the web app link `https://app.the-gathering.earth/<slug>/`, and where leads go:
people on the year's pipeline journey (`2027-person`: To invite → To contact → In conversation →
Signed up) or Outreach; organisations on Org Outreach.

## Common mistakes

- **Using the web form, or `metis_class: "local_gathering"`.** The gathering misses the year's
  shared journeys, and its class can't be fixed later.
- **Offering journeys per holon** (`journey_ids` on update) instead of using the year's class.
  That's how earlier 2027 gatherings drifted onto `cz-2026`, `pk-2027` and others.
- **Blindly setting `allow_duplicate`.** It's only for shared lasting links the user has seen.
  Never use it to get past a name match.
- **Copying the old year's dates, tickets or price-list description.**
