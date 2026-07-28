# Recording Downloader

Fetches the meeting recording from the meeting provider and stores it, ready for everything
else. This is always the first step: no recording, no pipeline.

## At a glance

| | |
|---|---|
| **Needs** | A recording ID on the conversation (put there when the meeting was booked) |
| **Produces** | The recording file, stored and linked to the conversation |
| **Waits when** | The provider hasn't finished uploading the recording yet |
| **Re-running** | Safe — skips if the file is already there |

## What it does

Downloads the recording from the meeting provider (Cloudflare RealtimeKit) and prepares it
for streaming, so a video player can start it without downloading the whole file first.

It does **not** fetch the transcript. That's a separate step
([Transcript Importer](transcript-importer.md)), specifically so that a missing or slow
transcript never holds up — or breaks — getting the recording safely stored.

## How it behaves

- **The usual wait.** Recordings move through *invoked → recording → uploading → uploaded* at
  the provider, and only an *uploaded* recording can be downloaded. Just after a meeting ends
  it will be in one of the earlier states, so the step waits and tries again. A few minutes is
  normal.
- **It won't download twice.** If the recording is already recorded on the conversation and
  the file is still on disk, the step does nothing and moves on.
- **Fallback on preparation.** If the streaming-preparation pass fails, the original file is
  kept and used rather than the step failing.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| Sitting here for a few minutes after the meeting, no error | The recording isn't *uploaded* at the provider yet | Normal. Wait for the next run. |
| Sitting here for hours, no error | The meeting may never have been recorded, or the conversation has no recording ID | Check the meeting was actually recorded; check the conversation carries a recording reference from booking |
| Error mentioning credentials or authorisation | The meeting-provider credentials on the agent are missing or wrong | An administrator needs to correct them, then re-run the step |
| Error from the provider's API | The recording ID doesn't resolve, or the provider rejected the request | Confirm the recording exists at the provider for that session |
| Downloaded, but a later step says the file is missing | The file was archived to cloud storage and the local copy deleted | Expected after the [Cloud Storage Migrator](cloud-storage-migrator.md) runs — steps that need the media use the cloud copy |

## Technical reference

| | |
|---|---|
| **Step type** | `realtimekit_downloader` |
| **Runs after** | *(nothing — first step)* |
| **Feeds** | `transcript_importer`, `google_transcribe`, `video_editor` |
| **Reads** | `config["enter-coherence"]["recordingId"]` |
| **Writes** | `config["iris.downloads"]["recording"]` |
| **Needs on the agent** | `cloudflare.cloudflare_account_id`, `cloudflare.app_id`, `cloudflare.api_token` |
| **Needs on the server** | `ffmpeg` |
