# Transcript Importer

Imports the transcript the meeting provider produced, and matches each speaker to the real
person who was in the meeting.

One of **two alternative** transcription steps — a journey uses this **or**
[Google Transcribe](google-transcribe.md), never both. Use this one when the provider's
transcript is good.

## At a glance

| | |
|---|---|
| **Needs** | The meeting session reference, and the participant list from booking |
| **Produces** | The conversation's transcript, with speakers attributed |
| **Waits when** | The provider is still generating the transcript |
| **Re-running** | Safe — replaces the transcript rather than duplicating it. But see *Resetting* below: a finished transcript is protected |

## What it does

Downloads the transcript file from the meeting provider and turns it into the conversation's
transcript, one segment per utterance. Each speaker is matched to a real Person using the
participant list captured when the meeting was booked; a speaker who can't be matched becomes
an unresolved placeholder that someone assigns by hand in the assign-speakers UI.

Getting speakers matched matters beyond tidiness: [Content Generator](content-generator.md)
refuses to write from a transcript whose speakers are unresolved.

## How it behaves

- **Three outcomes when it asks for the transcript**: still being generated (waits and retries),
  no transcript exists for the session (fails, with a note naming the likely cause —
  transcription wasn't enabled for the meeting), or a real transcript (imports it).
- **Timings are recalculated.** The provider reports absolute clock times, not offsets into
  the recording, so the step fetches the session start and computes each segment's position
  itself. This is why it needs the provider credentials even though it's "just" importing a
  file.
- **Re-importing replaces, never appends** — you can't end up with a doubled transcript.

## Resetting this step

A finished transcript is not silently overwritten: an import that disagrees with the stored
transcript is refused. Resetting the step is the sanctioned way to replace it, and it is
**destructive**:

- The transcript and its speakers are deleted. Nothing is lost by dropping the speakers here —
  this step re-derives each speaker from the participant list on every import.
- Anything derived from the transcript is deleted with it: the conversation's memory build,
  its extracted claims and evidence, and any answers that cited that evidence. Participants'
  **consent decisions are not touched** — only what was derived from the transcript.
- Steps downstream that used the transcript are re-armed so they regenerate against the new
  one.

This is also how you switch a journey between this step and Google Transcribe: the second
source is refused while a transcript stands, and accepted after a reset.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| Waiting shortly after the meeting | The provider is still generating the transcript | Normal. It retries on its own. |
| Error: no transcript for the session | Transcription wasn't enabled for that meeting | Nothing to import. Switch the journey to [Google Transcribe](google-transcribe.md) to transcribe from the audio instead |
| Transcript imported but speakers show as placeholders | Those speakers weren't in the booking participant list | Assign them by hand in the assign-speakers UI, then regenerate the draft |
| Error mentioning credentials | Provider credentials missing or wrong on the agent | An administrator corrects them; then re-run |
| Segments appear at wrong times | Session start couldn't be resolved | Re-run the step; if it persists, report it — timings are computed from the session start |
| Re-import refused | A finished transcript already exists | Deliberate. Reset the step if you really mean to replace it — read the warning first |

## Technical reference

| | |
|---|---|
| **Step type** | `transcript_importer` |
| **Runs after** | `realtimekit_downloader` |
| **Alternative to** | `google_transcribe` (both replace the whole transcript — use exactly one) |
| **Feeds** | `content_generator` |
| **Reads** | `config["enter-coherence"]["sessionId"]`, `config["enter-coherence"]["participants"]` |
| **Writes** | `TranscriptSegment` rows; `config["iris.downloads"]["transcript_json"]`, `["transcript_json_expiry"]` |
| **Needs on the agent** | `cloudflare.cloudflare_account_id`, `cloudflare.app_id`, `cloudflare.api_token` |
