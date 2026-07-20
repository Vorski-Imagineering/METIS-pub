# API Playbook

Authoritative reference for the METIS REST API. All endpoints, conventions, and
integration patterns are documented here.

Live OpenAPI schemas: `/api/v1/openapi.json` (API), `/api/openapi.json` (Core)

---

## General Conventions

### Authentication

All endpoints require a Bearer token unless noted otherwise:

```
Authorization: Bearer <API_TOKEN>
```

Webhook endpoints (`/api/hook/*`) are unauthenticated.

### CORS

Browser CORS is enabled for API routes only (`/api/*`).

- Allowed origins come from `CORS_ALLOWED_ORIGINS` (comma-separated env var).
- Allowed methods: `GET, POST, PUT, PATCH, OPTIONS`.
- Allowed request headers: `Authorization, Content-Type`.
- Preflight `OPTIONS` requests return CORS headers for allowed origins.

### Base URL

`/api/`

### Routing

| Prefix       | Auth                  |
|--------------|-----------------------|
| `/v1`        | TokenBearer (per-op) |
| `/hook`      | None                  |
| `/agents`    | Bearer (API_TOKEN)    |
| *(root)*     | —                     |

Coherence API (`/api/coherence/`): see `coherence-PLAYBOOK.md`

### Response shapes

- Top-level responses use typed Ninja `Schema` classes (no raw dicts).
- Nullable fields use `Optional[T] = None`.
- No deep nesting beyond one level.
- List endpoints return `[]` when nothing matches (not 404).

### Side effects

- `GET` endpoints do **not** create records unless explicitly documented (see
  `GET /coherence/conversations` below).
- System-generated notes use `create_note_with_refs(author=None, ...)`.

---

## API v1 — `/api/v1/`

Public REST API for AI clients and the METIS-hosted MCP adapter. Mostly read-only; the two
write endpoints are `POST /api/v1/relationships/{relationship_id}/update` and
`POST /api/v1/memberships/{membership_id}/update`.

**Live schema:** `/api/v1/openapi.json` — always in sync with the implementation.
**Swagger UI:** `/api/v1/docs`

---

### Authentication

The API uses a two-step auth flow distinct from the main `API_TOKEN` bearer and browser session cookies. **Neither `API_TOKEN` nor session cookies authenticate `/api/v1/` endpoints.**

#### Login flow

1. Client calls `POST /api/v1/auth/login` with:
   - `X-Metis-Api-Key: <API_LOGIN_SECRET>` header
   - JSON body: `{"email": "...", "password": "..."}`
2. Server returns a 24-hour bearer token: `metis_agentic_<token_id>_<secret>`
3. Subsequent calls send `Authorization: Bearer <token>`
4. Logout: `POST /api/v1/auth/logout` revokes the token server-side

**Token format:** `metis_agentic_<session_key>_<secret>`
- `session_key`: 32-char lowercase-alphanumeric Django session key
- `secret`: 43-char base64url random value (only a SHA-256 hash is stored server-side)
- Backed by the Django database session table (not per-process cache)

**Invalidation triggers:**
- Explicit logout
- Token expiry (24 hours)
- Password change (`account.get_session_auth_hash()` mismatch)
- Account deactivation (`is_active=False`)

#### Settings

| Setting               | Env var               | Description |
|-----------------------|-----------------------|-------------|
| `API_LOGIN_SECRET` | `API_LOGIN_SECRET` | Shared login gate secret. Required on every login call. Rotate by updating the env var and updating client config. |

**Secret rotation procedure:**
1. Set the new `API_LOGIN_SECRET` in the server environment and restart/reload.
2. Update all clients to send the new value in `X-Metis-Api-Key`.
3. Existing read tokens remain valid until they expire naturally or are logged out.

---

### Error shape

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

**Exception — request validation (`422`):** errors raised by the framework
*before* the endpoint runs (a missing required query/path param, or a value
outside its allowed range — e.g. `limit` above its cap) do **not** use the
envelope above. They return HTTP `422` with django-ninja's default shape:

```json
{"detail": [{"type": "...", "loc": ["query", "limit"], "msg": "..."}]}
```

Application-level validation that the endpoint checks itself (unknown `type`,
empty `q` after trimming, etc.) still returns `400` with the `validation_error`
envelope. Clients should treat both `400` and `422` as non-retryable bad input.

---

### Endpoints

#### `POST /api/v1/auth/login` — auth: X-Metis-Api-Key + credentials

Exchange METIS email/password for a 24-hour bearer token. The account must have a linked METIS `Person` or login returns 403.

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

#### `POST /api/v1/auth/logout` — auth: tokenBearer

Revoke the current read token. The backing session row is deleted immediately.

**Response 200:** `{"revoked": true}`

---

#### `GET /api/v1/auth/whoami` — auth: tokenBearer

Return the logged-in METIS `Person` for the current token.

**Response 200:**
```json
{"authenticated": true, "person": {"id": 42, "name": "Alice", ...}}
```

---

#### `GET /api/v1/search` — auth: tokenBearer

Search public `Person` and `Holon` fields. Mirrors the `/search/` UI behavior.

| Param | In | Required | Default | Description |
|---|---|---|---|---|
| `q` | query | yes | — | Search query (min 2 chars) |
| `types` | query | no | `person,holon` | Comma-separated subset |
| `limit_per_type` | query | no | 20 | Max 50 per type |

Returns ranked results (name/channel hits ranked above description-only hits).

---

#### `GET /api/v1/people` — auth: tokenBearer

Search people by name substring.

| Param | In | Required | Default | Description |
|---|---|---|---|---|
| `q` | query | yes | — | Case-insensitive `Person.name` substring |
| `limit` | query | no | 100 | Max 100 |
| `offset` | query | no | 0 | Page offset — page by incrementing `offset` by `limit` until `has_more` is `false` |

**Response 200:** `PersonSearchResponse` — `{query, limit, offset, count, has_more, items}`

---

#### `GET /api/v1/people/{person_id}` — auth: tokenBearer

Retrieve one person by integer PK. Returns 404 if not found.

---

#### `GET /api/v1/holons` — auth: tokenBearer

Search holons. At least one of `q` or `class` must be provided.

| Param | In | Required | Description |
|---|---|---|---|
| `q` | query | no | Case-insensitive `Holon.name` substring |
| `class` | query | no | Holon class slug, e.g. `organisation`, `local_gathering`, `camp`, or `domain`. Matches that class and its whole subtree (e.g. `class=camp` also reaches `camp_pt2026`, `camp_mx2026`, etc.). |
| `parent` | query | no | Filter by parent Holon PK (e.g. parent Local Gathering for camps) |
| `limit` | query | no | Default 100, max 100 |
| `offset` | query | no | Page offset — page by incrementing `offset` by `limit` until `has_more` is `false` |

**Response 200:** `HolonSearchResponse` — `{query, class, parent, limit, offset, count, has_more, items}`

---

#### `GET /api/v1/classes` — auth: tokenBearer

Discover active database-backed object classes and API-safe capability config.
Use `object_kind=holon` to list Holon classes. Existing Holon payloads continue
to expose the class slug as the string field `type`; class metadata is not
embedded in every Holon response.

Only `is_active: true` classes are listed. A retired class (`is_active: false`)
can still be the `type` on objects assigned to it before retirement — that slug
won't appear here or resolve via `/classes/{object_kind}/{slug}` (404). An
unknown `type` value means "retired class", not a data error.

| Param | In | Required | Description |
|---|---|---|---|
| `object_kind` | query | no | Optional class scope, e.g. `holon` |

**Response 200:** `list[MetisClassPublic]`

#### `GET /api/v1/classes/{object_kind}/{slug}` — auth: tokenBearer

Retrieve one active object class with API-safe config. Returns 404 if not found
or inactive.

---

#### `GET /api/v1/holons/{holon_id}` — auth: tokenBearer

Retrieve one holon by integer PK. Returns 404 if not found.

---

#### `GET /api/v1/holons/by-slug/{slug}` — auth: tokenBearer

Retrieve one holon by slug. Returns 404 if not found.

---

#### `POST /api/v1/experiences` — auth: tokenBearer

Create an Experience (gathering-owned) under an owning holon (a Camp or a
Gathering). Body: `parent_id` (int, required), `name`/`description` (string,
required), `metis_class` (string, optional — an experience-subtree class
slug allowed by the parent; defaults to the parent's first allowed one),
`info_fields` (object, optional).

`info_fields` uses the same validation as `info_fields` on
`POST /holons/{holon_id}/update` — notably, a `select`-type field (e.g. a
`tags` field) is **multi-value**: submit a JSON array of strings even for a
single tag, and any value not in the field's `options` is silently dropped
rather than rejected.

**Response 201:** `{experience: HolonPublic}`. **Errors:** `400` (empty
name/description, disallowed `metis_class`, no experience class allowed on
parent, invalid `info_fields`), `403` (no edit access to parent), `404`
(parent not found).

---

### Public field projections (v1)

**PersonPublic:** `id`, `name`, `description`, `photo_url`, `actor_kind`, `contact`

Private fields (`infos`, `config`, memberships, journey state, notes) are excluded from v1.
`contact` is intentionally returned to authenticated read-token holders.

**HolonPublic:** `id`, `name`, `slug`, `type`, `description`, `parent_id`, `logo_url`, `links`

`type` is the Holon's class slug string. Slugs are database-backed; active ones
are discoverable at `/api/v1/classes?object_kind=holon`, but a Holon can carry
a retired (`is_active: false`) class slug not present in that list — see
`GET /api/v1/classes` above.

`logo_url` is computed as `holon.logo.url if holon.logo else null` — it is not a model field.
`links` is intentionally returned to authenticated read-token holders.

Private fields (`infos`, `config`, memberships, relationships, journey state, notes) are excluded from v1.

---

#### `GET /api/v1/responsible` — auth: tokenBearer

Unified worklist across both `Membership` (person-side) and `HolonRelationship`
(holon-side) follow-up assignments, ordered by `follow_up_after` ascending
(items with no `follow_up_after` sort last). Any authenticated read-token
holder can see all records.

The two kinds are not forced into one shape: `kind="person"` items carry
`person`+`holon`; `kind="holon"` items carry `from_holon`+`to_holon`.
`HolonRelationship` has no inherent "subject" side (it's symmetric — `from_holon`
and `to_holon` are just two related holons), so unlike `Membership` it
can't be collapsed into a single subject/context pair.

| Param         | In    | Required | Default | Description |
|---------------|-------|----------|---------|-------------|
| `responsible` | query | no       | —       | Filter by responsible `Person.id` |
| `type`        | query | no       | all     | Comma-separated subset of `person`, `organisation`, `local_gathering`, `camp`, `domain`. `person` selects `Membership` items; the Holon types select `HolonRelationship` items where `from_holon` or `to_holon` has that class slug. |
| `when`        | query | no       | none    | Comma-separated subset of `overdue`, `today`, `future`. Omitted = no date filter (includes items with no `follow_up_after` set). When provided, only matching buckets are included (undated items are excluded). |
| `limit`       | query | no       | 100     | Max 100     |
| `offset`      | query | no       | 0       | Page offset — page by incrementing `offset` by `limit` until `has_more` is `false` |

**Response 200:**
```json
{
  "count": 2,
  "limit": 100,
  "offset": 0,
  "has_more": false,
  "items": [
    {
      "kind": "person",
      "id": 34,
      "follow_up_after": "2025-03-24",
      "journey_name": "Contact",
      "step_title": "Invited",
      "responsible_person": { "id": 7, "name": "Victor Vorski", ... },
      "person": { "id": 32, "name": "liel maghen", ... },
      "holon": { "id": 1, "name": "Global", ... }
    },
    {
      "kind": "holon",
      "id": 9,
      "follow_up_after": "2025-03-26",
      "journey_name": "Partnership",
      "step_title": "Negotiating",
      "responsible_person": null,
      "from_holon": { "id": 4, "name": "Summit Camp", ... },
      "to_holon": { "id": 11, "name": "Beta Inc", ... }
    }
  ]
}
```

`journey_name`, `step_title`, `follow_up_after`, and `responsible_person` are
`null` when not set. `person`/`holon` are only present on `kind="person"`
items; `from_holon`/`to_holon` are only present on `kind="holon"` items.

**Errors:** `400` if `type` or `when` contains an unrecognised value.

---

#### `GET /api/v1/people/{person_id}/memberships` — auth: tokenBearer

List all memberships for a person, ordered by journey name then holon name.

| Param       | In    | Required | Default | Description |
|-------------|-------|----------|---------|-------------|
| `person_id` | path  | yes      | —       | Person PK   |
| `limit`     | query | no       | 50      | Max 200     |

**Response 200:** `MembershipListResponse` — `{count, items: [{membership_id, holon, journey_name, step_title, follow_up_after, responsible_person}]}`

`responsible_person` is a full `PersonPublic` object or `null`.

**Errors:** `404` if person not found.

---

#### `GET /api/v1/people/{person_id}/notes` — auth: tokenBearer

List notes attached to a person's memberships (via `NoteReference` role=FLOW), newest first.

| Param       | In    | Required | Default | Description |
|-------------|-------|----------|---------|-------------|
| `person_id` | path  | yes      | —       | Person PK   |
| `limit`     | query | no       | 50      | Max 200     |

**Response 200:** `NoteListResponse` — `{count, limit, items: [{id, body, note_type, created_at, author_person}]}`

`author_person` is a full `PersonPublic` object or `null`.

**Errors:** `404` if person not found.

---

#### `GET /api/v1/holons/{holon_id}/memberships` — auth: tokenBearer

List all memberships in a holon, ordered by journey name then person name.

| Param      | In    | Required | Default | Description |
|------------|-------|----------|---------|-------------|
| `holon_id` | path  | yes      | —       | Holon PK    |
| `limit`    | query | no       | 50      | Max 200     |

**Response 200:** `HolonMembershipListResponse` — `{count, items: [{membership_id, person, journey_name, step_title, follow_up_after, responsible_person}]}`

**Errors:** `404` if holon not found.

---

#### `GET /api/v1/holons/{holon_id}/relationships` — auth: tokenBearer

List holon relationships where the holon appears as `from_holon` or `to_holon`.

| Param      | In    | Required | Default | Description |
|------------|-------|----------|---------|-------------|
| `holon_id` | path  | yes      | —       | Holon PK    |
| `limit`    | query | no       | 50      | Max 200     |

**Response 200:** `HolonRelationshipListResponse` — `{count, items: [{relationship_id, from_holon, to_holon, journey_name, step_title, follow_up_after, responsible_person}]}`

**Errors:** `404` if holon not found.

---

#### `GET /api/v1/holons/{holon_id}/notes` — auth: tokenBearer

List notes referencing a holon directly, or via its memberships/relationships, newest first.

| Param      | In    | Required | Default | Description |
|------------|-------|----------|---------|-------------|
| `holon_id` | path  | yes      | —       | Holon PK    |
| `limit`    | query | no       | 50      | Max 200     |

**Response 200:** `NoteListResponse` — `{count, limit, items: [{id, body, note_type, created_at, author_person}]}`

**Errors:** `404` if holon not found.

---

#### `POST /api/v1/relationships/{relationship_id}/update` — auth: tokenBearer

Record an update on an existing `HolonRelationship`: a required note, plus an optional follow-up date change and an optional journey step move. Field changes and the note are applied atomically.

| Param             | In   | Required | Description                  |
|-------------------|------|----------|------------------------------|
| `relationship_id` | path | yes      | `HolonRelationship` PK       |

**Request body** (`RelationshipUpdateIn`):

| Field            | Type        | Required | Notes |
|------------------|-------------|----------|-------|
| `note`           | string      | yes      | Stored verbatim (trimmed). Must be non-empty. |
| `follow_up_after`| date / null | no       | ISO `YYYY-MM-DD` to set, `null` to clear. Omit to leave unchanged. |
| `step_slug`      | string      | no       | Active step slug on the relationship's current journey. |
| `advance_step`   | boolean     | no       | Move to the next active step in the current journey. |

`step_slug` and `advance_step: true` are mutually exclusive.

**Behavior:**
- `step_slug` must name a non-archived step on the relationship's existing journey; any missing/archived/other-journey slug is `400 validation_error`.
- `advance_step: true` moves to the next active step by `(order, pk)`; the first active step when no current step is set; `400 validation_error` ("no next active step") if there is none.
- The note body is never augmented with audit text — the `changes` object reports what actually changed instead.

**Response 200:** `RelationshipUpdateOut` — `{relationship, note, changes}` where `relationship` is a `HolonRelationshipItem`, `note` is a `NoteItem`, and `changes` reports `current_step` (by **slug**) and/or `follow_up_after` (ISO dates) as `{old, new}`. `changes` is empty for a note-only update or when submitted values match current values.

**Permissions:** union of both holon sides — a caller who can edit `from_holon` OR `to_holon` may update (`can_update_relationship`). Account FK ids are never exposed; `responsible`/`author` are projected as `Person` (`responsible_person`, `author_person`) or null.

**Errors:** `400` (empty note, malformed `follow_up_after`, invalid `step_slug`, both step controls supplied, no next active step), `403` permission denied, `404` relationship not found.

---

#### `POST /api/v1/memberships/{membership_id}/update` — auth: tokenBearer

Record an update on an existing `Membership`: a required note, plus an optional follow-up date change and an optional journey step move. Field changes and the note are applied atomically.

| Param           | In   | Required | Description       |
|-----------------|------|----------|--------------------|
| `membership_id` | path | yes      | `Membership` PK    |

**Request body** (`RelationshipUpdateIn` — same shape as the relationship-update endpoint):

| Field            | Type        | Required | Notes |
|------------------|-------------|----------|-------|
| `note`           | string      | yes      | Stored verbatim (trimmed). Must be non-empty. |
| `follow_up_after`| date / null | no       | ISO `YYYY-MM-DD` to set, `null` to clear. Omit to leave unchanged. |
| `step_slug`      | string      | no       | Active step slug on the membership's current journey. |
| `advance_step`   | boolean     | no       | Move to the next active step in the current journey. |

`step_slug` and `advance_step: true` are mutually exclusive.

**Behavior:**
- `step_slug` must name a non-archived step on the membership's existing journey; any missing/archived/other-journey slug is `400 validation_error`.
- `advance_step: true` moves to the next active step by `(order, pk)`; the first active step when no current step is set; `400 validation_error` ("no next active step") if there is none.
- The note body is never augmented with audit text — the `changes` object reports what actually changed instead.
- The note is attached to both the membership's person and holon note feeds (`membership.note_extra_refs()`).

**Response 200:** `MembershipUpdateResponse` — `{membership, note, changes}` where `membership` is a `MembershipItem`, `note` is a `NoteItem`, and `changes` reports `current_step` (by **slug**) and/or `follow_up_after` (ISO dates) as `{old, new}`. `changes` is empty for a note-only update or when submitted values match current values.

**Permissions:** the caller must be able to edit the membership's holon (`can_update_membership` — same check `can_edit_holon` uses for relationships). Account FK ids are never exposed; `responsible`/`author` are projected as `Person` (`responsible_person`, `author_person`) or null.

**Errors:** `400` (empty note, malformed `follow_up_after`, invalid `step_slug`, both step controls supplied, no next active step), `403` permission denied, `404` membership not found.

---

### v1 scope notes

- Read-only except for `POST /api/v1/relationships/{relationship_id}/update` and `POST /api/v1/memberships/{membership_id}/update` — the two write endpoints (note + optional follow-up/step change on an existing relationship or membership).
- No CORS in v1 — designed for server-side AI clients, not browser JS.
- **Authorization is authentication-level on reads, object-scoped on writes.** Any valid token can read every Person/Holon/Membership/relationship/note in the instance — there is no per-record visibility check on `GET` endpoints (including the note feeds). Private fields are dropped at the projection level, but note bodies and follow-up state are fully readable. This is intentional: a token represents a trusted METIS Person with directory-wide read access. The write endpoints, by contrast, require edit access on the relevant holon side — `can_update_relationship` (either side of the relationship) or `can_update_membership` (the membership's holon) — or return `403`.

---

## Endpoints

### `GET /api/agents/{slug}/`

Return a single agent by slug.

| Param  | In   | Type   | Required | Description       |
|--------|------|--------|----------|-------------------|
| `slug` | path | string | yes      | Agent identifier  |

**Response** `200` — `AgentOut`

```json
{
  "slug": "onboarding",
  "name": "Onboarding Agent",
  "prompt": "...",
  "infos": {}
}
```

**Errors:** `404` if the slug does not match any agent.

---

### `POST /api/chat/{agent_slug}/message/` (unauthenticated)

Public web chat endpoint for talking to an agent without API auth.

| Param       | In   | Type   | Required | Description |
|-------------|------|--------|----------|-------------|
| `agent_slug`| path | string | yes      | Target agent slug |

**Request body**

```json
{
  "body": "Hello *world*",
  "visitor_id": null
}
```

| Field       | Required | Notes |
|-------------|----------|-------|
| `body`      | yes      | Human message text. Empty/whitespace-only returns `400`. |
| `visitor_id`| no       | Omit on first message; send previously returned value to continue same thread. |

**Response** `200` — `PublicChatOut`

```json
{
  "visitor_id": "83ac84d2-9f2b-4ba4-8d49-fd5eac15f946",
  "thread_key": "web:visitor:83ac84d2-9f2b-4ba4-8d49-fd5eac15f946:agent:12",
  "human_html": "Hello <i>world</i>",
  "agent_html": "<b>Hi</b> back",
  "created_at": "2026-04-05T10:34:12.412312+00:00"
}
```

The HTML fields use the same Telegram-compatible markdown renderer as bot replies.

**Errors:**
- `400` for empty `body`
- `404` if `agent_slug` does not exist
- `503` if the agent runtime is not configured

---

### `POST /api/hook/agents/{slug}` (unauthenticated)

Receives Telegram webhook updates for an agent. Always returns `{"ok": true}`.

| Param  | In   | Type   | Required | Description       |
|--------|------|--------|----------|-------------------|
| `slug` | path | string | yes      | Agent identifier  |

Behavior:

- For text messages from `private`, `group`, and `supergroup` chats:
  - runs the shared agent chat runtime
  - stores chat notes
  - sends the agent reply back to the originating Telegram chat
  - sends a Q&A mirror message to `agent.config.telegram.echo_channel` (when configured)
- For all other updates, falls back to the raw echo path (best-effort mirror to the echo channel).

---

## Request / Response Schemas

### `PersonOut`

| Field     | Type   | Nullable |
|-----------|--------|----------|
| `id`      | integer| no       |
| `name`    | string | no       |
| `photo`   | string | yes      |
| `contact` | object | no       |

### `AgentOut`

| Field    | Type   | Nullable |
|----------|--------|----------|
| `slug`   | string | no       |
| `name`   | string | no       |
| `prompt` | string | no       |
| `infos`  | object | no       |

### `ConversationPatch` (request body)

| Field             | Type    | Required | Description |
|-------------------|---------|----------|-------------|
| `infos`           | object  | no       | Keys to shallow-merge into `conversation.infos` |
| `expectedVersion` | integer | no       | Optimistic concurrency guard (see PATCH endpoint above) |

### `VersionConflict` (409 response)

| Field            | Type    | Description |
|------------------|---------|-------------|
| `error`          | string  | Always `"version_conflict"` |
| `message`        | string  | Human-readable explanation |
| `currentVersion` | integer | Version currently stored on the server |

---

## Adding a New Endpoint

1. Add the handler to the appropriate router module (or create a new router).
2. Register the router if new.
3. The live OpenAPI schema at `/<api>/openapi.json` is generated automatically — no spec file to edit. Update the relevant `PLAYBOOK.md` only for narrative/auth conventions/gotchas that cannot be expressed in decorators/schemas.
4. URL changes require internal approval before merging.
