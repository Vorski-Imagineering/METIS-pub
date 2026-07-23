# App API Playbook — `/api/`

Reference for the `/api/` surface: the service endpoints that METIS's own apps expose
for their operational needs — agent records and integration webhooks here, Coherence
in [`coherence-PLAYBOOK.md`](coherence-PLAYBOOK.md).

**If you are integrating with METIS from outside, you want `/api/v1/` instead** — the
open API, documented in [`API.md`](API.md). Despite the paths, `/api/v1/` is a
separate surface rather than a version of this one, and the two do not share
authentication. See the summary [below](#api-v1--apiv1).

**Live schema:** `/api/openapi.json` — **Swagger UI:** `/api/docs`

---

## General Conventions

These conventions describe `/api/` only. `/api/v1/` has its own auth, error envelope
and conventions — see [`API.md`](API.md).

### Authentication

Endpoints on this surface take the shared bearer token unless noted otherwise:

```
Authorization: Bearer <API_TOKEN>
```

Endpoints whose writes must be attributable to a specific person instead require a
per-user token, obtained from `POST /api/v1/auth/login` and sent the same way; those
are marked where they appear. Webhook endpoints (`/api/hook/*`, `/api/coherence/hook/*`)
are unauthenticated and verify the caller by other means.

Browser session cookies do **not** authenticate any endpoint on this surface.

### CORS

Browser CORS is enabled for `/api/*`.

- Allowed origins come from `CORS_ALLOWED_ORIGINS` (comma-separated env var).
- Allowed methods: `GET, POST, PUT, PATCH, OPTIONS`.
- Allowed request headers: `Authorization, Content-Type`.
- Preflight `OPTIONS` requests return CORS headers for allowed origins.

Credentials are not allowed, so a cross-origin browser cannot send a session cookie here.

### Routing

| Prefix              | Auth                                     | Documented in |
|---------------------|------------------------------------------|---------------|
| `/api/agents`       | Bearer (shared `API_TOKEN`)              | this file |
| `/api/chat`         | None (visitor-facing)                    | this file |
| `/api/hook`         | None (webhook)                           | this file |
| `/api/coherence`    | Bearer (shared `API_TOKEN`) or per-user token | [`coherence-PLAYBOOK.md`](coherence-PLAYBOOK.md) |

### Response shapes

- Top-level responses use typed Ninja `Schema` classes (no raw dicts).
- Nullable fields use `Optional[T] = None`.
- No deep nesting beyond one level.
- List endpoints return `[]` when nothing matches (not 404).

### Side effects

- `GET` endpoints do **not** create records unless explicitly documented (the one
  exception is `GET /api/coherence/conversations` — see
  [`coherence-PLAYBOOK.md`](coherence-PLAYBOOK.md)).
- Notes created by the system rather than by a person are recorded with no author.

---

## API v1 — `/api/v1/`

The open API for external systems integrating with METIS lives at `/api/v1/`, and is
documented in full in [`API.md`](API.md): authentication, the error envelope, the
access model, every endpoint, and the public field projections.

It is a separate surface from the one this playbook covers, with its own
authentication — neither the shared `API_TOKEN` nor a browser session authenticates
`/api/v1/`. App-owned parts of it are documented by their owning app:
[`outreach-PLAYBOOK.md`](outreach-PLAYBOOK.md) for `/api/v1/outreach/*`.

**Live schema:** `/api/v1/openapi.json` — **Swagger UI:** `/api/v1/docs`

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

Web-channel endpoint for talking to an agent. Unauthenticated because visitors
have no account — not because the exchange is throwaway: each message is
recorded on the agent's chat record (a `NoteThread`, the same one the Telegram
channel writes) and feeds agent memory. `visitor_id` is what keeps a visitor's
successive messages on one thread.

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

**Response** `200` — `AgentChatOut`

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

### `AgentOut`

| Field    | Type   | Nullable |
|----------|--------|----------|
| `slug`   | string | no       |
| `name`   | string | no       |
| `prompt` | string | no       |
| `infos`  | object | no       |

Coherence's own schemas — the person shape it returns, the conversation patch body,
and the `version_conflict` 409 — are documented with the endpoints that use them in
[`coherence-PLAYBOOK.md`](coherence-PLAYBOOK.md). The live schema at
`/api/openapi.json` is authoritative for every shape on this surface.
