# Transcript Importer

| | |
|---|---|
| **Label** | Transcript Importer |
| **Slug** | `transcript_importer` |
| **File** | `metis_apps/coherence/iris_transcript_import.py` |
| **Class** | `TranscriptImporter` |
| **Depends on** | `realtimekit_downloader` |

## Purpose

Downloads the Cloudflare RealtimeKit **provider transcript** JSON (if not already on disk)
and imports it into `TranscriptSegment` rows, resolving each `peerData.cpi` to a `person_id`
via `config["enter-coherence"]["participants"]` (falling back to a deterministic negative
placeholder id for unresolved speakers).

This is one of the two transcription sources; use it when the provider transcript is good.
The alternative is [google-transcribe](google-transcribe.md) — see its page for the
"pick one" choice.

## Pipeline position

- **Upstream (`depends_on`):** `realtimekit_downloader`.
- **Feeds into:** `content_generator` (consumes the `TranscriptSegment` rows — a data
  dependency, not a declared `depends_on`).
- **Alternative to:** `google_transcribe`. Both do a **delete-then-insert** of
  `TranscriptSegment` rows; a journey must use exactly one, or whichever runs last silently
  discards the other's output.

## Data flow

**Reads**
- `config["enter-coherence"]["sessionId"]`, `config["enter-coherence"]["participants"]`

**Writes**
- `config["iris.downloads"]["transcript_json"]`,
  `config["iris.downloads"]["transcript_json_expiry"]`
- `TranscriptSegment` rows (model, not JSON config). Re-running **replaces** the
  conversation's segments rather than appending, so a re-import (after clearing the step
  marker) never duplicates the transcript.

## Requirements

- **Agent.config:** `cloudflare.cloudflare_account_id`, `cloudflare.app_id`,
  `cloudflare.api_token` (needed for the session `started_at` lookup — not credential-free).
- **System:** none.
- **External credentials:** Cloudflare RealtimeKit (above).

## Behavior details

The transcript fetch (`GET .../sessions/{id}/transcript?format=JSON`) distinguishes three
cases:

- **Still generating** (no download URL) → `RetryLater`.
- **No JSON transcript for the session** (Cloudflare returns an empty `.csv` placeholder) →
  clear **terminal error** naming the likely cause: transcription not enabled for the
  meeting.
- **A real `.json` transcript** → download + import.

**Offset gotcha:** Cloudflare's `startTime`/`endTime` are absolute Unix epoch
**milliseconds, not offsets**. The job fetches `GET .../sessions/{session_id}` for the
session's `started_at` and computes `offset_ms = entry.startTime - started_at` (clamped to
`>= 0`) itself. (Confirmed against real data; an earlier assumption they were already
relative was wrong.)

See `specs/iris-transcript-dowload-jobstep.md` for full design and open questions.

## Step slug convention

None fixed; place it on the step right after `realtimekit_downloader` (e.g.
`"transcript-imported"` / `"downloaded"`). Matches `config["iris_job"] =
"transcript_importer"`.

## Testing this step

No automated test today. Manual scenario (staging):

- **Happy path:** a session with a real JSON transcript → segments imported, offsets
  computed from `started_at`, speakers resolved via `participants`.
- **Still generating:** a just-ended session → `RetryLater`.
- **Transcription disabled:** a session with only the empty-CSV placeholder → terminal error
  naming the cause.
- **Re-import:** clear the step marker and re-run → segments replaced, not duplicated.

Reset clears the imported rows via `reset_owned_output`. See the
*testing guide* (internal engineering doc, not published here).

## Related runbooks

- *manual-retrigger* (internal engineering doc, not published here)
