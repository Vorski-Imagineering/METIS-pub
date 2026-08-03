# Transcript Importer

Imports the transcript the meeting provider produced, and matches each speaker to the real
person who was in the meeting.

One of **two alternative** transcription steps — a journey uses this **or**
[Google Transcribe](google-transcribe.md), never both. Use this one when the provider's
transcript is good.

## At a glance

| | |
|---|---|
| **Needs** | The approved conversation window, the meeting session reference, and the participant list from booking |
| **Produces** | The conversation's transcript, with speakers attributed |
| **Waits when** | The provider is still generating the transcript |
| **Waits also when** | The approved window hasn't been written yet (it keeps retrying for a while, then fails) |
| **Imports nothing when** | The conversation's approved window is missing — see *Only the conversation* below |
| **Re-running** | Safe — replaces the transcript rather than duplicating it. But see *Resetting* below: a finished transcript is protected |

## What it does

Downloads the transcript file from the meeting provider and turns it into the conversation's
transcript, one segment per utterance — but only the part of it that belongs to the
conversation, see below. Each speaker is matched to a real Person using the
participant list captured when the meeting was booked; a speaker who can't be matched becomes
an unresolved placeholder that someone assigns by hand in the assign-speakers UI.

Getting speakers matched matters beyond tidiness: [Content Generator](content-generator.md)
refuses to write from a transcript whose speakers are unresolved.

## Only the conversation, never the whole meeting

Both people stay in one meeting for the whole flow: lounge, consent, conversation, and the
post-lounge afterwards. The provider transcribes the **entire meeting**, so its file can contain
things said before anyone agreed to be recorded and after the conversation was ended.

So the application records the interval it approved — the moment capture was confirmed and the
conversation admitted, and the moment the last microphone went quiet — and this step imports
**only the sentences that lie wholly inside it**:

- A sentence that straddles either edge is dropped whole. There is no way to know which words
  fell on which side, and half a sentence is not worth the risk of leaking the other half.
- Nothing is stretched to be helpful. There is no grace period, no rounding, no guessing the
  boundary from when recording happened to start or from where the transcript happens to begin.
- **No window, no transcript.** If either boundary is missing the step waits for a while (the
  app writes the end boundary when the last microphone goes quiet, which can be after the step
  first looks) and then fails, rather than falling back to the whole meeting. This is
  deliberate: importing too much is a privacy incident, importing nothing is an error someone
  can see and fix.
- Timings are counted from the start of the conversation, so a transcript begins at 00:00 when
  the conversation did — not minutes in, where the lounge ended.

Every excluded sentence is counted with the reason it was excluded (before the start, after the
end, crossing an edge, or a timestamp that couldn't be trusted), so "why is that line not in the
transcript?" always has an answer, and an empty transcript can be told apart from a failed one.

**The provider's own file is never kept.** It covers the whole meeting, so storing it would keep
the very speech this step exists to leave out — it is fetched, filtered, and discarded within the
run. The step records how many rows it saw and excluded, plus a fingerprint of the file, rather
than offering the file itself for download.

That accounting is readable over the API at
`GET /api/coherence/conversations/{id}/transcript/import-evidence` (see the
[Coherence API playbook](../../../../api/coherence-PLAYBOOK.md#read-the-transcript-import-evidence)),
so a caller with its own copy of the provider file can check the fingerprint and the counts
against it. Counts and fingerprints only — never the excluded lines themselves.

A conversation whose transcript was imported **before** this rule existed keeps it: this step
reports it rather than rewriting or deleting history. Ask an administrator to run the transcript
window audit for the list.

## How it behaves

- **Three outcomes when it asks for the transcript**: still being generated (waits and retries),
  no transcript exists for the session (fails, with a note naming the likely cause —
  transcription wasn't enabled for the meeting), or a real transcript (imports it).
- **Timings are recalculated.** The provider reports clock times, not offsets into the
  conversation, so the step fetches the meeting session's start and end and computes each
  sentence's position itself. This is why it needs the provider credentials even though it's
  "just" importing a file. A sentence whose timing can't be placed with confidence is dropped
  and counted, never guessed at.
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

**Reset is refused for a transcript that could not be imported again.** If a conversation has a
transcript but no approved window — an older one, from before this rule — resetting would delete
it with nothing able to replace it, because a re-import without a window imports nothing and the
boundaries of a past conversation can't be reconstructed. The step says so instead of clearing
it. Removing such a transcript is a deliberate deletion, not a reset.

This is also how you switch a journey between this step and Google Transcribe: the second
source is refused while a transcript stands, and accepted after a reset.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| Waiting shortly after the meeting | The provider is still generating the transcript | Normal. It retries on its own. |
| Error: no transcript for the session | Transcription wasn't enabled for that meeting | Nothing to import. Switch the journey to [Google Transcribe](google-transcribe.md) to transcribe from the audio instead |
| Error mentioning a missing transcript window | The application never recorded when the conversation started/ended | Not fixable here — the conversation app must send the boundaries. Nothing is imported until it does |
| Error saying no rows fall inside the window | Everything the provider transcribed was outside the conversation | Check the raw file and the boundaries before assuming a bug — a conversation where nobody spoke on the record looks exactly like this |
| Reset refused, naming a missing window | The transcript predates this rule, so it cannot be re-imported | Write the window first if you can; otherwise treat removing it as a deliberate deletion |
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
| **Reads** | `config["enter-coherence"]`: `meetingId`, `participants`, `conversationStartedAt`, `captureEndedAt` (the last two are required) |
| **Writes** | `TranscriptSegment` rows; `config["iris.transcript_import"]["evidence"]` (the per-import row accounting, including the artifact's fingerprint) |
| **Needs on the agent** | `cloudflare.cloudflare_account_id`, `cloudflare.app_id`, `cloudflare.api_token` |
