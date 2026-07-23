# METIS API

Public REST API for AI clients. Mostly read-only; the write endpoints are
`POST /api/v1/relationships/{relationship_id}/update`,
`POST /api/v1/memberships/{membership_id}/update`, and
`POST /api/v1/holons/{holon_id}/update`. Generic bounded Membership creation is
available at `POST /api/v1/holons/{holon_id}/memberships:bulk-add`.

**Live schema:** `https://app.the-gathering.earth/api/v1/openapi.json`
**Swagger UI:** `https://app.the-gathering.earth/api/v1/docs`

---

## Coherence Core API

Coherence maintains its API narrative and operational conventions in
`coherence-PLAYBOOK.md`, including event discovery,
operational conversation search, and journey-step config reading/tuning
(IRIS prompts). The live shared Core API schema is available at
`/api/openapi.json` and interactive documentation at `/api/docs`. Keep endpoint
contracts in those Coherence-owned sources rather than duplicating them here.

---

## Outreach

Outreach uses the generic Holon and Membership endpoints for private network
search and campaign workflows, plus app-owned `/api/v1/outreach/actions` and
`/api/v1/outreach/people/{person_id}/linkedin` endpoints for action queues and
source-specific Person enrichment. See
[`outreach-PLAYBOOK.md`](outreach-PLAYBOOK.md) for the client flow and
[`../metis_apps/outreach/linkedin-outreach.md`](../metis_apps/outreach/linkedin-outreach.md)
for the web import and campaign guide. There is no API import route and no
Outreach-specific contacts resource.

The Chrome extension uses the session-authenticated `/eapi/v1/outreach/`
surface to advance the same Membership workflow; see the
[`extension-PLAYBOOK.md`](extension-PLAYBOOK.md) for that browser-only flow.

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
  or a caller whose team-active authority covers that Holon. Direct reads of an
  inaccessible private Holon return `404`, and collection/worklist endpoints
  filter it out.
- **Writes** (`POST /relationships/{id}/update`, `POST /memberships/{id}/update`,
  `POST /holons/{id}/update`) **are** object-scoped: the caller must be able to
  edit the relevant holon — `can_update_relationship` (either side of the
  relationship), `can_update_membership` (the membership's holon), or
  `can_edit_holon` (the holon itself) — otherwise the call returns
  `403 permission_denied`. `POST /holons/{id}/update` additionally requires
  global edit access to set `journey_ids`.

Do not use ordinary Person fields for private address-book data: Person
projections remain shared-directory data even when one of their Memberships is
on a private Holon.

---

## Endpoints

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
| `limit` | query | no | 100 | Max 100 |
| `offset` | query | no | 0 | Page offset — increment by `limit` until `has_more` is `false` |

**Response 200:** `{query, limit, offset, count, has_more, items: [PersonPublic]}`

---

### `GET /api/v1/people/{person_id}` — auth: tokenBearer

Retrieve one person by integer PK. Returns 404 if not found.

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
| `info_fields` | object (string→any) | Keyed by an `info_field_groups` field `key` for the holon's class (discoverable via `GET /classes`). 400 on an unknown key, a `slideshow`-type key (not settable via this API), or a malformed `select`/`video` value. A `select`-type field is **multi-value**: its value must be a JSON array of strings (e.g. `["Dancing and music", "Inner Development"]`), even to set a single tag — there is no single-value select. Any submitted value not in the field's `options` list is silently dropped rather than rejected, so double-check spelling against `GET /classes`. |
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

### `GET /api/v1/classes` — auth: tokenBearer

Discover active object classes and API-safe capability config. Use `object_kind=holon`
to list Holon classes. Existing Holon payloads still return the class slug as
`type`; they do not embed class config.

Only classes with `is_active: true` are listed here. A class can be retired
(`is_active: false`) while objects already assigned to it remain on it — their
`type` will still show the retired slug, but that slug will not appear in this
list and `GET /classes/{object_kind}/{slug}` will 404 for it. Treat an unknown
`type` as "retired class", not an error.

For holon classes, `config` also includes `info_field_groups` — the schema of
custom per-class fields (grouped, each with `key`/`type`/`label`/`options`/etc.)
that `POST /holons/{holon_id}/update`'s `info_fields` accepts, keyed by `key`.

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
  "config": {"css_class": "holon-type-event", "hasAdditionalFields": true}
}
```

### `GET /api/v1/classes/{object_kind}/{slug}` — auth: tokenBearer

Retrieve one active object class. Returns 404 if not found or inactive.

---

### `GET /api/v1/journeys` — auth: tokenBearer

List every Journey with aggregate usage counts, for auditing the journey
catalog (e.g. spotting unused or redundant journeys). Each item reports
`step_count` and a `usage` object (`holon_direct_count`, `membership_count`,
`relationship_count`) — aggregate totals only, not the underlying rows. To
inspect the actual Membership/HolonRelationship records, use
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
  "usage": {"holon_direct_count": 1, "membership_count": 0, "relationship_count": 4}
}
```

### `GET /api/v1/journeys/{slug}` — auth: tokenBearer

Retrieve one journey, including every step (ordered, archived steps included)
with per-step `usage` counts (`membership_count`, `relationship_count`) — the
signal for spotting orphaned or stale steps. Returns 404 if not found.

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
  "usage": {"membership_count": 0, "relationship_count": 1}
}
```

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
| `info_fields` | object (string→any), optional | Same validation as `POST /holons/{holon_id}/update`'s `info_fields` above — in particular, `select`-type fields (e.g. a `tags` field) take a JSON array of strings, not a single string. |

**Response 201:** `{experience: HolonPublic}`.

**Permissions:** the caller must be able to edit the *parent* holon's content
(`can_edit_holon_content`).

**Errors:** `400` (empty name/description, disallowed/unknown `metis_class`,
parent config allows no experience class, invalid `info_fields`), `403`
permission denied on parent, `404` parent not found.

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
| `sort` | query | no | `name` | `name`, `-name`, `follow_up_after`, or `-follow_up_after` |
| `limit` | query | no | 50 | Max 200 |
| `offset` | query | no | 0 | Page offset |

**Response 200:** `{count, limit, offset, has_more, items: [{membership_id, person, journey_name, journey_slug, step_title, step_slug, follow_up_after, responsible_person}]}`

**Errors:** `404` if holon not found.

### `POST /api/v1/holons/{holon_id}/memberships:bulk-add` — auth: tokenBearer

Create 1–500 exact `(person, holon, journey)` Memberships with per-item
outcomes. The Journey must be available in the Holon's effective class catalog
and permit bulk addition. A later exact retry returns `already_present`; clients
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
follow-up date change and an optional journey step move. All changes are applied atomically.

| Param | In | Required | Description |
|---|---|---|---|
| `relationship_id` | path | yes | HolonRelationship PK |

**Request body:**

| Field | Type | Required | Notes |
|---|---|---|---|
| `note` | string | yes | Stored verbatim (trimmed). Must be non-empty. |
| `follow_up_after` | date / null | no | ISO `YYYY-MM-DD` to set, `null` to clear. Omit to leave unchanged. |
| `step_slug` | string | no | Active step slug on the relationship's current journey. |
| `advance_step` | boolean | no | Move to the next active step in the current journey. |

`step_slug` and `advance_step: true` are mutually exclusive.

**Behavior:**
- `step_slug` must name a non-archived step on the relationship's existing journey.
- `advance_step: true` moves to the next active step by `(order, pk)`; the first active step when no current step is set.
- The `changes` object in the response reports what actually changed (never augments the note text).

**Response 200:** `{relationship, note, changes}` where `changes` reports `current_step` (by slug) and/or `follow_up_after` (ISO dates) as `{old, new}`. Empty when nothing changed.

**Permissions:** a caller who can edit either holon side may update the relationship.

**Errors:** `400` (empty note, malformed date, invalid step_slug, both step controls supplied, no next step), `403` permission denied, `404` not found.

---

### `POST /api/v1/memberships/{membership_id}/update` — auth: tokenBearer

Record an update on an existing person membership: a required note, plus an optional
follow-up date change and an optional journey step move. All changes are applied atomically.

| Param | In | Required | Description |
|---|---|---|---|
| `membership_id` | path | yes | Membership PK |

**Request body:**

| Field | Type | Required | Notes |
|---|---|---|---|
| `note` | string | yes | Stored verbatim (trimmed). Must be non-empty. |
| `follow_up_after` | date / null | no | ISO `YYYY-MM-DD` to set, `null` to clear. Omit to leave unchanged. |
| `step_slug` | string | no | Active step slug on the membership's current journey. |
| `advance_step` | boolean | no | Move to the next active step in the current journey. |
| `responsible_person_id` | integer / null | no | Person with a user account; `null` clears responsibility. |

`step_slug` and `advance_step: true` are mutually exclusive.

**Behavior:**
- `step_slug` must name a non-archived step on the membership's existing journey.
- `advance_step: true` moves to the next active step by `(order, pk)`; the first active step when no current step is set.
- The `changes` object in the response reports what actually changed (never augments the note text).
- The note is attached to both the person's and the holon's note feeds.

**Response 200:** `{membership, note, changes}` where `changes` reports `current_step` (by slug) and/or `follow_up_after` (ISO dates) as `{old, new}`. Empty when nothing changed.

**Permissions:** a caller who can edit the membership's holon may update it.

**Errors:** `400` (empty note, malformed date, invalid step_slug, both step controls supplied, no next step), `403` permission denied, `404` not found.

---

## Public field projections

**PersonPublic:** `id`, `name`, `description`, `photo_url`, `actor_kind`, `contact`

Private fields (`infos`, `config`, memberships, journey state, notes) are excluded.
`contact` is returned to authenticated read-token holders.

**HolonPublic:** `id`, `name`, `slug`, `type`, `description`, `parent_id`, `logo_url`, `links`

`type` is always the Holon's class slug string, not a nested class object. Valid
slugs are database-backed and can be discovered through `/api/v1/classes?object_kind=holon`.

`logo_url` is `null` when no logo is set.
`links` is returned to authenticated read-token holders.

Private fields (`infos`, `config`, memberships, relationships, journey state, notes) are excluded.

---

## Scope notes

- No CORS — designed for server-side AI clients, not browser JS.
- List endpoints return `[]` when nothing matches (never 404).
- `GET` endpoints do not create or modify records.
