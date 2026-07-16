# Coherence API Playbook

---

## Assumptions

The following were inferred from code, not from explicit configuration:

- **`API_TOKEN`** is a static shared secret stored in Django settings. No token rotation or per-client tokens observed.
- **`ConversationOut.journey_slug / journey_name / step_slug / step_title`** are resolved from the ORM relation at serialisation time. They may be empty strings if the conversation has no journey/step set.
- **Operational conversation endpoints** return both `infos` and `config`. Browse endpoints return publishable metadata only and do not expose internal `config`.
- **Browse endpoints** return a separate public conversation shape and do **not** expose raw `conversation.infos` or internal `conversation.config`.
- **The list endpoint** (`GET /api/coherence/conversations`) returns all matching results in one response — there is no `limit`/`offset` param. Scope queries with `person_id`/`journey`/`time` to keep result sets small.
- **Error format** for Django Ninja endpoints follows Ninja's default: `{"detail": "..."}` for 404s and `{"detail": [...]}` for 422 validation errors.

---

## Base URLs

| Environment | Base URL |
|-------------|----------|
| Dev / staging | `https://dev.the-gathering.earth/` |
| Production  | `https://app.the-gathering.earth/` |

All endpoints live under `/api/coherence/`.

---

## Machine-readable spec / interactive docs

Coherence routes are mounted on the same shared `NinjaAPI` instance as the rest of the
Core API (`/api/coherence/...` alongside `/api/...`), so they're covered by the same
live, always-current OpenAPI document — there is no separate hand-maintained Coherence
spec file.

| What | Dev / staging | Production |
|------|----------------|------------|
| Interactive Swagger UI (try endpoints in the browser) | `https://dev.the-gathering.earth/api/docs` | `https://app.the-gathering.earth/api/docs` |
| Raw OpenAPI JSON | `https://dev.the-gathering.earth/api/openapi.json` | `https://app.the-gathering.earth/api/openapi.json` |

This `PLAYBOOK.md` stays as the narrative companion (golden paths, algorithms, field
reference) for things that don't fit cleanly in a schema — the OpenAPI doc is the
source of truth for exact request/response shapes.

---

## Authentication

Most endpoints accept any of: `Authorization: Bearer <API_TOKEN>` (a static shared secret set
by `settings.API_TOKEN`, no expiry), an authenticated Django session (web app/extension), or a
per-user API token (see below) — whichever the caller has.

The discovery and media endpoints — `/conversation-events`, `/conversations/search`,
transcript replacement, and audio upload/download — are the exception: they reject `API_TOKEN`
and the session cookie, and require a per-user API token, because writes on these endpoints are
attributed to a real person. Obtain one via the shared `/api/v1/` auth flow:

```bash
curl -X POST "https://dev.the-gathering.earth/api/v1/auth/login" \
  -H "X-Metis-Api-Key: <API_LOGIN_SECRET>" \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "..."}'
# => {"token": "metis_agentic_<id>_<secret>", "token_type": "Bearer", "expires_in_seconds": 86400, ...}
```

Then send that token as the Bearer credential on Coherence requests:

```bash
curl "https://dev.the-gathering.earth/api/coherence/conversation-events" \
  -H "Authorization: Bearer metis_agentic_<id>_<secret>"
```

The token is valid for 24 hours and can be revoked early via `POST /api/v1/auth/logout`. See
`api/agentic/router.py` for the full login/logout contract.

## CORS

Browser CORS is enabled for API routes only (`/api/*`).

- Allowed origins come from `CORS_ALLOWED_ORIGINS` (comma-separated env var).
- Allowed methods: `GET, POST, PUT, PATCH, OPTIONS`.
- Allowed request headers: `Authorization, Content-Type`.
- Preflight `OPTIONS` requests include CORS headers for allowed origins.

**Example:**
```bash
curl "https://dev.the-gathering.earth/api/coherence/conversations?person_id=42&journey=coherence-check&time=2026-03-01T14%3A30%3A00Z" \
  -H "Authorization: Bearer mysecrettoken"
```

---

## Global Rules

### Error format

Django Ninja errors follow this envelope:

```json
// 404
{"detail": "Not Found"}

// 400 – invalid query combination
{"detail": "Provide exactly one of journey_id or journey_slug."}

// 422 – validation failure
{
  "detail": [
    {"loc": ["query", "person_id"], "msg": "field required", "type": "missing"}
  ]
}
```

Application-level errors (version conflicts, invalid batch input, RealtimeKit metadata
issues, namespace placement) use a separate `{"error": "...", "message": "..."}` envelope
instead of Ninja's default `{"detail": ...}`. See each endpoint's Golden Path section below
for the exact `error` codes it can return.

### Datetime format

All datetimes are **ISO 8601 with UTC timezone**:
```
2026-03-01T14:00:00Z
```

### ID format

All IDs are **positive integers** (PostgreSQL bigint PKs). Slugs (e.g. journey slug) are URL-safe strings generated by Django's `slugify`.

---

## Discover Conversation Events and conversations

```text
GET /api/coherence/conversation-events
GET /api/coherence/conversation-events?holon_slug={holon_slug}

GET /api/coherence/conversations/search
GET /api/coherence/conversations/search?holon_slug={holon_slug}
GET /api/coherence/conversations/search?connected_holon_slug={holon_slug}
GET /api/coherence/conversations/search?person_id={person_id}
GET /api/coherence/conversations/search?sort=date_asc
```

These discovery endpoints require a per-user API token (see Authentication above); the shared `API_TOKEN` is not accepted.

`/conversation-events` lists every Coherence Conversation Event. Supplying
`holon_slug` narrows it to that holon when it is an event plus every Conversation
Event in its descendant tree.

`/conversations/search` is the side-effect-free operational list endpoint: no
filters returns every conversation, including scheduled, unscheduled, active,
and completed rows. It never creates a conversation.

Its optional filters combine with **AND**:

- `holon_slug`: conversation ownership—`Conversation.event` is this holon or
  one of its descendants;
- `connected_holon_slug`: participation—the conversation is explicitly linked
  to this holon through `Conversation.connected`;
- `person_id`: the Person is in `Conversation.participants`.

`sort` orders by `start`: `date_desc` is the default (newest first), and
`date_asc` is oldest first. Conversations without a start date are always last;
ID is the stable tie-breaker.

Ownership and participation are intentionally separate. An Event owns a
conversation through `Conversation.event`; `connected` is supplementary
involvement and does not change that owner.

Each search item includes its event, journey/step, time bounds, Persons, and
connected Holons, but deliberately excludes raw `infos`, `config`, and
transcript content. Missing filter targets return 404; valid filters with no
matches return `[]`.

---

## Replace a conversation transcript

```text
PUT /api/coherence/conversations/{conversation_id}/transcript/segments
Authorization: Bearer <per-user token from POST /api/v1/auth/login>
Content-Type: application/json
```

Replace all normalized `TranscriptSegment` rows for a conversation. This is a
destructive, full-replacement operation—not an append or patch.

Each successful replacement adds a Conversation note with the acting user and segment count.

```json
{
  "segments": [
    {
      "person_id": 52,
      "text": "A time-coded utterance.",
      "offset_ms": 14320,
      "question_id": 3
    }
  ]
}
```

The batch must contain 1–50 segments. Every segment requires a non-zero integer
`person_id` (negative IDs are valid unresolved speakers), non-blank `text`, and
`offset_ms >= 0`. `question_id` is optional but must refer to an existing
Question. The server validates the full request before deleting current rows;
invalid input returns `400 {"error":"invalid_transcript_segments","message":"…"}`
and preserves the existing transcript. Success returns `200 {"replaced": N}`.

A later Cloudflare provider or Chirp import replaces these rows again. The endpoint
does not delete the downloaded raw transcript JSON or change IRIS download metadata.
Repeated identical requests produce the same transcript content, but new segment
row IDs and creation timestamps.

---

## Upload or download conversation audio

```text
POST /api/coherence/conversations/{conversation_id}/audio
Authorization: Bearer <per-user token from POST /api/v1/auth/login>
Content-Type: multipart/form-data

audio=@conversation.wav
```

Uploads and replaces the conversation's canonical sound file. Supported extensions
are `aac`, `flac`, `m4a`, `mp3`, `oga`, `ogg`, `opus`, `wav`, and `webm`; the maximum
size is 500 MiB. A successful upload returns `201` with the `infos["audio"]`
metadata (`path`, `name`, `content_type`, `size_bytes`, `source`, `created_at`).
Invalid extensions, empty files, and oversized files return
`400 {"error":"invalid_conversation_audio","message":"…"}` and leave the
previous audio metadata/file intact.

Each successful upload adds a Conversation note with the acting user, filename, and byte count.

```text
GET /api/coherence/conversations/{conversation_id}/audio
Authorization: Bearer <per-user token from POST /api/v1/auth/login>
```

Streams the stored canonical audio file through the authenticated API. It returns
404 when the conversation has no audio metadata or the referenced managed file is
missing. This avoids exposing an unauthenticated `/media/` URL.

When a conversation has no uploaded audio, `GoogleTranscribe` extracts and stores
a FLAC from the downloaded recording before sending it to Chirp. A later upload
becomes the canonical audio used by a future Chirp run; it does not rewrite the
existing transcript automatically.

---

## Algorithm: "Is a conversation active now for this journey?"

The `GET /api/coherence/conversations` endpoint determines whether a conversation is "active" at a given point in time using this filter:

```python
CoherenceConversation.objects.filter(
    participants__id=person_id,
    journey__slug=journey,
    start__lte=time + timedelta(minutes=5),
).filter(Q(finish__gte=time) | Q(finish__isnull=True))
```

**Three conditions must all be true:**

1. `participants__id=person_id` — the given person is a participant in the conversation.
2. `journey__slug=journey` — the conversation belongs to the requested journey slug.
3. `start__lte=time + timedelta(minutes=5)` — the conversation starts no later than 5 minutes after `time`. This means a caller querying up to 5 minutes **before** the scheduled start will still get a match.
4. `finish__gte=time OR finish IS NULL` — the conversation has not yet finished at `time`, or it is open-ended.

**In plain terms:** a conversation is returned if the person is a participant, the conversation belongs to the requested journey, it has not ended, and it either has already started or starts within the next 5 minutes.

**In simple terms:** Imagine a meeting on a calendar. You walk up to the room and ask "is my coherence-check conversation happening right now?" The answer is yes if: (1) your name is on the invite, (2) it is for that journey, (3) the meeting hasn't finished yet, and (4) it either already started or starts in the next 5 minutes. We allow the 5-minute early window so an agent connecting just before the scheduled time still finds the conversation.

**Edge cases:**
- If `start` is `null`, that conversation will never match.
- If `finish` is `null`, that conversation can still match because the endpoint treats it as open-ended.
- The 5-minute early window is hardcoded; it cannot be overridden by the caller.
- The `time` parameter is supplied by the caller — it is not server-side "now".
- If no conversation matches, the endpoint creates and returns a new unscheduled conversation for that journey.

---

## Golden Path: Find the current conversation for a person

```bash
curl "https://dev.the-gathering.earth/api/coherence/conversations?person_id=42&journey=coherence-check&time=2026-03-01T14%3A30%3A00Z" \
  -H "Authorization: Bearer mysecrettoken"
```

```json
[
  {
    "id": 7,
    "participants": [
      {"id": 42, "name": "Alice Ferreira", "photo": null, "contact": {"email": "alice@example.com"}},
      {"id": 18, "name": "Bob Silva",      "photo": "/media/people/bob.jpg", "contact": {}}
    ],
    "connected": [
      {"id": 3, "name": "⬢ Global", "type": "domain", "slug": "global"}
    ],
    "infos": {"publishing": {"youtube": {"title": "Conversation trailer"}}},
    "config": {"cal.com": {"bookingId": "abc123xyz"}},
    "start":  "2026-03-01T14:00:00Z",
    "finish": "2026-03-01T15:00:00Z",
    "journey_slug": "coherence-check",
    "journey_name": "Coherence Check",
    "step_slug":    "scheduled",
    "step_title":   "Scheduled"
  }
]
```

If nothing matches, the endpoint creates a new unscheduled conversation for that person and journey instead of returning an empty array.

---

## Golden Path: Fetch a single conversation by ID

```bash
curl "https://dev.the-gathering.earth/api/coherence/conversations/7" \
  -H "Authorization: Bearer mysecrettoken"
```

Returns a single `ConversationOut` object (same shape as items in the list endpoint), or 404 if not found.

---

## Golden Path: Browse child events and available journeys for a holon

```bash
curl "https://dev.the-gathering.earth/api/coherence/browse/holons/gathering-2026" \
  -H "Authorization: Bearer mysecrettoken"
```

```json
{
  "holon": {
    "id": 1,
    "slug": "gathering-2026",
    "name": "Gathering 2026",
    "type": "domain"
  },
  "events": [
    {
      "id": 10,
      "slug": "opening-weekend",
      "name": "Opening Weekend",
      "type": "event",
      "journeys": {
        "scope": "direct",
        "items": [
          {
            "id": 5,
            "slug": "speaker-interview",
            "name": "Speaker Interview",
            "description": "Recorded speaker interview",
            "source": "direct"
          }
        ]
      }
    },
    {
      "id": 11,
      "slug": "story-lab",
      "name": "Story Lab",
      "type": "event",
      "journeys": {
        "scope": "direct",
        "items": []
      }
    }
  ]
}
```

Rules:

- The endpoint uses the requested holon's immediate child events only
- It returns only conversation journeys directly attached to each event
- No parent inheritance or fallback lookup is applied here

---

## Golden Path: Browse conversations for a journey

```bash
curl "https://dev.the-gathering.earth/api/coherence/browse/conversations?journey_slug=speaker-interview" \
  -H "Authorization: Bearer mysecrettoken"
```

```json
{
  "journey": {
    "id": 5,
    "slug": "speaker-interview",
    "name": "Speaker Interview",
    "description": "Recorded speaker interview",
    "texts": {
      "intro": "Welcome"
    }
  },
  "conversations": [
    {
      "id": 101,
      "title": "Interview with Alice",
      "start": "2026-04-03T09:00:00Z",
      "finish": "2026-04-03T10:00:00Z",
      "step": {
        "slug": "recorded",
        "title": "Recorded"
      },
      "participants": [
        {"id": 42, "name": "Alice Ferreira", "photo": "/media/people/alice.jpg"}
      ],
      "connected": [
        {"id": 10, "slug": "opening-weekend", "name": "Opening Weekend", "type": "event"}
      ],
      "publishing": {
        "summary": {"text": "Short public summary"},
        "thumbnails": [{"url": "/media/coherence/thumbs/direct.jpg"}],
        "youtube": {"description": "Long external description"}
      },
      "public": {
        "summary": "Short public summary",
        "thumbnail": "/media/coherence/thumbs/direct.jpg",
        "youtube_description": "Long external description"
      }
    }
  ]
}
```

Rules:

- Provide exactly one of `journey_id` or `journey_slug`
- Without `holon_slug`, the endpoint returns all conversations for that journey
- `holon_slug` is optional; when provided, it filters to conversations connected to that event holon
- Conversations not connected to any holon are included only in the unfiltered journey-wide call
- Results are ordered newest first by `start`, then by `id`
- Raw `infos` is intentionally not returned

Example with event filter:

```bash
curl "https://dev.the-gathering.earth/api/coherence/browse/conversations?journey_slug=speaker-interview&holon_slug=opening-weekend" \
  -H "Authorization: Bearer mysecrettoken"
```

---

## Golden Path: Browse all child-event journey conversations for a holon

```bash
curl "https://dev.the-gathering.earth/api/coherence/browse/holons/gathering-2026/conversations" \
  -H "Authorization: Bearer mysecrettoken"
```

```json
{
  "holon": {
    "id": 1,
    "slug": "gathering-2026",
    "name": "Gathering 2026",
    "type": "domain"
  },
  "events": [
    {
      "id": 10,
      "slug": "opening-weekend",
      "name": "Opening Weekend",
      "type": "event",
      "journeys": [
        {
          "journey": {
            "id": 5,
            "slug": "speaker-interview",
            "name": "Speaker Interview",
            "description": "Recorded speaker interview",
            "texts": {"intro": "Welcome"}
          },
          "conversations": [
            {
              "id": 101,
              "title": "Interview with Alice",
              "start": "2026-04-03T09:00:00Z",
              "finish": "2026-04-03T10:00:00Z",
              "step": {"slug": "recorded", "title": "Recorded"},
              "participants": [
                {"id": 42, "name": "Alice Ferreira", "photo": "/media/people/alice.jpg"}
              ],
              "connected": [
                {"id": 10, "slug": "opening-weekend", "name": "Opening Weekend", "type": "event"}
              ],
              "publishing": {
                "summary": {"text": "Short public summary"},
                "thumbnails": [{"url": "/media/coherence/thumbs/direct.jpg"}],
                "youtube": {"description": "Long external description"}
              },
              "public": {
                "summary": "Short public summary",
                "thumbnail": "/media/coherence/thumbs/direct.jpg",
                "youtube_description": "Long external description"
              }
            }
          ]
        }
      ]
    },
    {
      "id": 11,
      "slug": "story-lab",
      "name": "Story Lab",
      "type": "event",
      "journeys": []
    }
  ]
}
```

Rules:

- The endpoint uses the requested holon's immediate child events only
- For each child event, it includes only conversation journeys directly attached to that event
- A conversation appears in a group only if it is connected to that event and its journey is attached to that event
- Conversations connected to a child event but using some other journey are excluded from that event's groups
- Inherited journeys are not included here, and the overview endpoint also stays direct-only

---

## Golden Path: Batch lookup persons by IDs

```bash
curl "https://dev.the-gathering.earth/api/coherence/browse/persons?ids=42,18,7" \
  -H "Authorization: Bearer mysecrettoken"
```

```json
[
  {"id": 42, "name": "Alice Ferreira", "photo": "/media/people/alice.jpg", "contact": {"email": "alice@example.com"}},
  {"id": 18, "name": "Bob Silva", "photo": null, "contact": {}},
  {"id": 7, "name": "Carol Dias", "photo": "/media/people/carol.jpg", "contact": {"telegram": "@carol"}}
]
```

Rules:

- Pass a comma-separated list of integer IDs via the `ids` query parameter
- Maximum 50 IDs per request
- Unknown IDs are silently skipped — no 404 for missing persons
- Order of results is not guaranteed

---

## Golden Path: Batch lookup holons by IDs

```bash
curl "https://dev.the-gathering.earth/api/coherence/browse/holons?ids=10,1" \
  -H "Authorization: Bearer mysecrettoken"
```

```json
[
  {
    "id": 10,
    "slug": "opening-weekend",
    "name": "Opening Weekend",
    "type": "event",
    "description": "The opening weekend of the gathering",
    "logo": "/media/holons/logos/opening.jpg",
    "links": {"website": "https://example.com"},
    "infos": {"locations": [1, 2]}
  },
  {
    "id": 1,
    "slug": "gathering-2026",
    "name": "Gathering 2026",
    "type": "domain",
    "description": "",
    "logo": null,
    "links": {},
    "infos": {}
  }
]
```

Rules:

- Pass a comma-separated list of integer IDs via the `ids` query parameter
- Maximum 50 IDs per request
- Unknown IDs are silently skipped — no 404 for missing holons
- Returns full public holon data: description, logo, links, infos
- Order of results is not guaranteed

---

## Golden Path: Update a conversation's infos

Once an agent has found the conversation via the list endpoint, it can attach data to `infos`:

```bash
curl -X PATCH "https://dev.the-gathering.earth/api/coherence/conversations/7" \
  -H "Authorization: Bearer mysecrettoken" \
  -H "Content-Type: application/json" \
  -d '{
    "infos": {"agent_notes": "User seemed engaged"}
  }'
```

Returns the full updated `ConversationOut`. `infos` and `config` are both **shallow-merged** when provided.

### Some namespaces are forbidden here entirely

`infos` and `config` are separate stores by convention (see `CONVERSATION_JSON_FIELDS.md`):
`config` = operational/pipeline state, `infos` = output content. Namespaces that have their own
dedicated, correct-by-construction endpoint — or are written internally only — are rejected
**regardless of which field you address them under**, not just when misplaced:

```bash
curl -X PATCH "https://dev.the-gathering.earth/api/coherence/conversations/7" \
  -H "Authorization: Bearer mysecrettoken" \
  -H "Content-Type: application/json" \
  -d '{
    "config": {"enter-coherence": {"phase": "exit-lounge"}}
  }'
# 400 {"error": "invalid_namespace_placement", "message": "'\''enter-coherence'\'' cannot be written via this endpoint — use PATCH /conversations/{id}/enter-coherence instead"}
```

| Namespace | Rule |
|-----------|------|
| `enter-coherence` | Forbidden here in either field. Use `POST/GET /conversations/{id}/enter-coherence` (below) — the only endpoint that may write it. |
| `cal.com`, `iris.*` | Forbidden here in either field. Written internally only (webhook / Iris pipeline) — no client should ever send these. |
| `publishing`, `publishing_approval`, `publishing_status` | Must be written via `infos`, not `config` (still just a placement check — no dedicated endpoint yet). |

Namespaces not in this table are still accepted in either field. The same rules apply to
`POST .../recorded`.

This replaced an earlier, weaker version of this check that only validated *placement*
(reject `enter-coherence` under `infos`, still allow it under `config`) — that version still let
`enter-coherence` PartyKit silently drift the same room state between `infos` and `config` across
requests, since it could still address `config['enter-coherence']` directly through this generic
endpoint. Giving it a narrow endpoint that can only ever touch that one sub-object closes the
mistake structurally instead of merely detecting it.

---

## Golden Path: Upsert enter-coherence room state + RealtimeKit metadata

`POST/GET /conversations/{id}/enter-coherence` is the **sole owner of
`config['enter-coherence']`** — the only endpoint that may write it. `enter-coherence` PartyKit
uses it for two purposes that used to go through two different paths (generic `PATCH` for
room state, a since-removed `/realtimekit` endpoint for meeting metadata) and now share one:

- **Room state** — `phase`, `claims`, `version` (with `expectedVersion` for optimistic concurrency).
- **RealtimeKit metadata** — `meetingId`, `recordingId`, `recordingEndedAt`,
  `participants`, so METIS can recover the post-meeting transcript. The canonical
  **session id is derived server-side** from Cloudflare (see below) — it is not
  accepted from the client.

> **`sessionId` is ignored.** METIS derives the canonical session from
> Cloudflare (list the meeting's sessions, pick the real recorded one); the old client-supplied `sessionId`, read off the
> browser SDK, was unreliable and caused conv-220's empty-transcript defect.
> **Sending `sessionId` is accepted but ignored** — the value is never stored, so
> a legacy client still sending it keeps working. Stop sending it; a future
> release may remove the field. Any previously stored `sessionId` is scrubbed on
> the next write.

```bash
curl -X POST "https://dev.the-gathering.earth/api/coherence/conversations/456/enter-coherence" \
  -H "Authorization: Bearer mysecrettoken" \
  -H "Content-Type: application/json" \
  -d '{
    "phase": "conversation",
    "version": 4,
    "expectedVersion": 3,
    "claims": {"Alice": {"personId": 123, "claimedAt": "2026-07-07T17:56:00.000Z"}},
    "meetingId": "bbb8940e-1b97-402a-97d6-2708b7feca41",
    "participants": [
      {
        "browserSessionId": "browser-session-id",
        "personId": 123,
        "displayName": "Alice",
        "realtimeKitParticipantId": "rtk-participant-id",
        "customParticipantId": "coherence:coherence-456:browser-session-id",
        "assignedAt": "2026-07-07T17:56:00.000Z",
        "lastCredentialIssuedAt": "2026-07-07T17:56:00.000Z"
      }
    ]
  }'
```

Returns `{"ok": true, "conversationId": 456, "meetingId": "...", "version": 4, "phase": "conversation", "participantCount": 1}`.

Rules:
- **Every field is optional** and merged individually — send only what changed. `meetingId` may
  be absent at first (e.g. writing `phase` before a RealtimeKit meeting exists) and supplied later.
- **Scalar fields never erase a previously stored non-null value** when omitted/null: `recordingId`,
  `recordingEndedAt`. `phase`/`version` simply take the latest provided value (they're
  live state, not durable IDs).
- **Optimistic concurrency guard (`expectedVersion`):** if provided, the server checks that the
  current `config['enter-coherence'].version` matches it before writing. On mismatch, returns
  **409** `version_conflict` with `currentVersion` — fetch the latest state and retry. Omit to
  write unconditionally. First write (no `enter-coherence` yet) is accepted regardless of
  `expectedVersion`.
- **`claims` upsert per display-name key** (shallow-merged) — writing one claim never erases
  another.
- **`participants` upsert by `customParticipantId`.** Resending the same `customParticipantId`
  with a new `realtimeKitParticipantId` updates the participant id and `lastCredentialIssuedAt`
  (covers token-refresh recreation) but keeps the original `assignedAt`.
- **Meeting conflict:** if a different `meetingId` is already stored for this conversation, the
  call returns **409** `meeting_conflict` with `currentMeetingId` and writes nothing.
- Does **not** advance the journey step.

Diagnostics lookup:

```bash
curl "https://dev.the-gathering.earth/api/coherence/conversations/456/enter-coherence" \
  -H "Authorization: Bearer mysecrettoken"
```

Returns the currently stored `meetingId`/`recordingId`/`version`/`phase`/`claims`/`participants` (null/empty if nothing has been written yet). `sessionId` is not returned — it is derived, not stored.

---

## Golden Path: Mark a conversation as recorded

After the conversation recording is complete, call this endpoint to advance the journey to the next step and log a note. You can optionally update `infos` and/or `config` with the same shallow-merge semantics as PATCH.

```bash
curl -X POST "https://dev.the-gathering.earth/api/coherence/conversations/7/recorded" \
  -H "Authorization: Bearer mysecrettoken" \
  -H "Content-Type: application/json" \
  -d '{
    "infos": {"recording_url": "https://example.com/rec/abc123"}
  }'
```

Returns the full updated `ConversationOut` with the step advanced. If the conversation is already on the last step, the note is still created but the step remains unchanged.

**Note:** This endpoint is not idempotent — calling it twice will advance the step twice (if further steps exist) and create two notes.

---

## cal.com booking webhook

Unauthenticated endpoint that receives cal.com booking webhooks for a specific person. Register the URL as the cal.com webhook destination, e.g. `https://dev.the-gathering.earth/api/coherence/hook/cal.com/42`.

```bash
curl -X POST "https://dev.the-gathering.earth/api/coherence/hook/cal.com/42" \
  -H "Content-Type: application/json" \
  -d '{ "triggerEvent": "BOOKING_CREATED", ... }'
```

Always returns `{"ok": true}` — errors are logged, not surfaced. No auth required.

Handled events (via `triggerEvent` in the request body):

| Event                  | Action                                                                 |
|------------------------|------------------------------------------------------------------------|
| `BOOKING_CREATED`      | Creates a new conversation, adds participants, attaches a note.        |
| `BOOKING_RESCHEDULED`  | Updates `start`/`finish` on the existing conversation, attaches a note.|
| `BOOKING_CANCELLED`    | Attaches a cancellation note, then deletes the conversation.           |

Journey is resolved from the `videoCallUrl` in the payload metadata. If the slug doesn't match a `CONVERSATION`-type journey, an error note is attached to the person and no conversation is created.

A `GET` on the same path returns a plain-text activation hint and is used when registering the destination in cal.com.

---

## ConversationOut field reference

| Field                 | Type              | Nullable | Notes |
|-----------------------|-------------------|----------|-------|
| `id`                  | integer           | no       | |
| `participants`        | list[PersonOut]   | no       | |
| `connected`           | list[object]      | no       | Each has `id`, `name`, `type`, `slug` |
| `infos`               | object            | no       | Public/display metadata; publishing artefacts live under `infos["publishing"]` |
| `config`              | object            | no       | Internal/operational metadata; cal.com, Enter Coherence, and Iris state live here |
| `start`               | datetime          | yes      | ISO 8601 UTC |
| `finish`              | datetime          | yes      | ISO 8601 UTC |
| `journey_slug`        | string            | no       | |
| `journey_name`        | string            | no       | |
| `journey_description` | string            | yes      | |
| `step_slug`           | string            | no       | |
| `step_title`          | string            | no       | |
| `texts`               | object            | no       | Keys: `welcome`, `enter`, `post`, `goodbyeURL`; empty `{}` if not configured |
| `questions`           | list[Question]    | no       | Ordered by journey question sequence; each has `id` and `text` |

---

## JourneyConversationBrowse field reference

| Field | Type | Nullable | Notes |
|-------|------|----------|-------|
| `journey.id` | integer | no | |
| `journey.slug` | string | no | |
| `journey.name` | string | no | |
| `journey.description` | string | no | Empty string if not set |
| `journey.texts` | object | no | From `journey.config["texts"]`; empty `{}` if not configured |
| `conversations[].id` | integer | no | |
| `conversations[].title` | string | no | Uses `publishing.youtube.title` when present, else a server-generated fallback |
| `conversations[].start` | datetime | yes | ISO 8601 UTC |
| `conversations[].finish` | datetime | yes | ISO 8601 UTC |
| `conversations[].step` | object | no | `slug` and `title` of the current step; empty strings if unset |
| `conversations[].participants` | list[PublicPerson] | no | Name, optional photo, and contact dict |
| `conversations[].connected` | list[HolonRef] | no | Minimal connected holons |
| `conversations[].publishing` | object | no | Full public publishing payload from `infos["publishing"]` |
| `conversations[].public.summary` | string | yes | From `infos["publishing"]["summary"]["text"]` |
| `conversations[].public.thumbnail` | string | yes | First thumbnail URL from `infos["publishing"]["thumbnails"]`, or `infos["publishing"]["youtube"]["thumbnail"]` as fallback |
| `conversations[].public.youtube_description` | string | yes | From `infos["publishing"]["youtube"]["description"]` |

---

## HolonConversationBrowse field reference

| Field | Type | Nullable | Notes |
|-------|------|----------|-------|
| `holon` | `HolonRef` | no | Requested holon |
| `events[]` | list | no | Immediate child holons of type `event` |
| `events[].journeys[]` | list | no | Directly attached conversation journeys for that event |
| `events[].journeys[].journey` | `JourneyBrowse` | no | Journey metadata |
| `events[].journeys[].conversations` | list[`PublicConversationOut`] | no | Only conversations connected to that event and using that journey |

---

## Endpoint Quick Reference

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET`    | `/api/coherence/browse/holons/{holon_slug}` | Bearer/Session/User token | Browse child events and available conversation journeys |
| `GET`    | `/api/coherence/browse/holons/{holon_slug}/conversations` | Bearer/Session/User token | Browse all child-event attached journey conversations for a holon |
| `GET`    | `/api/coherence/browse/holons?ids=…` | Bearer/Session/User token | Batch lookup public holon details by IDs (max 50) |
| `GET`    | `/api/coherence/browse/persons?ids=…` | Bearer/Session/User token | Batch lookup public person details by IDs (max 50) |
| `GET`    | `/api/coherence/browse/conversations` | Bearer/Session/User token | Browse public conversations for one journey |
| `GET`    | `/api/coherence/conversation-events` | User token only | List all Conversation Event holons, optionally below a holon |
| `GET`    | `/api/coherence/conversations` | Bearer/Session/User token | List active conversations for a person at a point in time |
| `GET`    | `/api/coherence/conversations/search` | User token only | List conversations globally or by owner holon, connected holon, and Person |
| `GET`    | `/api/coherence/conversations/{id}` | Bearer/Session/User token | Fetch a single conversation |
| `PATCH`  | `/api/coherence/conversations/{id}` | Bearer/Session/User token | Update infos/config (shallow merge), optional concurrency guard |
| `PUT`    | `/api/coherence/conversations/{id}/transcript/segments` | User token only | Replace all normalized transcript segments atomically (1–50 rows) |
| `POST`   | `/api/coherence/conversations/{id}/audio` | User token only | Upload and replace canonical audio (multipart, max 500 MiB) |
| `GET`    | `/api/coherence/conversations/{id}/audio` | User token only | Download canonical audio |
| `POST`   | `/api/coherence/conversations/{id}/enter-coherence` | Bearer/Session/User token | Sole owner of config['enter-coherence']: upsert room state (phase/claims/version) + RealtimeKit metadata (idempotent) |
| `GET`    | `/api/coherence/conversations/{id}/enter-coherence` | Bearer/Session/User token | Look up stored enter-coherence room state + RealtimeKit metadata (diagnostics) |
| `POST`   | `/api/coherence/conversations/{id}/recorded` | Bearer/Session/User token | Advance to next step, add "recorded" note, optionally update infos/config |
| `GET`    | `/api/coherence/hook/cal.com/{person_id}` | None | cal.com webhook activation check (plain-text hint) |
| `POST`   | `/api/coherence/hook/cal.com/{person_id}` | None | cal.com booking webhook (BOOKING_CREATED/RESCHEDULED/CANCELLED) |
