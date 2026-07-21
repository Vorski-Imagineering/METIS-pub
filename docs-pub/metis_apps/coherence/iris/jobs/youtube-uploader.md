# YouTube publishing (upload / metadata sync / thumbnail sync)

YouTube publishing is **three independently re-runnable steps**, split along the
YouTube Data API's own seams so metadata or a thumbnail can be re-pushed without
re-uploading (or orphaning) the video.

| Step | Slug | Class | API | Owns |
|---|---|---|---|---|
| Video upload | `youtube_video_upload` | `YouTubeVideoUpload` | `videos.insert` + `videos.list` poll | `records.youtube.{video_id, video_url, visibility, upload_status, processing_status, uploaded_at, processed_at}` |
| Metadata sync | `youtube_metadata_sync` | `YouTubeMetadataSync` | `videos.list` → `videos.update` | `records.youtube.{metadata_synced_at, synced_hash}` |
| Thumbnail sync | `youtube_thumbnail_sync` | `YouTubeThumbnailSync` | `thumbnails.set` | `records.youtube.thumbnail_synced_at` |

All three live in `metis_apps/coherence/iris_youtube.py`. A typical journey runs them
in that order, immediately after `content_generator` (and, for the thumbnail,
`cover_image_generator`).

## Video upload — `youtube_video_upload`

Uploads the recording as an **unlisted** video and polls processing status until ready.
Expensive and rarely re-run.

> **Recording selection** (`_select_recording_rel`): prefers the cleaned cut
> `edited_recording` from [video-editor](video-editor.md) when its file exists on disk,
> else the raw `recording`. Publishing the cleaned cut is a deliberate product decision.

- **Reads:** `fields.title`, `fields.youtube_description` (RetryLater until both exist);
  the local recording file.
- **Writes:** the `records.youtube` upload state above.
- **Idempotency:** if `video_id` already exists, skips straight to the processing poll —
  never uploads a second copy.
- **Reset orphans the video:** because this step owns `records.youtube.video_id`, the reset
  confirmation warns that the uploaded video is **not** deleted on YouTube (a re-run uploads
  a second copy). Delete it on YouTube first if that's not intended.
- **Length pre-flight:** probes duration and checks the channel's `longUploadsStatus`, failing
  fast on >15 min uploads from channels not verified for long uploads.

## Metadata sync — `youtube_metadata_sync`

Pushes the current title + description to the uploaded video. **Read-modify-write:**
`videos.update` *replaces* the snippet (any omitted property is cleared) and requires
`title` + `categoryId`, so the step fetches the current snippet with `videos.list(part=snippet)`,
mutates the target fields, and sends the full snippet back. Chapter timestamps are remapped
onto the edited cut here (`_publish_description`).

- **Reads:** `fields.title`, `fields.youtube_description`, `records.youtube.video_id`.
- **No-op guard:** stores a `synced_hash` of the last-pushed metadata; if the current metadata
  matches, the step returns without touching the API — safe to run on every pipeline pass, and
  the way to re-publish an edited title/description is simply to re-run (or reset) this step.
- Cost ≈ 51 quota units/video (1 list + 50 update) against the 10,000/day default.

## Thumbnail sync — `youtube_thumbnail_sync`

Sets the AI-generated cover image as the video thumbnail via `thumbnails.set`. Cheap and
idempotent — reset/re-run to re-push a regenerated thumbnail.

- **Reads:** `artifacts.thumbnail`, `records.youtube.video_id`.

## Credentials (shared across all three; OAuth 2.0 only — no service accounts)

- `Agent.config["youtube"].client_id` / `.client_secret` — the shared GCP OAuth client.
- `JourneyStep.config.youtube_refresh_token` — the per-channel token, written by the in-app
  **Connect YouTube** flow. Connecting on **any one** of the three youtube steps authorises
  the others: `_refresh_token_for_step` falls back to a sibling youtube step's token.

Access tokens are minted per run in memory and never written back to config. Setup:
[youtube-uploader-setup.md](youtube-uploader-setup.md).

## Error classification (all three, `_classify_yt_error`)

- *Transient* → in-run backoff (1s/5s/25s, 3 attempts) then `RetryLater`: HTTP 500/503, network
  errors, 403 `quotaExceeded`. Processing-poll timeout is also RetryLater (video is uploaded).
- *Permanent* → error note + pipeline halt: other 4xx, YouTube reporting processing `failed`,
  invalid step config. A revoked/expired refresh token (`invalid_grant`) surfaces a permanent
  error whose note names the journey page + step to reconnect.
- **Truncation:** title capped at 100 chars, description at 5,000 (YouTube API limits).

## Migration from the old combined step

The old single `youtube_uploader` step was split by migration
`0020_split_youtube_uploader_step`: each `youtube_uploader` JourneyStep is repointed to
`youtube_video_upload` (keeping its slug/order) and two ordered siblings
(`youtube_metadata_sync`, `youtube_thumbnail_sync`) are inserted after it, later steps shifting
+2. The bespoke **Sync Status** button + `/youtube/sync/` endpoint were retired — re-running
the metadata-sync step replaces them.

> **Ops:** the django-q2 Schedule that pointed `func` at `…iris_youtube.youtube_uploader` must be
> replaced with three schedules targeting `youtube_video_upload`, `youtube_metadata_sync`, and
> `youtube_thumbnail_sync` (each with `agent_slug`).

## Testing

- `test_iris_youtube.py` — recording selection.
- `test_youtube_split.py` — metadata read-modify-write + no-op guard, thumbnail sync, shared-channel
  token fallback, the split migration, and the reset orphan warning.
- `test_coherence.py` — `YouTubeVideoUpload` config + upload/poll process coverage.
