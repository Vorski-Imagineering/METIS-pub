# Recording Downloader

| | |
|---|---|
| **Label** | Recording Downloader |
| **Slug** | `realtimekit_downloader` |
| **File** | `metis_apps/coherence/iris_realtimekit.py` |
| **Class** | `RealtimekitDownloader` |
| **Depends on** | *(none — first stage)* |

## Purpose

Downloads the Cloudflare RealtimeKit recording to local storage, applying MP4 faststart.
This is the first stage: it produces the raw recording every other branch builds on. The
post-meeting **transcript is not** handled here — it is fetched by
[transcript-importer](transcript-importer.md), so a missing or late transcript never blocks
or errors the recording download.

## Pipeline position

- **Upstream (`depends_on`):** none — first stage.
- **Feeds into:** `transcript_importer`, `google_transcribe`, and `video_editor` (all three
  branch off the raw recording).
- **Alternative to:** none.

## Data flow

**Reads**
- `config["enter-coherence"]["recordingId"]`

**Writes**
- `config["iris.downloads"]["recording"]`

## Requirements

- **Agent.config:** `cloudflare.cloudflare_account_id`, `cloudflare.app_id`,
  `cloudflare.api_token`.
- **System:** `ffmpeg` on PATH (MP4 faststart; falls back to the original file with a
  warning if it fails).
- **External credentials:** Cloudflare RealtimeKit (above).

## Behavior details

- **Idempotency:** skips re-download if the config path is set **and** the file still exists
  on disk.
- **`RetryLater` conditions:** the recording isn't `UPLOADED` yet. RealtimeKit recordings
  progress `INVOKED → RECORDING → UPLOADING → UPLOADED`; only `UPLOADED` recordings are
  picked up — this is the usual "why hasn't this run yet" answer just after a meeting ends.
- **Done vs error:** "done" once the recording is on disk; a permanent error is a bad
  Cloudflare config or an API failure.

## Step slug convention

Not fixed in the module; the live production Schedule uses `"recorded"` (matching
`iris-template`'s step 2). What matters is `config["iris_job"] = "realtimekit_downloader"`.

## Testing this step

No automated test today. Manual scenario (staging):

- **Happy path:** a conversation with a valid `enter-coherence.recordingId` for an
  `UPLOADED` recording → the file lands and `config["iris.downloads"]["recording"]` is set.
- **Not ready:** point at a recording still `RECORDING`/`UPLOADING` → `RetryLater` (no error
  Note).
- **Bad credentials:** clear/typo a `cloudflare.*` key → permanent error with the API
  message.

See the *testing guide* (internal engineering doc, not published here) for the shared verification pattern and
how to seed a safe test conversation.

## Related runbooks

- *manual-retrigger* (internal engineering doc, not published here)
- *copy-conversation* (internal engineering doc, not published here) — seed a test conversation that
  keeps the recording reference.
