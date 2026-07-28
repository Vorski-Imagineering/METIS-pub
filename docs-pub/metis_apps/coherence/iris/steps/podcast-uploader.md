# Podcast Uploader

Extracts the audio and publishes it as a podcast episode.

## At a glance

| | |
|---|---|
| **Needs** | The title, and the recording (cloud copy preferred, local otherwise) |
| **Produces** | A published podcast episode and its URL |
| **Waits when** | The title isn't generated yet, or the recording isn't available |
| **Re-running** | Safe — skips entirely once an episode exists |

## What it does

Pulls the audio out of the recording, uploads it to the podcast host (Buzzsprout), and records
the episode details on the conversation.

**The title is the only hard requirement.** Everything else degrades gracefully: the episode
description falls back from the YouTube description, to the subtitle, to the title. A missing
subtitle never blocks an episode.

If the conversation has a transcript, it's appended to the episode description as plain-text
show notes, trimmed to the length podcast directories accept.

The season is taken from the step setting when there is one, and otherwise derived from the
year the upload runs.

## How it behaves

- **It checks for an existing episode before anything else** — before even validating
  credentials. An already-published conversation therefore never starts erroring because
  someone later broke the podcast configuration.
- **Prefers the cloud copy** of the recording when the
  [Cloud Storage Migrator](cloud-storage-migrator.md) has run, and the local file otherwise.
- **Rate limits and server errors are retried** in place and then on the next scheduled run.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| Waiting with no error | The title isn't generated yet | Normal. Check the [Content Generator](content-generator.md) step. |
| Error: no recording available | Neither a cloud copy nor a local file could be found | Check whether the recording was migrated and whether the storage settings are right |
| Error mentioning the podcast API key or show | Podcast host credentials are missing or wrong | An administrator fixes the agent configuration, then re-run |
| Error during audio extraction | The recording is corrupt or an unexpected format | Check the recording plays; re-download it if not |
| Episode published with a thin description | No YouTube description and no subtitle existed at the time | Fill them in and publish the update on the podcast host — this step won't overwrite a published episode |
| Re-run did nothing | An episode already exists for this conversation | Expected. Deliberate republishing is done on the podcast host |
| Wrong season number | No season set on the step, so it used the current year | Set the season explicitly on the step |

## Technical reference

| | |
|---|---|
| **Step type** | `podcast_uploader` |
| **Runs after** | `cloud_storage_migrator` (prefers the cloud copy as its source) |
| **Feeds** | nothing — terminal branch |
| **Reads** | `fields.title` (the only hard gate); optionally `fields.youtube_description`, `fields.subtitle`; the conversation's transcript for show notes; `config["iris.downloads"]["amazon_s3_key"]` or `["recording"]` |
| **Writes** | `records.podcast` — episode id, episode URL, RSS GUID, uploaded-at, host, show id |
| **Needs on the agent** | `spotify_podcasts.api_key`, `spotify_podcasts.show_id`; plus `cloud_storage.*` if reading the cloud copy |
| **Needs on the server** | `ffmpeg` |
