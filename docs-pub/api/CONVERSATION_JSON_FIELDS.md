# Conversation JSON Fields

`Conversation` has two JSONFields that together carry all pipeline state and
published output: **`config`** and **`infos`**.

**Rule of thumb:**
- `config` = operational state (pipeline markers, file paths, credentials used at runtime)
- `infos` = output content (generated text, uploaded URLs, approval records)

Nothing downstream should write to `config` to store publishing results, and
nothing upstream should write to `infos` to gate pipeline progression.

---

## `conversation.config`

Top-level keys are namespaced strings. All keys are optional; a missing key is
the same as that feature/step not having run yet.

---

### `enter-coherence`

Written by the enter-coherence webhook when a participant joins a live session.

```json
{
  "enter-coherence": {
    "recordingId": "uuid-string",
    "version": 3,
    "claims": {
      "Display Name": {
        "personId": -1
      }
    }
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `recordingId` | string | Cloudflare RealtimeKit recording UUID. Read by `RealtimekitDownloader`. |
| `version` | int | Optimistic-concurrency version. The API rejects updates whose `expectedVersion` doesn't match this value. |
| `claims` | object | Keyed by display name. Each value has `personId` (negative = unresolved external participant). Used to resolve speaker names in the transcript. |

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
| `chirp_stt` | object | **In-flight** state for `GoogleTranscribe`'s async Chirp batch job: GCS `prefix`/`results_prefix` for the staged audio + results, the `bucket` they live in (so reset can clean up without an agent to look it up from), the long-running `operation` name (diagnostics only), `duration_ms`, `language`, and `submitted_at` (ISO). Set when a batch is submitted, polled on later runs, and **deleted** once results are written (or the poll times out). Its presence means "a Chirp transcription is running for this conversation" — it is this step's own bookkeeping, not a user-facing breadcrumb. |
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
path and metadata live in `infos["audio"]`. `POST
/api/coherence/conversations/{id}/audio` writes uploaded files, while
`GoogleTranscribe` creates this entry when it must extract a FLAC from a
downloaded recording. The existing recording/video path remains in
`config["iris.downloads"]["recording"]` as pipeline provenance.

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

The managed path is restricted to `iris/audio/<conversation_id>/`. Download it
through the authenticated `GET /api/coherence/conversations/{id}/audio` endpoint,
not by constructing a public media URL from the path. Generic conversation PATCH
does not accept the `audio` namespace.

---

### `publishing`

The main publishing asset store, split by **kind** into three top-level sections:

- **`fields`** — editable text. Each field is a layered envelope: the effective
  `value`, a `source` (`"generated"` or `"manual"`), a `generated` block recording
  which job produced it (with model + prompt hash + timestamp), and — once a human
  edits it — an `override` block. A manual edit *shadows* the generated value rather
  than replacing it, so it can be reverted and re-generation never destroys it.
- **`records`** — publication records (uploaded video, published posts, episode).
  Plain, job-owned, never human-edited.
- **`artifacts`** — rendered media (thumbnail, quote cards). Plain, renderer-owned.

```json
{
  "publishing": {
    "fields": {
      "title": {
        "value": "The Future of Open Source",
        "source": "manual",
        "generated": {
          "value": "Open Source: A Conversation",
          "job": "content_generator",
          "at": "2025-01-15T10:02:00+00:00",
          "model": "gemini-2.5-pro",
          "prompt_hash": "9f2c1a7b0e4d5c6f"
        },
        "override": {
          "value": "The Future of Open Source",
          "user_id": 42,
          "user_name": "Ada Lovelace",
          "at": "2025-01-15T14:02:00+00:00"
        }
      },
      "subtitle": {"value": "A conversation with Ada Lovelace", "source": "generated", "generated": {"…": "…"}},
      "language": {"value": "en", "source": "generated", "generated": {"…": "…"}},
      "qa": {"value": {"segment_count": 312, "distinct_speakers": 2, "warnings": []}, "source": "generated", "generated": {"…": "…"}},
      "youtube_description": {"value": "Full YouTube description text...", "source": "generated", "generated": {"…": "…"}},
      "linkedin_post": {"value": "Loved this conversation with...", "source": "generated", "generated": {"…": "…"}},
      "instagram_quotes": {"value": [{"speaker": "Ada Lovelace", "text": "The engine..."}], "source": "generated", "generated": {"…": "…"}}
    },
    "records": {
      "youtube": {
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
          "7": {"post_url": "https://linkedin.com/feed/update/...", "published_at": "2025-01-16T09:00:00+00:00"}
        },
        "published_at": "2025-01-16T09:00:00+00:00"
      },
      "podcast": {
        "episode_id": "1234567",
        "episode_url": "https://www.buzzsprout.com/...",
        "rss_guid": "buzzsprout-1234567",
        "uploaded_at": "2025-01-16T10:00:00+00:00"
      },
      "telegram": {"note_id": 99, "linkedin_urls": ["https://linkedin.com/..."]},
      "cover_images": {"template_pack": "default", "render_version": 1, "generated_at": "2025-01-15T10:05:00+00:00"}
    },
    "artifacts": {
      "thumbnail": {"path": "iris/images/352/thumbnail/thumbnail.jpg", "url": "/media/...", "width": 1280, "height": 720, "generated_at": "…"},
      "linkedin_header": {"path": "…", "url": "…", "width": 1200, "height": 627, "generated_at": "…"},
      "instagram_quote_cards": [{"quote_index": 0, "speaker": "…", "text": "…", "path": "…", "url": "…"}],
      "imported_thumbnails": [{"url": "https://i.ytimg.com/..."}]
    }
  }
}
```

The GET response denormalises each field to its effective `value` (the provenance
envelope is not exposed on read); `records` and `artifacts` are returned as-is.

#### `publishing` path ownership

Each path is owned by exactly one job. Only the owning job writes to it; a job that
tries to write outside its declared ownership is rejected.

| Path | Owner | Notes |
|------|-------|-------|
| `fields.title`, `fields.subtitle`, `fields.language`, `fields.qa` | `ContentGenerator` | `qa` written before generation starts, visible even on failure. |
| `fields.youtube_description` | `ContentGenerator` | |
| `fields.linkedin_post` | `ContentGenerator` | Draft text shared by every participant; a participant edit on the approval page becomes an `override` on this one field. |
| `fields.instagram_quotes` | `ContentGenerator` | |
| `records.youtube.*` | `YouTubeUploader` | `video_id` references a live upload and is preserved across resets/migrations. |
| `records.linkedin.posts.<person_id>` (numeric PK string), `records.linkedin.published_at` | `LinkedInPublisher` | `post_url` comes from `OutreachAction.infos["post_url"]`. |
| `records.podcast.*` | `PodcastUploader` | |
| `records.telegram.*` | `TelegramDistributor` | |
| `records.cover_images` | `CoverImageGenerator` | Render marker. |
| `artifacts.thumbnail`, `artifacts.linkedin_header`, `artifacts.instagram_quote_cards` | `CoverImageGenerator` | |

Editable fields (`fields.title`, `fields.subtitle`, `fields.youtube_description`,
`fields.linkedin_post`) are the only paths a human may override; every other
path is job-generated.

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
