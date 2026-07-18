# YouTube Uploader

| | |
|---|---|
| **Label** | YouTube Uploader |
| **Slug** | `youtube_uploader` |
| **File** | `metis_apps/coherence/iris_youtube.py` |
| **Class** | `YouTubeUploader` |
| **Depends on** | `content_generator` |

## Purpose

Uploads the recording to YouTube as an **unlisted** video via the YouTube Data API v3, then
polls processing status until ready.

> **Recording selection** (`_select_recording_rel`, `iris_youtube.py:287`): prefers the
> cleaned cut `edited_recording` from [video-editor](video-editor.md) when its file exists
> on disk, falling back to the raw `recording` (journeys without a video-editor step, or an
> edited file missing on disk — the fallback logs a warning). Publishing the cleaned cut is
> a deliberate product decision (specs/VideoEditingAndClips.md).

## Pipeline position

- **Upstream (`depends_on`):** `content_generator` (needs title + description).
- **Feeds into:** `approval_waiter`, `cloud_storage_migrator`, `linkedin_publisher`,
  `telegram_distributor` (all gate on the YouTube result).
- **Alternative to:** none.

## Data flow

**Reads**
- Local recording file — `config["iris.downloads"]["edited_recording"]` preferred,
  `["recording"]` fallback (see Recording selection above).
- `infos["publishing"]["title"]` / `youtube.description` (prerequisite gate — RetryLater
  until content-generator has written both).
- `infos["publishing"]["thumbnail"]["path"]` (optional — thumbnail sync).
- `JourneyStep.config` (`visibility`, `category_id`, `set_thumbnail_if_available`,
  `processing_timeout_minutes`, `youtube_refresh_token`).

**Writes**
- `infos["publishing"]["youtube"]` (video_id, video_url, visibility, upload_status,
  processing_status, uploaded_at, processed_at, thumbnail_synced_at).

## Requirements

- **Credentials (OAuth 2.0 only — no service accounts):** assembled at `iris_youtube.py:346`
  from two places:
  - `Agent.config["youtube"].client_id` / `.client_secret` — the shared GCP OAuth client.
  - `JourneyStep.config.youtube_refresh_token` — the per-channel token, written by the
    in-app **Connect YouTube** flow (`journey_step_youtube_auth_callback`), **not** stored on
    the Agent.

  Access tokens are minted per run in memory and never written back to config.
  > `_validate_yt_config`'s error text says `Agent.config['youtube'] is missing required keys`
  > even when the missing key is the step's `refresh_token` — the message is imprecise; a blank
  > `refresh_token` almost always means the step was never connected via **Connect YouTube**.
- **System:** none.
- **External credentials:** YouTube OAuth (above). Setup:
  [youtube-uploader-setup.md](youtube-uploader-setup.md).

## Behavior details

- **Idempotency:** if `video_id` already exists, skips straight to the processing-status
  poll — never creates a second upload.
- **Processing poll:** after upload, polls YouTube processing state; a still-processing video
  past `processing_timeout_minutes` raises `RetryLater` (the "Sync Status" UI action
  re-polls without re-uploading).
- **Visibility:** uploads unlisted (or `private`); `public` is set later, at the approval
  step.
- **Error classification** (`_classify_yt_error`, `iris_youtube.py:143`):
  - *Transient* → in-run backoff (1s/5s/25s, 3 attempts) then `RetryLater`: HTTP 500/503,
    network errors, and 403 with reason `quotaExceeded` (daily quota — an upload costs
    ~1,600 of the 10,000 free units).
  - *Permanent* → error note + pipeline halt: other 4xx (400/401/non-quota 403), YouTube
    reporting processing `failed`, invalid step config.
  - Revoked/expired refresh token (`invalid_grant` on token mint) raises `YouTubeAuthError`,
    surfaced as a permanent error whose note tells staff exactly which journey page and step
    to reconnect.
- **RetryLater (not errors):** missing title/description/recording, processing-poll timeout,
  transient attempts exhausted. The `iris.<step-slug>` claim is released each time so the
  next scheduled run re-claims.
- **Truncation:** title capped at 100 chars, description at 5,000 (YouTube API limits).

## What binds a step to this job

Matching is on **`JourneyStep.config["iris_job"] == "youtube_uploader"`** (underscore — the
registry slug at `iris_youtube.py:530`), resolved by `_resolve_step_slugs` (`iris.py:188`) and
the ready-conversation query (`iris.py:436`). The `JourneyStep.slug` itself is a free-form
identifier and does **not** affect matching — there is no hyphen-vs-underscore requirement on it.

## Testing this step

- `test_iris_youtube.py` — automated coverage of the upload/idempotency/poll logic.
- *test-scripts/test-youtube-upload.md* (internal engineering doc, not published here) — manual
  end-to-end with real OAuth credentials on staging.

Run: `python3 manage.py test --keepdb --parallel auto metis_apps.coherence`. See the
*testing guide* (internal engineering doc, not published here).

## Related runbooks

- *takedown-youtube* (internal engineering doc, not published here) — delete an uploaded video.
- *manual-retrigger* (internal engineering doc, not published here)
- *consent-withdrawal* (internal engineering doc, not published here) — when a participant withdraws
  after publishing.
