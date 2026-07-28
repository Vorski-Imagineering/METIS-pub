# Troubleshooting IRIS

Everything here assumes the model described in [How IRIS works](how-iris-works.md): a
conversation sits on a step, the step's job runs on a timer, and each run either finishes and
moves the conversation on, waits quietly, or fails with a note.

Start on the conversation page. The step rail and the step inspector below it answer most
questions without anyone needing server access.

---

## Why isn't my conversation moving?

Work down this list in order. The first three cover almost every case.

### 1. Is there an error note?

Look at the current step on the rail. **Red ✗ means it failed** — open the step and read the
message, and check the activity timeline for the note. Error notes name the cause: a missing
credential, an expired connection, a rejected upload, a transcript too short to work with.

Fix the underlying cause first, then re-run the step (**Run Now**) or reset it. Re-running
before fixing the cause just reproduces the same error.

### 2. Is it waiting for something?

**No error and no movement usually means waiting**, which is normal. Open the step inspector
and look at the **Reads** row: each input the step needs is listed with ✓ if it's there and ○
if it isn't. A ○ tells you exactly what the step is waiting for, and clicking it jumps to the
step that produces it.

Common legitimate waits:

| Waiting on | Typical duration |
|---|---|
| The recording to finish uploading at the provider | a few minutes after the meeting ends |
| A transcription batch to complete | minutes to tens of minutes, depending on length |
| YouTube to finish processing an upload | minutes; longer for long videos |
| Participants to respond to a review request | up to the publish-by date |

Give it time. It will retry on its own schedule.

### 3. Does the step's job actually run?

If a step is neither erroring nor waiting on anything visible, the job behind it may not be
scheduled at all — in which case the conversation will sit there indefinitely with no error,
because nothing is running to notice it.

Symptoms: the step never shows ◐ Running, never produces a note, and **Run Now** reports that
no schedule exists for it. This is a system configuration matter — ask an administrator to
check the step's job is scheduled and that the background worker is running.

### 4. Is the step a manual one?

A step with no job attached shows *"Manual step — no automated job."* Nothing will ever move
it automatically; someone has to. That's not a fault, it's a checkpoint.

### 5. Is the journey ordered correctly?

A step placed before the step that produces its inputs will wait forever, because its inputs
never arrive while it's blocking the step that would create them. The inspector's Reads row
shows the ○ inputs and which step is supposed to produce each — if the producer is *after* the
waiting step in the journey, the journey is mis-ordered. See
[the step reference](steps/README.md) for the intended order.

---

## Reading the error

Error notes are written to be actionable. Some recurring ones and what they mean:

| The note says | What it means | What to do |
|---|---|---|
| Transcript too short / speakers not resolved | The draft generator refuses to write from a thin or unattributed transcript | Fix the transcript or assign speakers, then reset the generation step |
| Connection expired or revoked (YouTube / LinkedIn) | The stored authorisation is no longer valid | Reconnect on the journey step — see [YouTube setup](youtube-setup.md) |
| Missing configuration / credentials | The step needs a setting nobody has filled in | Add the setting, then re-run the step |
| Cannot reach a participant (no email, no linked Telegram) | The notifier refuses to skip anyone | Add contact details for that person; the step retries and clears itself |
| Result uncertain (LinkedIn) | A post may or may not have been created | Do **not** retry — check LinkedIn manually first; retrying risks a duplicate public post |

## Something is missing from the page

If a whole panel or action isn't there, you probably don't have the access it needs — several
IRIS actions (Run Now, Reset, Send test, connecting a channel) are staff-only. That's a
permissions matter, not a fault.

---

## Resetting and re-running a step

Two different actions, often confused:

- **Run Now** — runs the current step's job again immediately, without clearing anything.
  Use it when you've fixed the cause of a failure, or you just don't want to wait for the
  timer. Safe: every step checks its own work before redoing it.
- **Reset** — clears the step's run state *and the output that step owns*, then puts the
  conversation back on that step so the work is redone from scratch. Use it when the output
  itself is wrong, not just missing.

The reset dialog lists exactly what will be cleared before you confirm. Read it — the blast
radius differs a lot between steps.

### What reset does to the steps after it

Reset fully resets **the step you chose**. Later steps that consumed its output are
**re-armed** so they run again — but their existing output is *not* cleared. A re-armed step
runs with its old output still in place, and what happens then is up to that step: it may
overwrite it, regenerate it, or notice the work is already done and do nothing.

### What reset cannot undo

Reset only touches METIS. It does not:

- delete a video already uploaded to YouTube (a re-run uploads a *second* copy — delete the
  first one on YouTube if that isn't what you want),
- retract a published LinkedIn post, podcast episode, or Telegram message,
- unsend an email or a review request.

So regenerated content can end up differing from what was already published. Past the publish
gate, treat everything as permanent.

### Two special cases

**Transcription is deliberately protected.** A finished transcript is never silently
overwritten, and resetting an earlier step does not trigger re-transcription. Explicitly
resetting a transcription step *is* destructive: it deletes the transcript, the speaker
assignments, and everything derived from the transcript (the conversation's memory, extracted
claims and evidence, and any answers that cited them). Participants' consent decisions are not
touched. Read the confirmation dialog carefully.

**LinkedIn publishing refuses some resets.** A LinkedIn step whose result is *published*,
*submitting*, or *uncertain* cannot be reset — clearing METIS's record would not remove the
post, and would invite a duplicate. Reset is only allowed from a failed or retryable state.

---

## Escalating

If none of the above explains it, collect these before asking for help — they are what anyone
diagnosing it will ask for:

- the conversation link,
- which step it's parked on and the state shown on the rail,
- the exact text of the most recent error note,
- what the step inspector's Reads row shows as still missing (○).
