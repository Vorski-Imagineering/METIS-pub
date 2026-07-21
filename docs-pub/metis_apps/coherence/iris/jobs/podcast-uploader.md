# Podcast Uploader

| | |
|---|---|
| **Label** | Podcast Uploader |
| **Slug** | `podcast_uploader` |
| **File** | `metis_apps/coherence/iris_podcast.py` |
| **Class** | `PodcastUploader` |
| **Depends on** | `cloud_storage_migrator` |

## Purpose

Extracts audio and publishes the episode via the Buzzsprout hosting API.

## Pipeline position

- **Upstream (`depends_on`):** `cloud_storage_migrator` (prefers the cloud copy as source).
- **Feeds into:** nothing (terminal branch).
- **Alternative to:** none.

## Data flow

**Reads**
- `infos["publishing"]["title"]` — the only hard prerequisite gate (decision
  2026-07-20). `subtitle` and `youtube.description` are optional: the episode
  description falls back `youtube.description` → `subtitle` → `title`.
- The conversation's `TranscriptSegment` rows — appended to the episode
  description as plain-text show notes when present (truncated to 4000 chars,
  the Apple Podcasts description limit).
- `config["iris.downloads"]["amazon_s3_key"]` (preferred source) or
  `config["iris.downloads"]["recording"]` (local fallback).

**Writes**
- `infos["publishing"]["podcast"]` (episode_id, episode_url, rss_guid, uploaded_at, host, show_id).

## Requirements

- **Agent.config:** `spotify_podcasts.api_key`, `spotify_podcasts.show_id`; also needs
  `cloud_storage.*` (same shape as `cloud_storage_migrator`) if downloading from the cloud
  copy.
- **System:** `ffmpeg` on PATH (MP3 extraction).
- **External credentials:** Buzzsprout API (above), plus cloud storage if reading the cloud
  copy.

## Behavior details

- **Idempotency:** skips if `podcast.episode_id` is already set — checked before
  credential validation, so an already-published conversation never errors on
  since-broken agent config.
- **Source preference:** downloads from the cloud copy when available, else uses the local
  recording.
- **Season:** `config.season` when set; otherwise derived from the publication year
  (the year the upload runs).
- **Done vs error:** "done" once the episode is created and `podcast.episode_id` written;
  permanent error on a bad Buzzsprout config or API failure (transient 429/5xx are
  retried in-process, then released for the next scheduled run).

## Step slug convention

`"podcast_uploader"` (matches `config["iris_job"] = "podcast_uploader"`).

## Testing this step

Automated: `metis_apps/coherence/tests/test_iris_podcast.py` covers the happy path
(cloud and local source), prerequisite gate, missing recording, credential/API/FFmpeg
failures, transient-retry, idempotent re-run, show notes, and season derivation
(Buzzsprout mocked). Manual scenario (staging): with valid `spotify_podcasts.*` and a
migrated cloud object (or a local recording), run → episode created on Buzzsprout,
`infos["publishing"]["podcast"]` written. Re-run → skipped (episode_id present). See the
*testing guide* (internal engineering doc, not published here).

## Related runbooks

- *manual-retrigger* (internal engineering doc, not published here)
- *consent-withdrawal* (internal engineering doc, not published here) — removing a published episode.
