# Google Transcribe

Transcribes the recording's audio with Google's speech-to-text, separating the speakers as it
goes.

One of **two alternative** transcription steps — a journey uses this **or**
[Transcript Importer](transcript-importer.md), never both. Use this one when the recording is
good but the meeting provider's transcript isn't (or doesn't exist).

## At a glance

| | |
|---|---|
| **Needs** | The downloaded recording |
| **Produces** | The conversation's transcript, with speakers separated but unnamed |
| **Waits when** | The transcription batch is still running at Google — routinely several minutes |
| **Re-running** | Safe. But see *Resetting* below: re-running deletes manual speaker assignments |

## What it does

Extracts audio from the recording, sends it to Google Cloud Speech-to-Text for transcription
with speaker separation, and writes the result as the conversation's transcript.

Speaker separation tells apart *how many distinct voices* there are, not *who they are*. Each
one arrives as "Speaker 1", "Speaker 2" and so on, and someone assigns real people to them in
the assign-speakers UI. That assignment matters:
[Content Generator](content-generator.md) refuses to write from a transcript whose speakers
are unresolved.

**Length limit:** single-pass transcription with speaker separation caps at **60 minutes**.
A longer recording is rejected up front with a clear error rather than being silently
truncated.

## How it behaves

**It submits the work and comes back for it later.** Transcription takes minutes, which is far
longer than a background job is allowed to run, so this step never sits and waits. Each run
does two things:

1. **Collects** any conversation whose transcription was submitted earlier — asking Google
   whether that specific job finished, failed, or is still running.
2. **Submits** a few conversations that haven't been submitted yet (a handful per run, so one
   busy run can't monopolise the queue), then waits.

Over a few runs, a backlog drains steadily and several conversations transcribe concurrently.
The practical effect for you: a conversation sits on this step for several minutes with no
error, which is normal, and the timeline shows a "submitted" note while it's in flight.

Other behaviour worth knowing:

- **It recovers from crashes.** If a run dies mid-flight, the next run notices the abandoned
  claim, clears it, and resumes from wherever it got to — no manual intervention.
- **An empty result never wipes a good transcript.** If transcription comes back with no
  words at all, the step errors and leaves any existing transcript untouched.
- **Routine waiting is silent** — no notes are written while polling, so the timeline doesn't
  fill up with noise.

## Resetting this step

A finished transcript is not silently overwritten: a re-run producing different text is
refused. Resetting is the sanctioned way to replace it, and it is **destructive**:

- The transcript is deleted, **including any manual speaker assignment**. This one is not
  recoverable by re-running: speaker separation numbers voices arbitrarily each time, so
  "Speaker 2" next run needn't be the person it was last run. Keeping the old mapping would
  attach the wrong name to a voice, so it's discarded and speakers must be re-assigned.
- Anything derived from the transcript is deleted with it: the conversation's memory build,
  its extracted claims and evidence, and any answers that cited that evidence. Participants'
  **consent decisions are not touched**.
- Steps downstream that used the transcript are re-armed so they regenerate.

Nothing else is affected — the recording, the uploaded video, and publishing records stay.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| No movement for several minutes, a "submitted" note in the timeline | Transcription is running at Google | Normal. It collects the result on a later run. |
| No movement and no "submitted" note | Waiting its turn — only a few submissions happen per run | Normal on a busy backlog. Give it a few runs. |
| Error: recording too long | Over the 60-minute speaker-separation limit | Use the provider transcript instead, or split the recording |
| Error: no words / no transcript output | Silent, corrupt, or extremely short audio | Check the recording actually has audio; any existing transcript was left alone |
| Error mentioning credentials or a storage bucket | The Google service account or staging bucket isn't configured correctly | An administrator fixes the agent configuration, then re-run |
| Speakers are all "Speaker 1/2/3" | Expected — this step separates voices but can't name them | Assign real people in the assign-speakers UI, then regenerate the draft |
| Re-run refused | A finished transcript already exists | Deliberate. Reset the step if you really mean to replace it — you'll lose speaker assignments |

## Technical reference

| | |
|---|---|
| **Step type** | `google_transcribe` |
| **Runs after** | `realtimekit_downloader` |
| **Alternative to** | `transcript_importer` (both replace the whole transcript — use exactly one) |
| **Feeds** | `content_generator` |
| **Reads** | `infos["audio"]` or `config["iris.downloads"]["recording"]`; its own in-flight state at `config["iris.downloads"]["chirp_stt"]`; step settings `language`, `min_speakers`, `max_speakers` |
| **Writes** | `TranscriptSegment` rows; `infos["audio"]`; `config["enter-coherence"][<person_id>]` speaker labels; `config["iris.downloads"]["chirp_transcript"]` |
| **Needs on the agent** | `google.credentials` (Speech-to-Text + Storage Object Admin), `google.stt_bucket` (US multi-region) |
| **Needs on the server** | `ffmpeg`, `ffprobe`; Speech-to-Text API enabled |
| **Model** | Chirp 3, single-pass diarization (60-minute ceiling) |
