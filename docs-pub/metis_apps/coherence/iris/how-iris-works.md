# How IRIS works

This page explains the machinery: what actually happens between "the meeting ended" and
"it's published". It is the one page worth reading before any of the others, because nearly
every question about IRIS turns out to be a question about this.

The short version:

> A conversation sits on a **step**. Each step has a small program behind it that **runs on a
> timer**. When it runs, it looks for conversations parked on its step, does its bit of work,
> and moves each one on to the next step. If it can't do its work yet, it leaves the
> conversation exactly where it is and tries again next time.

Everything below is detail on that sentence.

---

## 1. The three words

**Conversation** — one recorded session. It is a record in Coherence with participants,
a recording, a transcript, and everything IRIS produces from it.

**Journey** — the production line a conversation travels along. A journey is an ordered list
of steps. Different journeys can have different steps: one show might publish to YouTube and
LinkedIn, another might only produce a transcript and an internal summary.

**Step** — one station on that line. "Download the recording." "Generate the draft." "Ask
participants to review." A conversation is always at exactly one step — that's its current
position, and it's what you see marked on the conversation page.

Most steps have an automated job attached. A few are **manual steps** with no job at all —
they're markers for something a person does, and a conversation parked on one stays there
until someone moves it.

## 2. Steps run on a timer, not on a button

Nobody starts IRIS for a particular conversation. Each step's job is scheduled to run
independently — typically every few minutes, all day, whether or not there is anything to do.

One run of one job looks like this:

1. **Find work.** The job asks: *which conversations are currently sitting on my step?*
   Only conversations parked exactly there are eligible. A conversation two steps ahead or
   one step behind is invisible to it.
2. **Claim each one.** Before doing anything, it marks the conversation as being worked on,
   so a second run — or a second server — can't pick up the same conversation at the same
   time.
3. **Do the work.** Download the file, call the AI, render the images, send the emails.
4. **Decide what happened** — see the next section.

Then it does the same for the next conversation on its step, and stops until its next
scheduled run. Each conversation is handled independently: one conversation failing never
stops the others in the same run.

The practical consequences:

- **A conversation moves one step at a time**, and only ever forward, and only when the job
  for its current step succeeded.
- **There are gaps between steps.** If every step runs every five minutes, a twelve-step
  journey takes at least an hour of clock time even when every step succeeds first try.
  That is normal and not a sign of a problem.
- **A step with no schedule never runs at all.** The conversation parks there quietly with no
  error, forever. This is the single most confusing failure mode in IRIS — see
  [Troubleshooting](troubleshooting.md).

Staff can skip the wait for the *current* step with the **Run Now** button on the step
inspector. It queues the same job the timer would have run, immediately.

## 3. What a step can do: done, waiting, or failed

Every run of a step on a conversation ends in exactly one of three ways.

### Done ✓

The work succeeded. The job saves what it produced onto the conversation, writes a note in
the activity timeline, and **advances the conversation to the next step in its journey**. If
there is no next step, the conversation stays where it is — it has reached the end.

### Waiting (nothing visible happens)

The step can't do its work *yet*, through no fault of anyone's: the recording is still
uploading, the video is still processing at YouTube, a participant hasn't replied.

The job releases the conversation, leaves it on the same step, and **writes nothing** — no
error, no note, no fuss. The next scheduled run tries again. This repeats, quietly, for as
long as it takes.

**Waiting looks identical to "nothing is happening", and that is the point.** If a
conversation hasn't moved and there is no error note, the overwhelmingly likely explanation
is that a step is waiting for something. See
[why isn't my conversation moving?](troubleshooting.md) for how to tell what it's waiting on.

### Failed ✗

Something is actually wrong: a credential is missing, an external service rejected the
request, the transcript is too thin to write from. The job:

- leaves the conversation on the step — it does **not** advance,
- marks the step as errored, so the step shows red on the conversation page,
- writes a note on the conversation saying what went wrong.

Nothing retries a failure on its own. A person has to fix the cause and re-run or reset the
step. That is deliberate: retrying a genuine error every five minutes forever would spam
external services and bury the real problem.

### What that looks like on screen

The conversation page shows every step of the journey as a rail of nodes:

| Marker | Meaning |
|---|---|
| ✓ Done | Ran successfully, conversation moved on |
| ◐ Running | Being worked on right now |
| ✗ Error | Failed — read the note; nothing will move until it's resolved |
| **Current** | Where the conversation is now (also marked ▼ on the rail) |
| Pending | Not reached yet |

Selecting a step opens its **inspector**, which shows what that step needs (its inputs, each
ticked ✓ if present or ○ if still missing), what it produces, when it last ran and for how
long, and the staff actions available on it.

## 4. Everything lives on the conversation

There is no separate queue, dashboard, or job console to go and look at. Every piece of state
IRIS has about a conversation is stored on the conversation itself:

- **Which step it's on** — its position in the journey.
- **Per-step run state** — pending, running, done, or errored, with timestamps.
- **The work product** — the title, description, quotes, image files, video URL, per-person
  notification and approval records.
- **The activity timeline** — a note for each completed step, and a note for each failure with
  its error text.

So the conversation page is the whole picture, and the answer to "what happened to this?" is
always on it. It also means nothing is lost if a background worker crashes: the next run
picks up from the state on the record.

## 5. Re-running, and what resetting means

Because a step's run state is stored per step, it can be cleared and the step run again.
**Reset** on the step inspector does that: it clears the step's own run state *and the output
that step produced*, then puts the conversation back on that step so the next run redoes it.
The confirmation dialog spells out exactly what will be cleared before you commit.

Two things about reset are worth internalising:

- **Steps are safe to re-run.** Every step is written to check its own work first: the video
  uploader never uploads a second copy if a video already exists, the notifier never emails
  someone twice, the migrator verifies the object is already in the bucket. Retrying is a
  routine event in IRIS, not an emergency, so steps are built to survive it.
- **Reset only cleans up inside METIS.** It cannot un-publish a YouTube video, un-send an
  email, delete a LinkedIn post, or withdraw a podcast episode. Anything that already left
  the building stays out there and has to be removed at the source.

Details and the exceptions (transcripts and LinkedIn are special) are in
[Troubleshooting → resetting a step](troubleshooting.md#resetting-and-re-running-a-step).

---

## Why it's built this way

Some of IRIS's behaviour looks odd until you know what it is protecting against.

**Why lots of small steps instead of one big "publish this" button?**
Publishing a conversation means waiting on half a dozen external services — a recording that
takes minutes to become available, a transcription that takes longer, YouTube processing,
and human beings replying to email. A single long-running process would spend most of its
life asleep, and any failure two hours in would throw away the two hours of work before it.
Splitting the work into steps means each piece of progress is saved the moment it's made,
and a failure costs you one step, not the whole run.

**Why does waiting look like nothing at all?**
Because "not ready yet" is the normal case, not an exception. If every unfinished YouTube
upload raised an error, the error list would be mostly noise and the real failures would be
invisible in it. Errors are reserved for things a person must act on. The cost is that
patience looks identical to paralysis — which is why the step inspector shows you which
inputs are still missing.

**Why is the conversation the source of truth, rather than a job queue?**
So there is exactly one place to look. Anyone who can see the conversation can see how far it
got, what it produced, and why it stopped, without access to a server or a background-jobs
console. It also makes the system restartable: the schedule can be stopped and started and
nothing is lost, because no progress was ever held in memory.

**Why does the pipeline stop dead when one participant can't be reached?**
The notification step refuses to start the publish clock until every participant has actually
been contacted. It would be easy to skip the unreachable person and carry on — and that is
exactly the failure everyone would regret, because publishing goes ahead by default when the
deadline passes. Someone who was never told cannot object. Blocking is the safe direction.

**Why is the video uploaded as *unlisted* first?**
So participants review the real thing — the actual hosted video, with its real title and
thumbnail — instead of a description of what will exist later. Making it public is a separate,
later step that only runs after the review gate clears.

**Why do resets not undo external publishing?**
Because they honestly can't in every case, and pretending otherwise would be worse than not
trying. A LinkedIn post published by a person can only be removed by that person. Instead of
a partial, unreliable "undo", IRIS makes the boundary explicit: everything before the publish
gate is freely repeatable, everything after it is real and permanent, and the gate is the
place where humans decide.

**Why is so much configurable per journey?**
Because the pipeline is the same shape for every show but the specifics never are — different
brand voice, different YouTube channel, different image templates, different notification
copy, different grace period. Those live as settings on each journey's steps, so a new show
is a cloned journey with different settings rather than new code.

---

## Glossary

| Term | Means |
|---|---|
| **Conversation** | One recorded session and everything derived from it. |
| **Journey** | The ordered list of steps a conversation travels through. |
| **Step** | One station on the journey. Has a job behind it, or is manual. |
| **Job** | The program behind a step. Runs on a timer; one per step type. |
| **Current step** | Where the conversation is right now. |
| **Advance** | Moving a conversation to the next step after a step succeeds. |
| **Waiting / retry** | A step deciding it can't run yet, silently, and trying again later. |
| **Note** | A timeline entry on the conversation — one per completed step, one per failure. |
| **Reset** | Clearing a step's run state and its output so it can run again. |
| **Unlisted** | A YouTube video only reachable by link — not public, not searchable. |
| **Publish-by date** | The date after which publishing proceeds unless someone opted out. |

## Where to go next

- [Using IRIS](using-iris.md) — what to click, stage by stage.
- [The pipeline steps](steps/README.md) — what each individual step does.
- [Troubleshooting](troubleshooting.md) — when it hasn't moved, or has gone red.
