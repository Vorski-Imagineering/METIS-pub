# Conversation JSON Fields

`Conversation` has two JSONFields that together carry all pipeline state and
published output: **`config`** and **`infos`**.

**Rule of thumb:**
- `config` = operational state (pipeline markers, file paths, credentials used at runtime)
- `infos` = output content (generated text, uploaded URLs, approval records)

Nothing downstream should write to `config` to store publishing results, and
nothing upstream should write to `infos` to gate pipeline progression.

**This is enforced, not just a convention.** `enter-coherence`, `audio`, `cal.com`, and
`iris.*` cannot be written via the generic `PATCH /conversations/{id}` or
`POST /conversations/{id}/recorded` endpoints at all (400
`invalid_namespace_placement`), regardless of which field (`infos` or
`config`) the caller addresses. `enter-coherence` has its own dedicated
endpoint (`POST/GET /conversations/{id}/enter-coherence`) that is the sole
writer of `config['enter-coherence']`; `audio` has its own upload endpoint;
`cal.com` and `iris.*` are written
internally only. Separately, `publishing`/`publishing_approval`/
`publishing_status` must be written via `infos`, not `config` (still just a
placement check, since there's no dedicated endpoint for those yet).

This was added after `enter-coherence` was observed sending
`config['enter-coherence']` in some requests and `infos['enter-coherence']`
in others for the same room state, causing the two fields to diverge on the
same conversation — the generic PATCH endpoint let the caller pick a field
and a namespace key with no server-side ownership check at all. Giving
`enter-coherence` a narrow endpoint that can only ever address
`config['enter-coherence']` closes that mistake structurally, rather than
just validating it after the fact. Unrecognised namespaces are still accepted
in either field via generic PATCH — only the namespaces documented below are
enforced.

---

## `conversation.config`

Top-level keys are namespaced strings. All keys are optional; a missing key is
the same as that feature/step not having run yet.

---

### `enter-coherence`

The sole owner of this key is `POST/GET /conversations/{id}/enter-coherence`
(see `../PLAYBOOK.md`). PartyKit writes room-state fields (`phase`,
`claims`, `version`) as the room progresses, and RealtimeKit meeting/session/
participant metadata as it becomes known — both through the same endpoint.

```json
{
  "enter-coherence": {
    "recordingId": "uuid-string",
    "version": 3,
    "claims": {
      "Display Name": {
        "personId": -1
      }
    },
    "meetingId": "bbb8940e-1b97-402a-97d6-2708b7feca41",
    "sessionId": "05e57591-d89e-45c9-ae44-08dc1eaad0e0",
    "recordingEndedAt": "2026-07-07T19:00:00+00:00",
    "participants": {
      "coherence:coherence-456:browser-session-id": {
        "browserSessionId": "browser-session-id",
        "personId": 123,
        "displayName": "Alice",
        "realtimeKitParticipantId": "rtk-participant-id",
        "customParticipantId": "coherence:coherence-456:browser-session-id",
        "assignedAt": "2026-07-07T17:56:00+00:00",
        "lastCredentialIssuedAt": "2026-07-07T17:56:00+00:00"
      }
    }
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `phase` | string | Current room-state phase, e.g. `conversation`, `exit-lounge`. Always overwritten to the latest value when provided. |
| `version` | int | Optimistic-concurrency version. The API rejects updates whose `expectedVersion` doesn't match this value. |
| `claims` | object | Keyed by display name. Each value has `personId` (negative = unresolved external participant). Used to resolve speaker names in the transcript. Upserted per display-name key — a write to one claim never erases another. |
| `meetingId` | string | RealtimeKit meeting id. Idempotency anchor for the `enter-coherence` endpoint once known; a differing `meetingId` on resend is rejected with 409. |
| `recordingId` | string | Cloudflare RealtimeKit recording UUID. Read by `RealtimekitDownloader`. |
| `sessionId` | string | RealtimeKit session id. Needed for the RealtimeKit REST transcript fetch; may arrive later than `meetingId`. |
| `recordingEndedAt` | ISO datetime | Timestamp from room/recording end, written by PartyKit. |
| `participants` | object | Keyed by `customParticipantId` (the value expected in transcript `peerData.cpi`). Upserted on resend; re-credentialing (new `realtimeKitParticipantId`) updates the id and `lastCredentialIssuedAt` but keeps the original `assignedAt`. |

---

### `cal.com`

Written once at conversation creation by the cal.com `BOOKING_CREATED` webhook handler.
Holds the raw booking payload as received from cal.com.

```json
{
  "cal.com": {
    "bookingId": "abc123",
    "title": "Conversation with Alice",
    "startTime": "2026-07-07T17:00:00.000Z",
    "endTime": "2026-07-07T18:00:00.000Z"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `bookingId` | string | cal.com booking id. Used by the webhook to look up the conversation on `BOOKING_RESCHEDULED`/`BOOKING_CANCELLED`. |
| *(rest)* | — | Raw cal.com payload fields, passed through as received. |

---

### `iris.downloads`

Written by `RealtimekitDownloader` (recording download), `CloudStorageMigrator`
(cloud upload), and `GoogleTranscribe` (Chirp breadcrumb). Tracks where the
recording file lives at each stage.

```json
{
  "iris.downloads": {
    "recording": "iris/recordings/352/video.mp4",
    "amazon_s3_key": "iris/recordings/352/video.mp4",
    "chirp_stt": {"prefix": "chirp-stt/352/ab…/", "results_prefix": "chirp-stt/352/ab…/results/", "bucket": "iris-…-stt", "operation": "projects/…/operations/…", "duration_ms": 3000000, "language": "en-US", "submitted_at": "..."},
    "chirp_transcript": {"model": "chirp_3", "language": "en-US", "at": "...", "segments": 128}
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `recording` | string | Path relative to `MEDIA_ROOT`. Set by `RealtimekitDownloader`. Always a local path — never overwritten by later steps. The file may be deleted from disk after cloud migration, but the path is preserved as a historical reference. |
| `amazon_s3_key` | string | S3/R2 object key written by `CloudStorageMigrator` after successful upload. Absent until cloud migration runs. `PodcastUploader` uses this to download from cloud; falls back to `recording` (local) if absent. |
| `chirp_stt` | object | **In-flight** state for `GoogleTranscribe`'s async Chirp batch job: GCS `prefix`/`results_prefix` for the staged audio + results, the `bucket` they live in (so reset can clean up without an agent to look it up from), the long-running `operation` name (diagnostics only), `duration_ms`, `language`, and `submitted_at` (ISO). Set when a batch is submitted, polled on later runs, and **deleted** once results are written (or the poll times out). Its presence means "a Chirp transcription is running for this conversation." |
| `chirp_transcript` | object | Breadcrumb written by `GoogleTranscribe` when Chirp-3 (re)transcribed the recording from audio: `model`, `language`, `at` (ISO datetime), and `segments` (count). Records that the current `TranscriptSegment` rows came from Chirp rather than the provider transcript. Absent unless `google_transcribe` ran. |

---

### `iris.<step_slug>`

The IrisJob base class writes one of these keys per pipeline step. It is the
primary idempotency guard — a conversation is only claimed by a job if this key
is absent. Written atomically under `select_for_update` to prevent double-claiming.

**Base shape (all jobs):**

```json
{
  "iris.content-generator": {
    "status": "done",
    "started": "2025-01-15T10:00:00+00:00",
    "finished": "2025-01-15T10:02:34+00:00",
    "worker": "hostname:12345"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `"processing"` → `"done"` or `"error"` |
| `started` | ISO datetime | When the job claimed this conversation. |
| `finished` | ISO datetime | When status transitioned to `done` or `error`. |
| `worker` | string | `hostname:pid` of the worker process that claimed this run. |
| `error` | string | Error message. Present only when `status = "error"`. |

**Recovery:** to retrigger a step, delete its `iris.<step_slug>` key from `config`
in Django Admin. The next scheduled run will re-claim the conversation.

All other step slugs (`iris.content-generator`, `iris.cover-image-generator`, `iris.youtube-uploader`,
`iris.approval-waiter`, `iris.cloud-storage-migrator`, `iris.podcast-uploader`,
`iris.linkedin-publisher`, `iris.telegram-distributor`) use only the base fields.

---

## `conversation.infos`

Top-level keys group output by domain. Jobs write to specific sub-paths;
they must not touch paths they don't own.

---

### `audio`

The canonical sound file is stored locally under `MEDIA_ROOT`; its relative
path and metadata live in `infos["audio"]`. It is written only by
`POST /api/coherence/conversations/{id}/audio` or by `GoogleTranscribe` when it
extracts FLAC from a recording for the first time.

```json
{
  "audio": {
    "path": "iris/audio/352/9ef2...ab.flac",
    "name": "chirp-extracted.flac",
    "content_type": "audio/flac",
    "size_bytes": 18300211,
    "source": "chirp_extracted",
    "created_at": "2026-07-16T14:30:00+00:00"
  }
}
```

| Field | Type | Description |
|---|---|---|
| `path` | string | Path relative to `MEDIA_ROOT`, constrained to `iris/audio/<conversation_id>/`. |
| `name` | string | Original upload filename or `chirp-extracted.flac`. |
| `content_type` | string | Server-selected MIME type based on the accepted audio extension. |
| `size_bytes` | integer | Stored file size. |
| `source` | string | `upload` or `chirp_extracted`. |
| `created_at` | ISO datetime | When this canonical file replaced the previous one. |

Generic conversation PATCH rejects the `audio` namespace. Download it through
the authenticated `GET /api/coherence/conversations/{id}/audio` endpoint rather
than constructing a public media URL from the stored path.

---

### `publishing`

The main publishing asset store. Written incrementally by multiple jobs.

```json
{
  "publishing": {
    "title": "The Future of Open Source",
    "subtitle": "A conversation with Ada Lovelace",
    "language": "en",
    "qa": {
      "segment_count": 312,
      "distinct_speakers": 2,
      "warnings": []
    },
    "meta": {
      "model": "gemini-2.5-pro",
      "generated_at": "2025-01-15T10:02:00+00:00"
    },
    "youtube": {
      "description": "Full YouTube description text...",
      "video_id": "dQw4w9WgXcQ",
      "video_url": "https://youtu.be/dQw4w9WgXcQ",
      "visibility": "unlisted",
      "upload_status": "uploaded",
      "processing_status": "succeeded",
      "uploaded_at": "2025-01-15T11:00:00+00:00",
      "processed_at": "2025-01-15T11:12:00+00:00",
      "thumbnail_synced_at": "2025-01-15T11:13:00+00:00"
    },
    "linkedin": {
      "posts": {
        "host": "Loved this conversation with...",
        "guest": "Honoured to join Ada to discuss...",
        "7": {
          "post_url": "https://linkedin.com/feed/update/...",
          "role": "host",
          "published_at": "2025-01-16T09:00:00+00:00"
        }
      },
      "published_at": "2025-01-16T09:00:00+00:00"
    },
    "instagram": {
      "quotes": [
        {"speaker": "Ada Lovelace", "text": "The engine...", "offset_ms": 123000},
        {"speaker": "Charles Babbage", "text": "I propose...", "offset_ms": 456000}
      ]
    },
    "podcast": {
      "episode_id": "1234567",
      "episode_url": "https://www.buzzsprout.com/...",
      "rss_guid": "buzzsprout-1234567",
      "uploaded_at": "2025-01-16T10:00:00+00:00"
    },
    "telegram": {
      "note_id": 99,
      "linkedin_urls": ["https://linkedin.com/..."],
      "distributed_at": "2025-01-16T11:00:00+00:00"
    }
  }
}
```

#### `publishing` field ownership

Each sub-path is owned by exactly one job. Only the owning job should write to it.

| Path | Owner | Notes |
|------|-------|-------|
| `title`, `subtitle`, `language` | `ContentGenerator` | |
| `qa.*` | `ContentGenerator` | Written before generation starts, visible even on failure. |
| `meta.*` | `ContentGenerator` | |
| `youtube.description` | `ContentGenerator` | |
| `linkedin.posts.host`, `linkedin.posts.guest` | `ContentGenerator` | Draft text; overwritten when participant edits on approval page. |
| `instagram.quotes[]` | `ContentGenerator` | |
| `youtube.video_id`, `youtube.video_url`, `youtube.visibility`, `youtube.upload_status`, `youtube.processing_status`, `youtube.uploaded_at`, `youtube.processed_at`, `youtube.thumbnail_synced_at` | `YouTubeUploader` | |
| `linkedin.posts.<person_id>` (keyed by PK string) | `LinkedInPublisher` | Overwrites draft text after Chrome extension posts. `post_url` comes from `OutreachAction.infos["post_url"]`. |
| `linkedin.published_at` | `LinkedInPublisher` | |
| `podcast.*` | `PodcastUploader` | |
| `telegram.*` | `TelegramDistributor` | |

---

### `publishing_approval`

Written by the participant approval flow (approval page + `conversation_approval_action` view).

```json
{
  "publishing_approval": {
    "updated_at": "2025-01-15T14:00:00+00:00",
    "people": {
      "7": {
        "approved": true,
        "approved_at": "2025-01-15T14:00:00+00:00",
        "was_logged_in": true
      },
      "12": {
        "approved": true,
        "approved_at": "2025-01-15T15:30:00+00:00",
        "was_logged_in": false
      }
    }
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `updated_at` | ISO datetime | Last time any participant approved. |
| `people` | object | Keyed by `str(person.pk)`. |
| `people.<pk>.approved` | bool | Whether this participant has approved. |
| `people.<pk>.approved_at` | ISO datetime | When they approved. |
| `people.<pk>.was_logged_in` | bool | `True` if the participant was authenticated when they approved; `False` for token-only (unauthenticated) approvals. |

---

### `publishing_status`

Written by the `ApprovalWaiter` job once all required approvals are collected.

```json
{
  "publishing_status": {
    "approved": true,
    "state": "approved"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `approved` | bool | `True` once the approval threshold is met (all participants, or any one — depending on `ApprovalWaiterConfig.require_all_participants`). |
| `state` | string | `"waiting"` or `"approved"`. |
