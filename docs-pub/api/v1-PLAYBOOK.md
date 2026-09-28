# METIS API Playbook — `/api/v1/`

Authoritative reference for `/api/v1/`, the open API for external systems
integrating with METIS. If you are building against METIS from outside — an AI
client, a data integration, a partner system — this is the surface you want, and
this file is where its contracts live.

**Not the same surface as `/api/`** — despite the paths, `/api/v1/` is not a
versioned edition of `/api/`. They are independent, with different authentication
and error shapes. See [`PLAYBOOK.md`](PLAYBOOK.md) for `/api/`, and
[`API.md`](API.md) for the full surface index if you're not sure which one you want.

**Live schema:** `https://app.the-gathering.earth/api/v1/openapi.json`
**Swagger UI:** `https://app.the-gathering.earth/api/v1/docs`

---

## What this API is

METIS models a network of people and the groups, events and communities they belong
to. This API exposes that model directly: holons (the groups, events and other
entities), the people in them, the memberships that place a person in a holon at a
point in a journey, and the relationships between holons — plus search and the class
and journey definitions that give those records their meaning.

It is read-mostly, and every call is authenticated as a real METIS account and
attributed to the Person behind it, so an integration's writes stay auditable to a
human rather than to a shared key. The write endpoints are
`POST /api/v1/relationships/{relationship_id}/update`,
`POST /api/v1/memberships/{membership_id}/update`, and
`POST /api/v1/holons/{holon_id}/update`. Generic bounded Membership creation is
available at `POST /api/v1/holons/{holon_id}/memberships:bulk-add`, bounded
HolonRelationship creation at
`POST /api/v1/holons/{holon_id}/relationships:bulk-add`, and
`POST /api/v1/people` creates a Person while `POST /api/v1/holons` creates an
Organisation.

App-owned parts of this surface are documented by their owning app:
[`outreach-PLAYBOOK.md`](outreach-PLAYBOOK.md) for `/api/v1/outreach/*`.

---

## Authentication

The API uses a two-step auth flow. Standard `API_TOKEN` bearer tokens and
browser session cookies do **not** authenticate `/api/v1/` endpoints.

### Login flow

1. Client calls `POST /api/v1/auth/login` with:
   - `X-Metis-Api-Key: <API_LOGIN_SECRET>` header
   - JSON body: `{"email": "...", "password": "..."}`
2. Server returns a 24-hour bearer token: `metis_agentic_<token_id>_<secret>`
3. Subsequent calls send `Authorization: Bearer <token>`
4. Logout: `POST /api/v1/auth/logout` revokes the token server-side

**Token format:** `metis_agentic_<session_key>_<secret>`
- `session_key`: 32-char lowercase-alphanumeric key
- `secret`: 43-char base64url random value (only a hash is stored server-side)

**Invalidation triggers:**
- Explicit logout
- Token expiry (24 hours)
- Password change
- Account deactivation

### Settings

| Setting | Description |
|---------|-------------|
| `API_LOGIN_SECRET` | Shared login gate secret. Required on every login call. |

**Secret rotation procedure:**
1. Set the new `API_LOGIN_SECRET` on the server and restart.
2. Update all clients to send the new value in `X-Metis-Api-Key`.
3. Existing tokens remain valid until they expire or are logged out.

---

## Error shape

All `/api/v1/` error responses use:

```json
{"code": "unauthenticated", "message": "Authentication required.", "retryable": false}
```

| code               | HTTP status | retryable |
|--------------------|-------------|-----------|
| `unauthenticated`  | 401         | false     |
| `permission_denied`| 403         | false     |
| `not_found`        | 404         | false     |
| `validation_error` | 400         | false     |
| `server_error`     | 500         | true      |

**Exception — request validation (`422`):** a missing required param or out-of-range
value returns HTTP `422` with a different shape:

```json
{"detail": [{"type": "...", "loc": ["query", "limit"], "msg": "..."}]}
```

Treat both `400` and `422` as non-retryable bad input.

---

## Access model

Most directory reads remain authentication-level, with an object-level privacy
exception for Holon classes explicitly configured as private:

- **Reads:** a valid token has shared-directory Person access. Ordinary Holons
  remain directory-readable. A private-class Holon, its Membership/workflow
  state, related notes, and relationships are visible only to a global editor
  or a caller who holds **view private** on that Holon or an ancestor of it. Direct reads of an
  inaccessible private Holon return `404`, and collection/worklist endpoints
  filter it out.
- **Writes** (`POST /relationships/{id}/update`, `POST /memberships/{id}/update`,
  `POST /holons/{id}/update`) **are** object-scoped: the caller must be able to
  edit the relevant holon — `can_update_relationship` (either side of the
  relationship), `can_update_membership` (the membership's holon), or
  `can_edit_holon` (the holon itself) — otherwise the call returns
  `403 permission_denied`. `POST /holons/{id}/update` additionally requires
  global edit access to set `journey_ids`.
- **Creating a Person** (`POST /people`) requires **global edit access** — the
  broadest gate on this API, and one most tokens do not carry. Adding to the
  shared directory is treated as a wider act than editing one record in it,
  because everyone else sees the result.

Do not use ordinary Person fields for private address-book data: Person
projections remain shared-directory data even when one of their Memberships is
on a private Holon.

---

## Endpoints

### `POST /api/v1/people` — auth: tokenBearer

Create a Person, optionally with an initial Membership and a note. Requires global
edit access.

Duplicates are **refused, never merged**: if `contact.email` or `contact.linkedin`
matches an existing Person, the call returns `409` with `match_field`,
`match_value`, and `existing_person_ids`, and writes nothing — the caller decides
whether to reuse that Person, correct the input, or merge in the web app. Names are
not treated as identity, so two people may share one.

`membership` and `note` are independent and optional. With both, the note lands on
the membership and so appears on the person's and the holon's feeds; with a note
alone it attaches to the Person. The whole call is one transaction — an invalid
membership means no Person is created either.

See the live schema for the full request and response shapes.

---

### `POST /api/v1/auth/login` — auth: X-Metis-Api-Key + credentials

Exchange METIS email/password for a 24-hour bearer token. The account must have
a linked METIS Person or login returns 403.

**Request body:**
```json
{"email": "user@example.com", "password": "..."}
```

**Response 200:**
```json
{
  "token": "metis_agentic_<id>_<secret>",
  "token_type": "Bearer",
  "expires_at": "2026-06-18T12:00:00+00:00",
  "expires_in_seconds": 86400,
  "person": {"id": 42, "name": "Alice", "description": "...", "photo_url": null, "actor_kind": "person", "contact": {}}
}
```

---

### `POST /api/v1/auth/logout` — auth: tokenBearer

Revoke the current read token immediately.

**Response 200:** `{"revoked": true}`

---

### `GET /api/v1/auth/whoami` — auth: tokenBearer

Return the logged-in METIS Person for the current token.

**Response 200:**
```json
{"authenticated": true, "person": {"id": 42, "name": "Alice", ...}}
```

---

### `GET /api/v1/search` — auth: tokenBearer

Search public Person and Holon fields together.

| Param | In | Required | Default | Description |
|---|---|---|---|---|
| `q` | query | yes | — | Search query (min 2 chars) |
| `types` | query | no | `person,holon` | Comma-separated subset |
| `limit_per_type` | query | no | 20 | Max 50 per type |

Returns ranked results (name/channel hits ranked above description-only hits).

---

### `GET /api/v1/people` — auth: tokenBearer

Search people by name substring.

| Param | In | Required | Default | Description |
|---|---|---|---|---|
| `q` | query | yes | — | Case-insensitive name substring |
| `sort` | query | no | `name` | `name`, `latest` (created desc), or `updated` (updated desc); all deterministic with a PK tie-breaker |
| `created_after` / `updated_after` | query | no | — | ISO-8601 timestamps; strictly-after filters for polling / incremental sync |
| `limit` | query | no | 100 | Max 100 |
| `offset` | query | no | 0 | Page offset — increment by `limit` until `has_more` is `false` |

**Response 200:** `{query, limit, offset, count, has_more, items: [PersonPublic]}` —
`PersonPublic` includes `created_at` and `updated_at`. Invalid sort values return a
validation error rather than being ignored.

> **These are the Person record's timestamps, not membership timestamps.** `created_at`
> is when the contact entered METIS, which is not when they joined any particular holon.
> A `Membership` stores no creation timestamp at all, so join order is not retrievable
> from this API. Do not reconstruct it by scraping `"Membership created: …"` notes: that
> body is only a *default*, replaced whenever the creating caller supplied its own note,
> so the reconstruction is silently incomplete.

---

### `GET /api/v1/people/{person_id}` — auth: tokenBearer

Retrieve one person by integer PK. Returns 404 if not found.

---

### `POST /api/v1/holons` — auth: tokenBearer

Create a top-level **Organisation** — the same record the web app's New organisation
page creates. Requires global edit access. There is no `class` field: other holon
types have their own create flows, and this endpoint creates organisations only.

Duplicates are **refused, never merged**: if an organisation already carries the same
name (case-insensitively) or the same value for any link key you sent, the call
returns `409` with `match_field`, `match_value`, and `existing_holon_ids`, and writes
nothing. Every key in `links` is checked, not a fixed list — so sending a `website`
you are unsure about is how you find out it is taken.

A name that would slug to a word reserved for site navigation (`org`, `public`,
`welcome`, `brand`, …) returns `400`. Such a holon's own page would be permanently
shadowed by that route, so the name has to change rather than the slug.

Creation records a "Holon created" note on the new organisation, marked `— via API`
like every other note this API writes. To add people to it, use
`POST /api/v1/holons/{holon_id}/memberships:bulk-add` with a journey from
`GET /api/v1/holons/{holon_id}/journeys`.

See the live schema for the full request and response shapes.

---

### `GET /api/v1/holons` — auth: tokenBearer

Generic holon discovery. At least one of `q` or `class` must be provided.

| Param | In | Required | Description |
|---|---|---|---|
| `q` | query | no | Case-insensitive name **or description** substring |
| `class` | query | no | Active holon class slug, e.g. `organisation`, `camp`, `experience`. Matches that class and its whole subtree (e.g. `class=camp` also reaches `camp_pt2026`, `camp_mx2026`, etc.). |
| `parent` | query | no | Filter by parent Holon PK (e.g. the owning Camp for experiences) |
| `sort` | query | no | `name` (default), `latest` (created desc), or `updated` (updated desc); all deterministic with a PK tie-breaker |
| `created_after` / `updated_after` | query | no | ISO-8601 timestamps; strictly-after filters for polling / incremental sync |
| `limit` | query | no | Default 100, max 100 |
| `offset` | query | no | Page offset — increment by `limit` until `has_more` is `false` |

**Response 200:** `{query, class, parent, limit, offset, count, has_more, items: [HolonPublic]}` —
`HolonPublic` now includes `created_at` and `updated_at`. Invalid class slugs or sort values
return a validation error rather than being ignored. The live schema at `/api/v1/openapi.json`
remains authoritative.

---

### `GET /api/v1/holons/{holon_id}` — auth: tokenBearer

Retrieve one holon by integer PK. Returns 404 if not found.

---

### `GET /api/v1/holons/by-slug/{slug}` — auth: tokenBearer

Retrieve one holon by slug. Returns 404 if not found.

---

### `POST /api/v1/holons/{holon_id}/update` — auth: tokenBearer

Edit a holon's core fields, locations/spheres, per-class custom fields
(`info_field_groups`), and/or journey assignments. Partial update: only fields
present in the request body are touched.

| Param | In | Required | Description |
|---|---|---|---|
| `holon_id` | path | yes | Holon PK |

**Request body (all fields optional):**

| Field | Type | Notes |
|---|---|---|
| `name` | string | Rejected if the holon's type marks `name` read-only (e.g. `domain`, `event`), or if empty after trimming. |
| `description` | string | Sanitized as rich-text HTML (same allowlist as the web editor). |
| `links` | object (string→string) | Full replace. Empty/whitespace-only values are dropped. |
| `locations` | array of strings | ISO country codes. 400 if any code is invalid. |
| `spheres` | array of integers | Sphere PKs. Must be active spheres. 400 if any id is invalid or inactive. |
| `info_fields` | object (string→any) | Keyed by an `info_field_groups` field `key` for the holon's class (discoverable via `GET /classes/holon/{type}`, inherited fields included). `POST /experiences` takes the same `info_fields`. 400 on an unknown key, a `slideshow`-type key, or a malformed `select`/`video` value. A `slideshow` field's photos are files rather than values — add them with [`…/slideshows/{field_key}/photos:add`](#post-apiv1holonsholon_idslideshowsfield_keyphotosadd--auth-tokenbearer). A `select`-type field is **multi-value**: its value must be a JSON array of strings (e.g. `["Dancing and music", "Inner Development"]`), even to set a single tag — there is no single-value select. Any submitted value not in the field's `options` list is silently dropped rather than rejected, so double-check spelling against `GET /classes`. |
| `journey_ids` | array of integers | Full replace of the holon's Journey assignments. Requires global edit access (see Permissions). 400 if any id is invalid. |

**Behavior:**
- `locations`/`spheres`/`info_fields` all live in the holon's `infos` JSON column and are merged into one update.
- The `changes` object in the response reports only fields that actually changed, `{old, new}` per field.

**Response 200:** `{holon: HolonPublic, changes}`.

**Permissions:** the caller must be able to edit the holon (`can_edit_holon`) for
any field. `journey_ids` additionally requires global edit access — journeys are
a class-catalog concern, not a per-holon one, matching the web UI's stricter
gate on the Journeys field.

**Errors:** `400` (validation failures per field above), `403` permission
denied, `404` not found.

---

### `GET /api/v1/holons/{holon_id}/slideshows/{field_key}` — auth: tokenBearer

Read a holon's slideshow photos, in display order.

A **slideshow** is an info field whose value is images rather than a JSON value.
You recognise one in `GET /api/v1/classes`: its field definition carries
`"type": "slideshow"`. Because the photos are files, they are not set through
`info_fields` on `…/update` — these four operations are where they are managed.

| Param | In | Required | Description |
|---|---|---|---|
| `holon_id` | path | yes | Holon PK |
| `field_key` | path | yes | The info field's `key` |

**Response 200:** `{holon_id, field_key, label, max_photos_per_request, allowed, count, photos}`.
Each photo is `{id, url, position, content_type, size_bytes, width, height, original_name}`.

- `id` is the handle `:reorder` and `/remove` take. `url` is derived from storage
  on every read and is **not** a durable identifier — do not store it as one.
- `position` is zero-based and dense: removing a photo renumbers the rest.
- `allowed` is the same sentence the web app shows under its file picker, so a
  client never has to restate the limits.

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "$BASE/api/v1/holons/1259/slideshows/photos"
```

**Permissions.** All four operations — including this read — require the same
rights as `POST /holons/{holon_id}/update`: the caller must be able to edit the
holon. A read-only caller can still see the images through
`GET /api/v1/holons/{holon_id}` → `info_fields[field_key]`, which returns the
URLs but not the photo `id`s.

**Errors:** `403` permission denied; `404` when the holon does not exist, when
`field_key` is not a slideshow field on its class, **or when the caller cannot
view the holon at all** — a holon you may not see is indistinguishable from one
that does not exist.

---

### `POST /api/v1/holons/{holon_id}/slideshows/{field_key}/photos:add` — auth: tokenBearer

Add one or more photos to the end of a slideshow. `multipart/form-data`; repeat
the `photos` field once per file.

| Param | In | Required | Description |
|---|---|---|---|
| `holon_id` | path | yes | Holon PK |
| `field_key` | path | yes | The slideshow field's `key` |
| `photos` | form-data | yes | 1–10 image files |

**All or nothing.** Every file is checked before any is stored, so if one file
is refused nothing is written — no rows and no uploaded bytes. Fix the offending
file and send the batch again.

**Limits.** Each file must be a GIF, JPEG, PNG or WEBP of at most 5 MB — the
`allowed` string in the response is the authoritative phrasing. At most **10
files per request**, because the whole multipart body has to fit inside the
server's upload limit; `max_photos_per_request` in the response carries the
number so you need not hardcode it. Send more photos as further requests; each
appends after the ones already there, in the order sent.

```bash
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -F photos=@camp-01.jpg \
  -F photos=@camp-02.jpg \
  -F photos=@camp-03.jpg \
  "$BASE/api/v1/holons/1259/slideshows/photos/photos:add"
```

**Response 200:** the whole slideshow after the add, so you never need to re-read it.

**Errors:** `400` with the refusal's own message — which names what the file
actually is and what the field accepts — or when more files than the cap are
sent. `422` when the `photos` field is missing altogether (the field is
required, so this is caught before the request reaches the endpoint). `403`
permission denied; `404` as above.

---

### `POST /api/v1/holons/{holon_id}/slideshows/{field_key}/photos:reorder` — auth: tokenBearer

Set the display order.

**Request body:** `{"photo_ids": ["<id>", "<id>", ...]}` — **every** photo id
currently in the slideshow, each exactly once, in the order wanted. A partial
list, a duplicate, a missing id, or an id from another field is refused with
`400` and nothing moves. The complete list is required because a partial one
would have to invent a rule for where the photos it omits go.

```bash
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"photo_ids":["3f2a…","9b71…","c04e…"]}' \
  "$BASE/api/v1/holons/1259/slideshows/photos/photos:reorder"
```

**Response 200:** the whole slideshow in its new order.

---

### `POST /api/v1/holons/{holon_id}/slideshows/{field_key}/photos/{photo_id}/remove` — auth: tokenBearer

Remove one photo and renumber the rest.

| Param | In | Required | Description |
|---|---|---|---|
| `photo_id` | path | yes | The photo's `id` from a read or an add |

An id that is not in **this** slideshow is a `404`, including an id belonging to
another of the same holon's fields — the scoping is deliberate.

```bash
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  "$BASE/api/v1/holons/1259/slideshows/photos/photos/3f2a…/remove"
```

**Response 200:** the whole slideshow after the removal.

---

### `GET /api/v1/classes` — auth: tokenBearer

Discover active object classes and API-safe capability config. Use `object_kind=holon`
to list Holon classes. Existing Holon payloads still return the class slug as
`type`; they do not embed class config.

Only classes with `is_active: true` are listed here. A class can be retired
(`is_active: false`) while objects already assigned to it remain on it — their
`type` will still show the retired slug, but that slug will not appear in this
list and `GET /classes/{object_kind}/{slug}` will 404 for it. Treat an unknown
`type` as "retired class", not an error.

`config` is the class's configuration with inherited keys filled in, limited to
API-safe keys (the live schema's `MetisClassPublic.config` names them). A key the
class does not set itself comes from the nearest ancestor class that sets it.
Keys are not merged: a key the class does set, even to an empty list, replaces
every ancestor's value. That is the rule saving applies to `info_field_groups`.

For holon classes, `config.info_field_groups` is the schema of custom per-class
fields (grouped, each with `key`/`type`/`label`/`options`/etc.) that `info_fields`
accepts, keyed by `key`, on `POST /holons`, `POST /holons/{holon_id}/update` and
`POST /experiences` for a holon of that class. A holon's class is its `type`, so
`GET /classes/holon/{type}` lists the fields that holon takes.

`journeys` is the class's effective journey catalog (own plus inherited, in
catalog order) — what every holon of the class offers, but not the whole offer
for any one holon: a journey can also be assigned to a single holon. For what a
given holon accepts, call `GET /holons/{holon_id}/journeys`. Each entry is a
`JourneyListItem` (see `GET /journeys` below); use `GET /journeys/{slug}` for a
journey's steps.

| Param | In | Required | Description |
|---|---|---|---|
| `object_kind` | query | no | Optional class scope, e.g. `holon` |

**Response 200:** `[MetisClassPublic]`

```json
{
  "object_kind": "holon",
  "slug": "event",
  "label": "Event",
  "plural_label": "Events",
  "description": "",
  "sort_order": 30,
  "is_system": true,
  "is_active": true,
  "icon_url": null,
  "config": {"css_class": "holon-type-event", "hasAdditionalFields": true},
  "journeys": [{"slug": "sponsorship", "name": "Sponsorship", "object_kind": "holon", "...": "..."}]
}
```

### `GET /api/v1/classes/{object_kind}/{slug}` — auth: tokenBearer

Retrieve one active object class. Returns 404 if not found or inactive.

---

### `GET /api/v1/journeys` — auth: tokenBearer

List every Journey with aggregate usage counts, for auditing the journey
catalog (e.g. spotting unused or redundant journeys). Each item reports
`step_count` and a `usage` object — aggregate totals only, not the underlying
rows.

Read **`usage.total`** for "is this journey in use": it counts every record
running the journey, so it stays correct as record types are added. The
per-type counts (`membership_count`, `relationship_count`,
`conversation_count`, `janussession_count`) are broken out alongside it. `holon_direct_count` is
**not** part of `total` — a holon attached to a journey is offering it in its
catalog, not running it.

To inspect the actual records, use
`GET /people/{person_id}/memberships`, `GET /holons/{holon_id}/memberships`,
or `GET /holons/{holon_id}/relationships`.

| Param | In | Required | Description |
|---|---|---|---|
| `metis_app` | query | no | Filter by owning MetisApp slug |
| `object_kind` | query | no | Filter by `applies_to` object kind, e.g. `holon` |
| `applies_to` | query | no | Filter by `applies_to` MetisClass slug |
| `is_conversation` | query | no | `true`/`false` — conversation vs. non-conversation journeys |
| `q` | query | no | Case-insensitive substring match on name or slug |
| `limit` | query | no | Default 50, max 200 |
| `offset` | query | no | Default 0 |

**Response 200:** `{count, limit, offset, has_more, items: [JourneyListItem]}`

```json
{
  "slug": "sponsorship",
  "name": "Sponsorship",
  "description": "",
  "metis_app_slug": "metis",
  "applies_to_slug": "camp",
  "applies_to_label": "Camp",
  "object_kind": "holon",
  "is_conversation": false,
  "public_visible": false,
  "config_flags": [{"key": "public-visible", "value": false, "is_set": false}],
  "step_count": 3,
  "usage": {
    "holon_direct_count": 1,
    "membership_count": 0,
    "relationship_count": 4,
    "conversation_count": 0,
    "janussession_count": 0,
    "total": 4
  }
}
```

### `GET /api/v1/journeys/{slug}` — auth: tokenBearer

Retrieve one journey, including every step (ordered, archived steps included)
with per-step `usage` counts and their `total` — the signal for spotting
orphaned or stale steps. Returns 404 if not found.

**Response 200:** `JourneyListItem` fields plus `steps: [JourneyStepItem]`,
each step shaped as:

```json
{
  "slug": "proposal",
  "order": 1,
  "title": "Proposal",
  "goal": "",
  "success_criteria": "",
  "starter_message": "",
  "is_archived": false,
  "config_flags": [],
  "usage": {
    "membership_count": 0,
    "relationship_count": 1,
    "conversation_count": 0,
    "janussession_count": 0,
    "total": 1
  }
}
```

---

### `GET /api/v1/journeys/{slug}/memberships` — auth: tokenBearer

Every Membership on this journey, across every holon it appears on. This is the
drill-down from the `usage.membership_count` above: the count says a journey is
in use, and this says by whom and where. It is the only way to reach those rows
when no holon class offers the journey any more, since there is then no holon to
ask `GET /holons/{holon_id}/memberships` about.

| Field | In | Type | Notes |
|---|---|---|---|
| `slug` | path | string | Journey slug. |
| `limit` | query | integer | Page size, 1–200. Default 50. |
| `offset` | query | integer | Zero-based offset of the first item. |
| `q` | query | string | Person name, description, or contact substring. |
| `step_slug` | query | string | Exact current step slug. |
| `follow_up` | query | string | `overdue`, `today`, `future`, or `none`. |
| `responsible_person_id` | query | integer | Person PK of the responsible person. |
| `sort` | query | string | `name` (default), `-name`, `follow_up_after`, `-follow_up_after`, `person_created`, `-person_created`. |

Filters combine with AND.

**Response 200:** `{count, limit, offset, has_more, items}`, each item:

```json
{
  "membership_id": 4021,
  "person": {"id": 88, "name": "Ada Lovelace", "...": "..."},
  "holon": {"id": 14, "name": "Analytical Engines Ltd", "...": "..."},
  "step_title": "Proposal",
  "step_slug": "proposal",
  "follow_up_after": "2026-10-01",
  "responsible_person": null
}
```

Unlike the holon- and person-scoped membership listings, each item names **both**
the person and the holon: the journey is what is fixed here, so neither side is
implied.

`count` is the size of *this page*, not a total — page with `offset` until
`has_more` is false to get the whole set. Do not compare `count` against
`usage.membership_count`: on any journey with more memberships than `limit`
(default 50) they differ for the ordinary reason that there are more pages.

**Permissions:** memberships on holons you cannot view are filtered out, so even
the full paged-through set can be smaller than `usage.membership_count`, which is
not permission-filtered.

**Errors:** `400` (unknown `sort` or `follow_up`), `404` unknown journey.

---

### `GET /api/v1/journeys/{slug}/relationships` — auth: tokenBearer

Every HolonRelationship on this journey — the same drill-down for
`usage.relationship_count`.

| Field | In | Type | Notes |
|---|---|---|---|
| `slug` | path | string | Journey slug. |
| `limit` | query | integer | Page size, 1–200. Default 50. |
| `offset` | query | integer | Zero-based offset of the first item. |
| `step_slug` | query | string | Exact current step slug. |

**Response 200:** `{count, limit, offset, has_more, items}`, each item carrying
`relationship_id`, `from_holon`, `to_holon`, `step_title`, `step_slug`,
`follow_up_after` and `responsible_person`.

**Permissions:** a relationship appears only when you can view **both** holons it
joins — either name would otherwise disclose the other.

**Errors:** `404` unknown journey.

---

### `GET /api/v1/journeys/{slug}/conversations` — auth: tokenBearer

Every recorded Conversation on this journey — the same drill-down for
`usage.conversation_count`.

| Field | In | Type | Notes |
|---|---|---|---|
| `slug` | path | string | Journey slug. |
| `limit` | query | integer | Page size, 1–200. Default 50. |
| `offset` | query | integer | Zero-based offset of the first item. |
| `step_slug` | query | string | Exact current step slug. |

**Response 200:** `{count, limit, offset, has_more, items}`, each item carrying
`conversation_id`, `event`, `participants`, `step_title`, `step_slug`,
`follow_up_after` and `responsible_person`.

**Permissions:** a conversation has no holon of its own, so it appears only when
you can view the Event holon it belongs to.

**Errors:** `404` unknown journey.

---

### `POST /api/v1/experiences` — auth: tokenBearer

Create an Experience (gathering-owned) under an owning holon — a Camp or a
Gathering.

**Request body:**

| Field | Type | Notes |
|---|---|---|
| `parent_id` | integer | PK of the owning holon. Must allow an experience-subtree class as a child, or 400. |
| `name` | string | Required, non-empty after trimming. |
| `description` | string | Required, non-empty after trimming. |
| `metis_class` | string, optional | An experience-subtree class slug allowed by `parent_id`. Omit to use the parent's default (first allowed experience class); 400 if the slug given isn't one of the parent's allowed classes. |
| `info_fields` | object (string→any), optional | Same validation as `POST /holons/{holon_id}/update`'s `info_fields` above — in particular, `select`-type fields (e.g. a `tags` field) are **multi-value**: submit a JSON array of strings even for a single tag. A value that isn't in the field's `options` is silently dropped rather than rejected. |

**Response 201:** `{experience: HolonPublic}`.

**Permissions:** the caller must be able to edit the *parent* holon's content
(`can_edit_holon_content`).

**Errors:** `400` (empty name/description, disallowed/unknown `metis_class`,
parent config allows no experience class, invalid `info_fields`), `403`
permission denied on parent, `404` parent not found.

---

### `POST /api/v1/experiences/{experience_id}/logo` — auth: tokenBearer

Upload and set (or replace) an Experience's logo image. The logo is a display
override: it takes precedence over the background image auto-assigned from the
owning camp/gathering's pool, so this is how a caller pins a specific image
instead of accepting the automatic draw.

Send `multipart/form-data` with a single `logo` file part.

| Field  | In   | Type | Notes |
|--------|------|------|-------|
| `experience_id` | path | integer | PK of the Experience holon. |
| `logo` | form | file | Required. `image/jpeg`, `image/png`, `image/gif` or `image/webp`, at most 5 MB. |

**Response 200:** `{experience: HolonPublic}` — `logo_url` reflects the new image.

**Permissions:** the caller must be able to edit the Experience's content
(`can_edit_holon_content`).

**Errors:** `400` (unsupported content type, larger than 5 MB), `403` permission
denied, `404` experience not found.

---

### `GET /api/v1/responsible` — auth: tokenBearer

Unified worklist across Membership (person-side) and HolonRelationship (holon-side)
follow-up assignments, ordered by `follow_up_after` ascending (items with no date sort last).

The two kinds are not forced into one shape: `kind="person"` items carry `person`+`holon`;
`kind="holon"` items carry `from_holon`+`to_holon`.

| Param | In | Required | Default | Description |
|---|---|---|---|---|
| `responsible` | query | no | — | Filter by responsible Person PK |
| `type` | query | no | all | Comma-separated subset of `person` and registered holon class slugs. `person` selects Membership items; each holon class selects HolonRelationship items involving that class or any descendant class. |
| `when` | query | no | none | Comma-separated subset of `overdue`, `today`, `future`. Omitted = no date filter (includes undated). When set, undated items are excluded. |
| `limit` | query | no | 100 | Max 100 |
| `offset` | query | no | 0 | Page offset |

**Response 200:**
```json
{
  "count": 2, "limit": 100, "offset": 0, "has_more": false,
  "items": [
    {
      "kind": "person", "id": 34, "follow_up_after": "2025-03-24",
      "journey_name": "Contact", "step_title": "Invited",
      "responsible_person": {"id": 7, "name": "Victor", ...},
      "person": {"id": 32, "name": "Alice", ...},
      "holon": {"id": 1, "name": "Global", ...}
    },
    {
      "kind": "holon", "id": 9, "follow_up_after": "2025-03-26",
      "journey_name": "Partnership", "step_title": "Negotiating",
      "responsible_person": null,
      "from_holon": {"id": 4, "name": "Summit Camp", ...},
      "to_holon": {"id": 11, "name": "Beta Inc", ...}
    }
  ]
}
```

`journey_name`, `step_title`, `follow_up_after`, and `responsible_person` are `null` when not set.

**Errors:** `400` if `type` or `when` contains an unrecognised value.

---

### `GET /api/v1/people/{person_id}/memberships` — auth: tokenBearer

List all memberships for a person, ordered by journey name then holon name.

| Param | In | Required | Default | Description |
|---|---|---|---|---|
| `person_id` | path | yes | — | Person PK |
| `limit` | query | no | 50 | Max 200 |
| `offset` | query | no | 0 | Page offset |

**Response 200:** `{count, limit, offset, has_more, items: [{membership_id, holon, journey_name, journey_slug, step_title, step_slug, follow_up_after, responsible_person}]}`

`responsible_person` is a full PersonPublic object or `null`.

**Errors:** `404` if person not found.

---

### `GET /api/v1/people/{person_id}/notes` — auth: tokenBearer

List notes on a person's memberships, newest first.

| Param | In | Required | Default | Description |
|---|---|---|---|---|
| `person_id` | path | yes | — | Person PK |
| `limit` | query | no | 50 | Max 200 |

**Response 200:** `{count, limit, items: [{id, body, note_type, created_at, author_person}]}`

`author_person` is a full PersonPublic object or `null`.

**Errors:** `404` if person not found.

---

### `GET /api/v1/holons/{holon_id}/memberships` — auth: tokenBearer

List all memberships in a holon, ordered by journey name then person name.

| Param | In | Required | Default | Description |
|---|---|---|---|---|
| `holon_id` | path | yes | — | Holon PK |
| `q` | query | no | — | Person name, description, or contact substring |
| `journey` | query | no | — | Exact Journey slug |
| `step_slug` | query | no | — | Exact current step slug |
| `responsible_person_id` | query | no | — | Exact responsible Person PK |
| `follow_up` | query | no | — | `overdue`, `today`, `future`, or `none` |
| `sort` | query | no | `name` | `name`, `-name`, `follow_up_after`, `-follow_up_after`, `person_created`, or `-person_created` |
| `limit` | query | no | 50 | Max 200 |
| `offset` | query | no | 0 | Page offset |

`person_created` orders by the **Person's** `created_at` (oldest first; prefix `-` for newest
first) — when the contact entered METIS, not when they joined this holon. See the note under
`GET /api/v1/people`: memberships carry no timestamp, so join order is not available here.

**Response 200:** `{count, limit, offset, has_more, items: [{membership_id, person, journey_name, journey_slug, step_title, step_slug, follow_up_after, responsible_person}]}`

**Errors:** `404` if holon not found.

### `GET /api/v1/holons/{holon_id}/journeys` — auth: tokenBearer

The journeys this holon offers: its class catalog plus any journey assigned to
this holon alone. `offered_by` is `class` or `holon` accordingly. This, not
`GET /classes/holon/{slug}` → `journeys`, is the set the membership endpoints
validate a journey slug against.

| Param | In | Required | Default | Description |
|---|---|---|---|---|
| `holon_id` | path | yes | — | Holon PK |
| `object_kind` | query | no | — | `person` or `holon`; omitted returns both |

Person journeys come first, then holon (relationship) journeys, each in offer
order: class catalog first, then the holon's own additions by name.
Conversation journeys are never listed. Not paged.

**Response 200:** `{count, items: [HolonJourneyItem]}` — a `JourneyListItem`
plus `offered_by`.

**Errors:** `404` if holon not found or not viewable.

---

### `POST /api/v1/holons/{holon_id}/memberships:bulk-add` — auth: tokenBearer

Create 1–500 exact `(person, holon, journey)` Memberships with per-item
outcomes. The Journey must be one the Holon offers — its class catalog **plus**
any journey assigned to that holon directly, which is exactly what
`GET /holons/{holon_id}/journeys` returns — and permit bulk addition. Requires
**Team member** on the holon. A later exact retry returns `already_present`; clients
should not issue overlapping bulk writes for the same Holon. See the
[Outreach API playbook](outreach-PLAYBOOK.md) for the primary client use case;
the live schema defines all fields and errors.

---

### `GET /api/v1/holons/{holon_id}/relationships` — auth: tokenBearer

List holon relationships where the holon appears as `from_holon` or `to_holon`.

| Param | In | Required | Default | Description |
|---|---|---|---|---|
| `holon_id` | path | yes | — | Holon PK |
| `limit` | query | no | 50 | Max 200 |

**Response 200:** `{count, items: [{relationship_id, from_holon, to_holon, journey_name, step_title, follow_up_after, responsible_person}]}`

**Errors:** `404` if holon not found.

---

### `POST /api/v1/holons/{holon_id}/relationships:bulk-add` — auth: tokenBearer

Create 1–500 HolonRelationships from this holon, with per-item outcomes. The
Journey must be a holon journey offered by **either** side — this holon or the
target — which is what `GET /holons/{holon_id}/journeys?object_kind=holon`
returns for each.

A holon pair has at most one relationship, and direction carries no meaning. So
the pair is checked **both ways**: if the two holons are already related in
either direction the item returns `already_present` with the existing
relationship and *its* journey, and nothing is changed — re-running a batch is
safe. An existing link on a different journey is reported, never moved; use
`POST /relationships/{relationship_id}/update` to move it. `already_present`
writes nothing at all — including any `note` sent for that item — so re-running
a batch with fresh notes records none of them.

The target must be one you can view; one you cannot is refused exactly like a
holon that does not exist. Permission is edit access on the path holon. Each new
relationship gets a note — the item's own, or the standard "Relationship
created" one. Clients should not issue overlapping bulk writes for the same
Holon. The live schema defines all fields and errors.

---

### `GET /api/v1/holons/{holon_id}/notes` — auth: tokenBearer

List notes referencing a holon (directly, via its memberships, or via its relationships), newest first.

| Param | In | Required | Default | Description |
|---|---|---|---|---|
| `holon_id` | path | yes | — | Holon PK |
| `limit` | query | no | 50 | Max 200 |

**Response 200:** `{count, limit, items: [{id, body, note_type, created_at, author_person}]}`

**Errors:** `404` if holon not found.

---

### `POST /api/v1/relationships/{relationship_id}/update` — auth: tokenBearer

Record an update on an existing holon relationship: a required note, plus an optional
follow-up date change, an optional change of responsible person, and an optional journey
step move. All changes are applied atomically.

| Param | In | Required | Description |
|---|---|---|---|
| `relationship_id` | path | yes | HolonRelationship PK |

**Request body:**

| Field | Type | Required | Notes |
|---|---|---|---|
| `note` | string | yes | Stored verbatim (trimmed). Must be non-empty. |
| `follow_up_after` | date / null | no | ISO `YYYY-MM-DD` to set, `null` to clear. Omit to leave unchanged. |
| `responsible_person_id` | integer / null | no | Person with a user account; `null` clears responsibility. Omit to leave unchanged. |
| `step_slug` | string | no | Active step slug on the relationship's current journey. |
| `advance_step` | boolean | no | Move to the next active step in the current journey. |

`step_slug` and `advance_step: true` are mutually exclusive.

**Behavior:**
- `step_slug` must name a non-archived step on the relationship's existing journey.
- `advance_step: true` moves to the next active step by `(order, pk)`; the first active step when no current step is set.
- The `changes` object in the response reports what actually changed (never augments the note text).

**Response 200:** `{relationship, note, changes}` where `changes` reports `current_step` (by slug), `follow_up_after` (ISO dates) and/or `responsible_person_id` (Person PKs; `old` is `null` when the previous responsible has no linked Person) as `{old, new}`. Empty when nothing changed.

**Permissions:** a caller who can edit either holon side may update the relationship.

**Errors:** `400` (empty note, malformed date, invalid step_slug, both step controls supplied, no next step, unknown `responsible_person_id` or a Person with no user account), `403` permission denied, `404` not found.

---

### `POST /api/v1/memberships/{membership_id}/update` — auth: tokenBearer

Record an update on an existing person membership: a required note, plus an optional
follow-up date change, an optional journey step move, and an optional journey
reassignment. All changes are applied atomically. **This is also the only way to move
a membership onto a different Journey** — there is no separate transfer endpoint and
`memberships:bulk-add` only creates new memberships; set `journey_slug` (with `step_slug`)
here to reassign an existing one.

| Param | In | Required | Description |
|---|---|---|---|
| `membership_id` | path | yes | Membership PK |

**Request body:**

| Field | Type | Required | Notes |
|---|---|---|---|
| `note` | string | yes | Stored verbatim (trimmed). Must be non-empty. |
| `follow_up_after` | date / null | no | ISO `YYYY-MM-DD` to set, `null` to clear. Omit to leave unchanged. |
| `step_slug` | string | no | Active step slug. Resolved against the membership's current journey, or against `journey_slug` if that's also given. Required when `journey_slug` is given. |
| `advance_step` | boolean | no | Move to the next active step in the current journey. Mutually exclusive with `journey_slug`. |
| `responsible_person_id` | integer / null | no | Person with a user account; `null` clears responsibility. Omit to leave unchanged. |
| `journey_slug` | string | no | Move the membership to a different Journey on the same Holon. Must be paired with `step_slug`; mutually exclusive with `advance_step`. Omit to leave the membership on its current Journey. |

`step_slug` and `advance_step: true` are mutually exclusive. `journey_slug` requires `step_slug` and is mutually exclusive with `advance_step`.

**Behavior:**
- `step_slug` must name a non-archived step — on the membership's existing journey, or on `journey_slug`'s journey when reassigning.
- `advance_step: true` moves to the next active step by `(order, pk)`; the first active step when no current step is set.
- `journey_slug` must name one of the person journeys the holon offers — its class catalog plus any journey assigned to that holon directly (`GET /holons/{holon_id}/journeys`) (a journey's `allow_bulk_add: false` config does *not* block reassignment, unlike bulk-add). Reassignment is rejected if the person already has another membership on that journey for the same holon.
- The `changes` object in the response reports what actually changed (never augments the note text).
- The note is attached to both the person's and the holon's note feeds.

**Response 200:** `{membership, note, changes}` where `changes` reports `journey` (by slug), `current_step` (by slug), `follow_up_after` (ISO dates) and/or `responsible_person_id` (Person PKs; `old` is `null` when the previous responsible has no linked Person) as `{old, new}`. Empty when nothing changed.

**Permissions:** a caller who can edit the membership's holon may update it.

**Errors:** `400` (empty note, malformed date, invalid step_slug, both step controls supplied, no next step, journey_slug without step_slug, journey_slug not allowed on this holon, duplicate membership on target journey, unknown `responsible_person_id` or a Person with no user account), `403` permission denied, `404` not found.

---

### Record history

Four read-only routes answer "who changed this, when, how, and what changed". Holons and people return every saved revision with its field changes; memberships and relationships return the periods they spent on each journey step. Other changes to a membership or relationship (follow-up date, priority and so on) are not recorded field by field, and neither are changes to classes or journeys.

- **`via`** is the channel a change came through: `web`, `admin`, `extension`, `api`, or `system` (no request at all: a script, a scheduled task, a test fixture). It is **`null` on every change saved before channels began to be recorded** — that means "not recorded", not "system".
- Changes made by a database migration, or by data loaded directly into the database, leave no entry at all.
- `config` holds admin-only settings, so a `config` change shows which setting changed with `withheld: true` and `old`/`new` both `null`.
- History shows values the record no longer has, so each route is readable by whoever may **edit** that record.

### `GET /api/v1/holons/{holon_id}/history` — auth: tokenBearer

List a holon's saved revisions, newest first.

| Param | In | Required | Default | Description |
|---|---|---|---|---|
| `holon_id` | path | yes | — | Holon PK |
| `limit` | query | no | 50 | 1-200 |
| `offset` | query | no | 0 | Zero-based offset |

**Response 200:** `{count, limit, offset, has_more, items: [{at, action, by_person, by_name, via, changes}]}`

- `action` is `created`, `updated` or `deleted`.
- `by_person` is a full PersonPublic object or `null`; `by_name` is a display name for the account (`null` when no account is recorded).
- `changes` is a list of `{path, old, new, withheld}`. Inside a JSON field the path names the leaf (`infos.info_fields.length`, `links.website`), or just the field (`links`) with the whole old and new values when the field changed as a whole (for example from null to an object); a foreign key is reported under its field name (`parent`, `metis_class`) with primary keys. `[]` for `created`, and for a save that changed nothing but its timestamp. `null` for the oldest recorded change when it is not a creation: there is nothing earlier to compare it with.
- One item per saved revision: nothing is merged or dropped, so `count` always matches `items`.

**Errors:** `403` if the caller may view but not edit the holon, `404` if the holon does not exist or the caller may not view it.

---

### `GET /api/v1/people/{person_id}/history` — auth: tokenBearer

List a Person's saved revisions, newest first. Same parameters and response as the holon route above, with `person_id` in the path.

**Errors:** `403` if the caller may not edit the Person, `404` if the Person does not exist.

---

### `GET /api/v1/memberships/{membership_id}/history` — auth: tokenBearer

List the periods a membership spent on each journey step, newest first.

| Param | In | Required | Default | Description |
|---|---|---|---|---|
| `membership_id` | path | yes | — | Membership PK |
| `limit` | query | no | 50 | 1-200 |
| `offset` | query | no | 0 | Zero-based offset |

**Response 200:** `{count, limit, offset, has_more, items: [{step_slug, step_title, entered_at, exited_at, outcome, by_person, by_name, via, reason}]}`

- `exited_at` is `null` for the step the membership is on now.
- `via` is how the membership was moved onto the step: `person`, `api`, `runner`, `runtime`, `system`, or `backfill` (the period recording began with; nobody moved it there).

**Errors:** the same rule as `POST /api/v1/memberships/{membership_id}/update`: `403` if the caller may not update the membership, `404` if it does not exist or its holon is not viewable.

---

### `GET /api/v1/relationships/{relationship_id}/history` — auth: tokenBearer

List the periods a holon relationship spent on each journey step, newest first. Same parameters and response as the membership route above, with `relationship_id` in the path.

**Errors:** the same rule as `POST /api/v1/relationships/{relationship_id}/update`: `403` if the caller may not update the relationship, `404` if it does not exist or either holon is not viewable.

---

## Public field projections

**PersonPublic:** `id`, `name`, `description`, `photo_url`, `actor_kind`, `contact`

Private fields (`infos`, `config`, memberships, journey state, notes) are excluded.
`contact` is returned to authenticated read-token holders.

**HolonPublic:** `id`, `name`, `slug`, `type`, `description`, `parent_id`, `logo_url`, `links`, `info_fields`

`type` is always the Holon's class slug string, not a nested class object. Slugs are
database-backed; active ones are discoverable at `/api/v1/classes?object_kind=holon`,
but a Holon can carry a retired (`is_active: false`) class slug that is not present in
that list — see [`GET /api/v1/classes`](#get-apiv1classes--auth-tokenbearer) above.

`logo_url` is computed as `holon.logo.url if holon.logo else null` — it is not a model
field, and is `null` when no logo is set.
`links` is returned to authenticated read-token holders.

`info_fields` carries the holon class's configured field values, keyed by field `key`.
A **slideshow** key reads as a list of image URLs in display order, and is present as an
empty list when the slideshow holds nothing — so a key you found in `GET /classes` never
simply disappears. Photo *ids*, which `:reorder` and `/remove` take, come from the
slideshow endpoints rather than from here.

Note this applies to **list** responses too, not only to reading one holon: a page of 200
holons of a class with a 30-photo slideshow carries 6000 URL strings. If you are paging
for names and ids, the payload is larger than it was before these fields existed.

Private fields (`infos`, `config`, memberships, relationships, journey state, notes) are excluded.

**Not the same shape as `/public/`'s projections.** `/public/` (see
[`public-PLAYBOOK.md`](public-PLAYBOOK.md)) serves a fully anonymous caller and
deliberately uses narrower, differently-named schemas built from data that's
already been `public_only`-filtered — it does not reuse `PersonPublic`/`HolonPublic`
above, since those assume a trusted, authenticated caller (e.g. `PersonPublic.contact`
dumps the raw contact dict). This divergence is intentional; don't try to unify them.

---

## Scope notes

- No CORS — designed for server-side AI clients, not browser JS.
- List endpoints return `[]` when nothing matches (never 404).
- `GET` endpoints do not create or modify records.
