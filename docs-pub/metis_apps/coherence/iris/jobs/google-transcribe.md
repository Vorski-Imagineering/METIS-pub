# Google Transcribe (Chirp-3)

| | |
|---|---|
| **Label** | Google Transcribe (Chirp-3) |
| **Slug** | `google_transcribe` |
| **File** | `metis_apps/coherence/iris_google_transcribe.py` |
| **Class** | `GoogleTranscribe` |
| **Depends on** | `realtimekit_downloader` |

## Purpose

Transcribes the downloaded recording with Google Cloud Speech-to-Text v2 (`chirp_3`, speaker
diarization on) and writes `TranscriptSegment` rows — an **alternative to**
[transcript-importer](transcript-importer.md) for journeys that would rather transcribe from
audio than import the provider transcript. Transcription mechanics live in
`chirp_transcribe.py` (ffmpeg → GCS → BatchRecognize → parse). Diarized speakers become
negative `person_id` placeholders with `enter-coherence["Speaker N"]` labels, resolved to
real participants via the existing assign-speakers UI.

## Pipeline position

- **Upstream (`depends_on`):** `realtimekit_downloader`.
- **Feeds into:** `content_generator` (data dependency on the `TranscriptSegment` rows).
- **Alternative to:** `transcript_importer` — use one or the other, never both (both do a
  delete-then-insert of `TranscriptSegment` rows). Pick `transcript_importer` when the
  provider transcript is good; pick `google_transcribe` when the recording is good but the
  provider transcript is bad/missing.

## Data flow

**Reads**
- `infos["audio"]` (preferred canonical audio), else `config["iris.downloads"]["recording"]`
  as the extraction fallback.
- `config["iris.downloads"]["chirp_stt"]` — its own in-flight batch state.
- `JourneyStep.config` (`language`, `min_speakers`, `max_speakers`).

**Writes**
- `infos["audio"]` when extraction creates the first canonical FLAC.
- `config["iris.downloads"]["chirp_stt"]` — in-flight batch state (set on submit, cleared on
  collect/error).
- `config["enter-coherence"][<person_id>]` — "Speaker N" labels.
- `config["iris.downloads"]["chirp_transcript"]` — model, language, at, segment count.
- `TranscriptSegment` rows (model). Re-running **replaces** the segments rather than
  appending.

## Requirements

- **Agent.config:** `google.credentials` (service-account JSON dict — Speech-to-Text +
  Storage Object Admin), `google.stt_bucket` (GCS staging bucket in the **US multi-region**).
- **System:** `ffmpeg` + `ffprobe` on PATH; Speech-to-Text API enabled on the project.
- **External credentials:** Google Cloud (above). `chirp_3` single-pass diarization caps at
  **60 minutes** — longer recordings are rejected with a clear error, not truncated.

## Behavior details

**Async (submit-then-collect) — why it does not block.** Chirp `BatchRecognize` is a
long-running server-side job. Waiting on it inline would block a django-q2 worker for
minutes; the cluster's 300s task timeout then reaps the worker mid-run, stranding
conversations at `processing` forever. This step therefore **never blocks on the batch job**.
Each scheduled run does two passes:

1. **Collect** (cheap, every in-flight conversation): if a conversation carries
   `chirp_stt`, poll the batch operation *by name* (`poll_batch_operation`) — polling the
   operation, not just the output folder, is what lets a failure fail fast. Outcomes:
   op failed → error immediately (staging deleted); op running → `RetryLater`, staging never
   deleted while a batch is live; op done + results → write segments, delete staging,
   advance (empty results → "no words" error); op done + no output after
   `RESULT_GRACE_SECONDS` → "produced no transcript output"; status unknown → if nothing was
   staged, re-run submit, else GCS-poll bounded by `MAX_POLL_SECONDS` (1h — the only path
   that times out).
2. **Submit** (bounded by `SUBMIT_BUDGET_PER_RUN`, default 5): for a conversation with no
   in-flight state, use `infos["audio"]` or extract a FLAC from the recording, stage in GCS,
   fire `BatchRecognize` **non-blocking**, persist `chirp_stt`, post a FLOW "submitted" note,
   and `RetryLater`. State is committed per-conversation immediately, so a reaped run loses
   at most one in-flight conversation. Over a few runs the whole backlog drains concurrently.

- **Self-healing:** a `processing` marker surviving *between* runs can only mean a
  crashed/reaped run. `_reclaim_stale_processing` clears such markers older than
  `STALE_PROCESSING_SECONDS` (15 min) at the top of each run, leaving any `chirp_stt` intact
  so a crash mid-submit resumes at Collect.
- **Hard error** (transcript left untouched) if Chirp returns zero words, so a silent/short
  recording never wipes an existing transcript.
- **Notes:** FLOW "recording submitted to Chirp" on submit, base "… completed" on success;
  routine per-poll / budget-deferral `RetryLater`s are silent (`notify=False`).

## Step slug convention

None fixed; place it where `transcript_importer` would go (right after
`realtimekit_downloader`) and use it **instead of** `transcript_importer`. Matches
`config["iris_job"] = "google_transcribe"`.

## Testing this step

- `test_iris_google_transcribe.py` and `test_recover_transcript_chirp.py` cover the
  submit/collect state machine and the stale-processing recovery / `write_chirp_segments`
  path (shared with the `recover_transcript_chirp` management command). What they **don't**
  cover is a real staging `BatchRecognize` round trip — exercise that on staging with valid
  `google.credentials` + `google.stt_bucket`.

Run: `python3 manage.py test --keepdb --parallel auto metis_apps.coherence`. See the
*testing guide* (internal engineering doc, not published here).

## Related runbooks

- *manual-retrigger* (internal engineering doc, not published here)
