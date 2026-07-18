# Extension API Playbook

Authoritative reference for the METIS Chrome Extension API (`/eapi/v1/`).

Live OpenAPI schema: `/eapi/openapi.json` — always in sync with the implementation.

---

## General Conventions

### Authentication

The Chrome extension communicates with METIS via a separate NinjaAPI instance mounted at `/eapi/`. It uses **session cookie auth** (same Django session as the web app, no Bearer token). CSRF is not enforced for `chrome-extension://` origins.

**Source:** `api/extension/api.py`, routers in `api/extension/v1/`

**Auth:** `_EapiSessionAuth` — checks Django session cookie + `request.user.is_authenticated`. The `/session` endpoint opts out (`auth=None`) to return a structured response instead of 401.

### CORS

Browser CORS is enabled for `/eapi/*`.

- Allowed origins come from `CORS_ALLOWED_ORIGINS` (comma-separated env var).
- Allowed methods: `GET, POST, PATCH, OPTIONS`.
- Allowed request headers: `Authorization, Content-Type`.

### Request Headers

All eapi requests from the extension include:

| Header                      | Value                          |
|-----------------------------|--------------------------------|
| `X-Extension-Version`       | `"1.0"`                        |
| `X-Supported-Panel-Versions`| `"1"`                          |

---

## Extension API — `/eapi/v1/`

### Endpoints

#### `GET /api/extension/v1/session` — auth: none

Returns current session state and extension capability metadata. Always 200; use
`user` field to detect authentication.

**Response:**

```json
{
  "authenticated": true,
  "user": { "id": 1, "name": "Jane Doe", "email": "jane@example.com" },
  "server_version": "1",
  "panel_version": "1",
  "extension_latest_version": "1.0.1"
}
```

Or if unauthenticated:

```json
{
  "authenticated": false,
  "user": null,
  "server_version": "1",
  "panel_version": "1",
  "extension_latest_version": "1.0.1"
}
```

---

#### `POST /api/extension/v1/resolve`

Given a LinkedIn URL, returns the matching Metis record (person or holon) if found.

**Request body:**

| Field          | Type   | Required | Description                         |
|----------------|--------|----------|-------------------------------------|
| `linkedin_url` | string | yes      | Raw LinkedIn profile/company URL    |
| `scraped`      | object | no       | Scraped data from the LinkedIn page |

**Response** — `ResolveOut`:

| Field     | Type    | Description                               |
|-----------|---------|-------------------------------------------|
| `found`   | bool    | Whether a matching record exists          |
| `kind`    | string  | `"person"` or `"holon"` (if found)        |
| `id`      | int     | Record PK (if found)                      |
| `name`    | string  | Display name (if found)                   |
| `subtitle`| string  | Role/type line (if found)                 |
| `url`     | string  | Absolute URL to Metis detail page         |
| `photo_url`| string | Avatar/logo URL (if found)                |

---

#### `POST /api/extension/v1/context/summary`

Hydrates METIS IDs declared by a controlled page through `#metis-page-context`.
External pages do not call this endpoint directly; the Chrome extension calls it
through `background.js` so session cookies and CORS stay consistent.

**Request body:**

| Field    | Type        | Required | Description |
|----------|-------------|----------|-------------|
| `people` | array[int]  | no       | METIS `Person.id` values. Duplicates are ignored. |
| `holons` | array[int]  | no       | METIS `Holon.id` values. Duplicates are ignored. |

Maximum accepted IDs: 50 total across `people` and `holons`. Exceeding the cap
returns `400`.

**Response:**

```json
{
  "people": [
    {
      "id": 123,
      "name": "Ada Lovelace",
      "subtitle": "Workshop host",
      "avatar": { "type": "initials", "url": "", "initials": "AL", "color": "#989B4B" },
      "badges": [{ "text": "Person", "tone": "person" }],
      "holons": [{ "id": 44, "name": "Borderland 2026", "type": "event" }]
    }
  ],
  "holons": [
    {
      "id": 44,
      "name": "Borderland 2026",
      "type": "event",
      "type_label": "Event",
      "subtitle": "",
      "avatar": { "type": "initials", "url": "", "initials": "B2", "color": "#989B4B" },
      "badges": [{ "text": "Event", "tone": "holon" }],
      "parent_id": null,
      "parent_name": ""
    }
  ],
  "missing": { "people": [], "holons": [] }
}
```

Missing or deleted IDs are omitted from `people` / `holons` and returned in
`missing`. New optional summary fields may be added without changing the DOM
contract version; extension renderers must ignore unknown fields.

---

#### `GET /api/extension/v1/panel/{kind}/{id}`

Full panel data for a person or holon.

| Param  | In   | Type   | Values              |
|--------|------|--------|---------------------|
| `kind` | path | string | `person` or `holon` |
| `id`   | path | int    | Record PK           |

**Response** — `PanelOut`: entity header + flows section + notes section (first page).

---

#### `GET /api/extension/v1/panel/{kind}/{id}/notes`

Paginated notes for a panel entity.

| Param    | In    | Type   | Description              |
|----------|-------|--------|--------------------------|
| `cursor` | query | string | Pagination cursor (opaque)|

**Response** — `SectionOut`: list of note items + next cursor.

---

#### `POST /api/extension/v1/notes`

Create a note on a person or holon.

**Request body** — `NoteCreateIn`:

| Field      | Type   | Required | Description                            |
|------------|--------|----------|----------------------------------------|
| `flow_ref` | string | yes      | `"person:<id>"` or `"holon:<id>"`      |
| `body`     | string | yes      | Note text (markdown)                   |

**Response** — `NoteCreateOut`:

| Field | Type | Description       |
|-------|------|-------------------|
| `id`  | int  | Created note PK   |

---

#### `PATCH /api/extension/v1/flows/{flow_type}/{flow_id}`

Update journey/step assignment on a person or holon flow.

| Param       | In   | Type   | Values              |
|-------------|------|--------|---------------------|
| `flow_type` | path | string | `person` or `holon` |
| `flow_id`   | path | int    | Flow record PK      |

**Request body** — `FlowPatchIn`:

| Field       | Type | Required | Description             |
|-------------|------|----------|-------------------------|
| `journey_id`| int  | no       | Journey PK to assign    |
| `step_id`   | int  | no       | Step PK within journey  |

**Response** — `FlowPatchOut`: updated flow data.

---

#### `POST /api/extension/v1/entities/person/upsert_from_linkedin`

Create or update a person from scraped LinkedIn data.

**Request body** — `PersonUpsertIn`: scraped profile fields (name, headline, photo_url, linkedin_url, etc.)

**Response** — `EntityUpsertOut`:

| Field     | Type   | Description                     |
|-----------|--------|---------------------------------|
| `id`      | int    | Person PK                       |
| `created` | bool   | True if a new record was made   |
| `url`     | string | Absolute URL to person detail   |

---

#### `POST /api/extension/v1/entities/holon/upsert_from_linkedin`

Same as above for organisations/holons.

**Request body** — `HolonUpsertIn`: scraped company fields.

**Response** — `EntityUpsertOut` (same shape).

---

#### `POST /api/extension/v1/entities/person/{person_id}/memberships`

Add a holon membership to a person. Used by the sidebar's inline Add-Membership
form, which mirrors the Django `person_membership_add` view.

Uniqueness is per `(person, holon, journey)` — the same person/holon pair may
exist across different journeys. On creation, a `FLOW` Note is recorded with
either the supplied `note` body or a default "Membership created: …" summary.

| Param       | In   | Type | Description |
|-------------|------|------|-------------|
| `person_id` | path | int  | Person PK   |

**Request body** — `MembershipCreateIn`:

| Field             | Type         | Required | Description                                                           |
|-------------------|--------------|----------|-----------------------------------------------------------------------|
| `holon_id`        | int          | yes      | Holon PK                                                              |
| `journey_id`      | int \| null  | no       | Person-type Journey PK. Defaults to holon's first person journey.     |
| `current_step_id` | int \| null  | no       | Step PK. Must belong to the selected journey.                         |
| `responsible_id`  | int \| null  | no       | User PK to assign as responsible.                                     |
| `follow_up_after` | string\|null | no       | `YYYY-MM-DD`.                                                          |
| `note`            | string\|null | no       | Optional body for the FLOW note emitted on creation.                  |

**Response** — `MembershipOut`:

| Field           | Type    | Description                                                     |
|-----------------|---------|-----------------------------------------------------------------|
| `membership_id` | int     | Membership PK                                                   |
| `person_id`     | int     | Person PK                                                       |
| `created`       | bool    | `false` if a matching membership already existed                |
| `flow`          | object  | `FlowItemOut` (same shape the `/panel` endpoint returns)        |

---

#### `GET /api/extension/v1/lookups/holons/search`

Search holons for the sidebar picker. Returns up to 30 results.

| Param  | In    | Type   | Description                                 |
|--------|-------|--------|---------------------------------------------|
| `q`    | query | string | Case-insensitive name substring             |
| `type` | query | string | `organisation` \| `local_gathering` \| `camp` \| `domain` |

**Response**: `[{id, name, type, type_display, parent_name}]`.

---

#### `GET /api/extension/v1/lookups/holon/{holon_id}/person-journeys`

Person-type journeys available in a holon's context. Used to populate the
journey dropdown after a holon is picked.

**Response**: `[{id, name, description, color_bg, color_text}]`.

---

#### `GET /api/extension/v1/lookups/journey/{journey_id}/steps`

Non-archived steps for a journey, in `order`. Used to populate the step
dropdown after a journey is picked.

**Response**: `[{id, title, color_bg, color_text, goal, success_criteria}]`.

---

#### `POST /api/extension/v1/matches/confirm`

Confirm that a LinkedIn URL belongs to an existing Metis person or holon.

**Request body** — `MatchConfirmIn`:

| Field          | Type   | Required | Description                           |
|----------------|--------|----------|---------------------------------------|
| `linkedin_url` | string | yes      | LinkedIn URL to confirm               |
| `kind`         | string | yes      | `"person"` or `"holon"`               |
| `id`           | int    | yes      | Metis record PK                       |

**Response** — `MatchConfirmOut`: updated record data.

---

## Outreach eAPI — `/api/extension/v1/outreach/`

All outreach endpoints use session cookie auth. The actor is always the Person
associated with the authenticated user. Router: `api/extension/v1/outreach.py`.

### State machine — SocialConnection

```
unknown → not_connected, requested, active
not_connected → requested
requested → active, cancelled
active → (terminal)
cancelled → (terminal)
```

Invalid transitions return `400`.

### Idempotency — OutreachAction bulk create

Duplicate detection prevents redundant queue entries:

| action_type            | Duplicate if another active action exists with…         |
|------------------------|---------------------------------------------------------|
| `request_connection`   | same `social_connection_id`                             |
| `send_message`         | same `membership_id`                                    |
| `download_profile`     | same `target_person_id` + `network`                     |
| `check_connection_state` | no deduplication                                      |

Active statuses for deduplication: `pending`, `running`, `blocked`, `rate_limited`.

### Endpoints

| Method | Path | Router file | Description |
|--------|------|-------------|-------------|
| `POST` | `/api/extension/v1/outreach/connections/bulk` | `outreach.py` | Upsert connections in bulk |
| `GET`  | `/api/extension/v1/outreach/connections` | `outreach.py` | List connections (filters: network, state) |
| `POST` | `/api/extension/v1/outreach/connections/{id}/transition` | `outreach.py` | Transition connection state |
| `POST` | `/api/extension/v1/outreach/connections/schedule-checks` | `outreach.py` | Create check actions for requested connections |
| `POST` | `/api/extension/v1/outreach/actions/bulk` | `outreach.py` | Create actions in bulk (with idempotency) |
| `GET`  | `/api/extension/v1/outreach/actions` | `outreach.py` | List actions (filters: status, action_type, network) |
| `POST` | `/api/extension/v1/outreach/actions/{id}/claim` | `outreach.py` | Claim a pending action (→ running) |
| `POST` | `/api/extension/v1/outreach/actions/{id}/complete` | `outreach.py` | Report outcome; handles connection transitions and follow-up queueing |
| `GET`  | `/api/extension/v1/outreach/daily-stats` | `outreach.py` | Remaining daily action counts for the actor |
| `GET`  | `/api/extension/v1/outreach/destinations` | `outreach.py` | Events + person journeys + steps for destination picker |
| `GET`  | `/api/extension/v1/outreach/config` | `outreach.py` | Fetch actor's outreach config |
| `PUT`  | `/api/extension/v1/outreach/config` | `outreach.py` | Save actor's outreach config |
| `POST` | `/api/extension/v1/outreach/search-capture` | `outreach_capture.py` | Compound Add flow from search capture |
| `POST` | `/api/extension/v1/outreach/actions/cancel-batch` | `outreach_capture.py` | Cancel all active actions in a batch (Undo) |

### Config storage

Outreach config is stored in `Person.config["outreach"]` (JSONField). The GET
endpoint returns `{}` if no config is set. The PUT endpoint merges at the
`outreach` key only — other `Person.config` keys are unaffected.

Supported config keys:

| Key | Default | Description |
|-----|---------|-------------|
| `daily_request_limit` | `20` | Max `request_connection` actions per day |
| `daily_message_limit` | `100` | Max `send_message` actions per day |
| `daily_download_limit` | `50` | Max `download_profile` actions per day |

### Search Capture compound endpoint

`POST /api/extension/v1/outreach/search-capture` orchestrates the full Add flow in a single call.
Each row in `results` is processed independently (failures do not block others).

**Per-row logic:**
1. Normalise LinkedIn URL → reject if invalid
2. Upsert `Person` (create if not found by `contact.linkedin`; update `description` if blank)
3. Upsert `SocialConnection` (get-or-create; transition state if valid)
4. Get-or-create `Membership` in the destination event/journey/step
5. Queue `request_connection` if `not_connected` and daily limit not exceeded
6. Queue `download_profile` if person is new or `enrich_existing=true` and daily limit not exceeded

**Row status values:** `ok`, `error`, `skipped`, `rate_limited`

**Daily limit enforcement:** The endpoint reads today's `OutreachAction` count from the DB,
tracks remaining slots in memory across rows, and marks excess rows `rate_limited`.

**Batch note:** A `Note` of type `FLOW` is created on the actor person summarising the batch.

### Runner endpoints (Milestone 3)

Router: `api/extension/v1/outreach_runner.py`

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/extension/v1/outreach/actions/next` | Claim next runnable action (priority-ordered, daily-limit aware) |
| `POST` | `/api/extension/v1/outreach/actions/{id}/heartbeat` | Extend the 5-minute claim lease |
| `POST` | `/api/extension/v1/outreach/actions/{id}/requeue` | Re-queue after a transient failure (with retry ceiling) |
| `GET`  | `/api/extension/v1/outreach/actions/stale` | List running actions with no heartbeat for >5 min |
| `POST` | `/api/extension/v1/outreach/person/{id}/enrich` | Write scraped LinkedIn profile data back to Person |

**`actions/next` priority order:**
1. `check_connection_state` (no daily limit)
2. `download_profile`
3. `request_connection`
4. `send_message`

Within each type: `scheduled_for <= now` first, then `created_at ASC`. The response includes
`attempt_count` and `max_attempts` so the runner can surface retry progress.

**Heartbeat / stale detection:** The runner calls `heartbeat` every ~55 s. This issues a
`queryset.update(updated_at=now)` — bypassing `auto_now` — so stale detection is simply
`status=running AND updated_at < now − 5 min`. No schema change required.

**Requeue (transient failure retry):** When the runner hits a transient failure (e.g. a
page-load timeout) it calls `/api/extension/v1/outreach/actions/{id}/requeue` instead of completing with
`failed`. The endpoint increments `attempt_count` and:
- If `attempt_count < RUNNER_MAX_ATTEMPTS`: resets the action to `pending`, bumps
  `scheduled_for` by `RUNNER_REQUEUE_DELAY_SECS` (default 60 s) so other actions get a
  turn first, and clears `started_at`. Returns `gave_up: false`.
- If `attempt_count >= RUNNER_MAX_ATTEMPTS` (default 3): marks the action permanently
  `failed`, sets `completed_at`, and returns `gave_up: true`.

Both `RUNNER_MAX_ATTEMPTS` and `RUNNER_REQUEUE_DELAY_SECS` live in `config/settings/base.py`
and are overridable via env vars.

**`person/enrich` merge rules:** Only writes fields that are currently blank (conservative merge).
Enrichment data lives in `Person.infos["linkedin"]` sub-dict. `description` is updated only
if the new combined headline+about is longer than the current value.

### Cancel batch

`POST /api/extension/v1/outreach/actions/cancel-batch` sets all `ACTIVE_STATUSES` actions matching
the `batch_id` and `actor_person` to `cancelled`. Used by the extension's "Undo last batch".

### Connection checking and follow-up (Milestone 4)

Router: `api/extension/v1/outreach.py`

**`POST /api/extension/v1/outreach/connections/schedule-checks`**

Creates `check_connection_state` actions for `SocialConnection` records in `requested` state.
- `min_age_days` (default: 3) — only include connections requested at least this many days ago.
  Set to 0 to bypass the age filter (individual "Check" button use-case).
- `connection_ids` — optional list of connection PKs; when present, only those connections are
  scheduled regardless of other filters.
- Idempotent: connections that already have an active `check_connection_state` action are skipped.
- Carries the `membership` forward from the original `request_connection` action so the follow-up
  logic in `action_complete` can find the step's `starter_message`.
- Returns `{ created: int, skipped: int }`.

**Extended `POST /api/extension/v1/outreach/actions/{id}/complete`**

`new_connection_state` (optional field) tells the backend the detected LinkedIn state:
- For any action with `social_connection_id` + `status=done`: the backend applies the state
  transition via `can_transition_to()` if valid.
- For `check_connection_state` + `new_connection_state=active` specifically:
  1. Transitions `SocialConnection` → `active`, sets `connected_at`.
  2. Finds the linked `Membership` (from the action's `membership`, or falls back to the
     most recent `request_connection` action for the same social connection).
  3. If `membership.current_step.starter_message` is non-blank, creates a `send_message`
     `OutreachAction` with the message snapshotted at acceptance time.
  4. Creates a "LinkedIn connection accepted." `Note` on the target `Person`.
  5. If a follow-up was queued: creates a "Follow-up message queued…" `Note`.
  6. Returns `{ action: OutreachAction, queued_follow_up: OutreachAction | null }`.

The response schema changed from `OutreachAction` to `ActionCompleteOut` (additive change).
Old clients that ignore unknown fields are unaffected.

**Message snapshot timing:** `starter_message` is read at the moment the connection is
accepted — not when the request was sent. Edits to the step's message between request and
acceptance are reflected in the follow-up.

**No step advancement:** Accepting a connection and queueing the follow-up does NOT advance
the Membership to the next journey step. Step management remains a manual METIS workflow concern.
