# Using IRIS — the staff walkthrough

Where to click, stage by stage, for staff running conversations through IRIS.

- For *what IRIS produces*, see [What IRIS does](what-iris-does.md).
- For *how the pipeline actually runs*, see [How IRIS works](how-iris-works.md) — read that
  first if you haven't; this page assumes it.
- For *it's stuck / it's gone red*, see [Troubleshooting](troubleshooting.md).

> This page assumes you can find your way around the app (see
> [Getting started](../../../web/app/getting-started.md) and
> [Focus](../../../web/app/focus-and-scoping.md)) and have Coherence access. If a Coherence
> nav item or conversation isn't visible to you, that's a permissions matter, not a fault.

---

## 1. Start from a conversation on a publishing journey

Conversations normally arrive automatically from the cal.com booking webhook rather than a
create form — see [Events & Conversations](../events-and-conversations.md) for where they come
from.

What IRIS needs before it can do anything useful:

- **The conversation is on a publishing journey.** The standard one is cloned from the *IRIS
  Standard Journey* template.
- **Participants are attached** — the people who took part. IRIS uses them to resolve speakers
  in the transcript, personalise LinkedIn copy, and send review links.
- **Related holons are connected** (the organisation, the event), if generation prompts should
  draw on them for context.

## 2. Read the conversation page

Everything IRIS knows is on this one page.

**The step rail** across the journey shows each step and its state — ✓ done, ◐ running,
✗ error, **Current** (also marked ▼), or pending. Click any step to open its **inspector**
below the rail.

**The step inspector** shows, for the selected step:

- what it needs (**Reads**), each input ticked ✓ if present or ○ if still missing — click a ○
  to jump to the step that produces it;
- what it produces (**Owns**) — which is also exactly what a reset of this step would clear;
- when it last ran and how long it took;
- staff actions: **Run Now**, **Reset…**, **Go To**, and **Send test…** on notifier steps.

**The activity timeline** carries a note for every completed step and a note for every
failure, with the error text. It is the first place to look when something is stuck.

Steps advance by themselves on success. A step that's simply waiting on something writes
nothing at all — no error, no note, no movement. That's the normal case, not a fault.

## 3. Recording and transcript

The recording is fetched a few minutes after the meeting ends (it isn't available at the
provider before then, so the step waits). The transcript follows — either imported from the
meeting provider or generated from the audio, depending on which transcription step the
journey uses.

Your job here is to **check speakers are matched to real people**. Unmatched speakers block
draft generation, deliberately.

## 4. Review and edit the generated draft

Generation produces the **Publishing** draft: title, subtitle, summary, YouTube description,
the LinkedIn post, and key quotes. In the Publishing panel you can:

- **edit any field** inline — edited fields are marked as manually edited;
- **Regenerate** — clears the draft and re-runs generation. Use it after the transcript
  improves (speakers matched) or after you change the prompts. You can record a reason, which
  goes into the activity trail.

If the transcript is too short or speakers are unresolved, IRIS **stops and leaves a note**
rather than generating weak content. Fix the cause, then regenerate.

## 5. Tune the generation prompts

The AI instructions are settings on the journey step, editable in the web UI — no developer
needed. You can set a shared base instruction plus one per output (title, subtitle,
description, LinkedIn post, quotes), and inject live conversation context into any of them.

Full detail: [Writing prompts](writing-prompts.md).

## 6. Cover images and hosted video

- **Cover images** — branded thumbnail, LinkedIn header, and quote cards, rendered from the
  approved content. The Cover Images panel shows status and previews; re-render after content
  changes, or retry a failed render.
- **Hosted video** — the recording is uploaded to YouTube as **unlisted**, so reviewers
  approve the real video. The panel shows upload and processing status. Re-running the
  metadata step re-pushes an edited title or description; re-running the thumbnail step
  re-pushes a regenerated thumbnail. Connecting a channel is a one-time setup per journey:
  [YouTube setup](youtube-setup.md).

## 7. Participant review

Each participant gets a personal **review link** — video, title, subtitle, thumbnail, quotes,
and the LinkedIn draft they can edit — plus a **publish-by date**.

The conversation waits at this gate until either every participant confirms early or the date
passes. Anyone who **opts out** blocks publishing outright; no deadline overrides that.

Before it goes out, use **Send test…** on the notifier step to read the actual copy against
this conversation. It offers *Send to me* (safe — re-rendered with your own link) and *Send to
the participant* (a real message to a real person, with a confirmation prompt).

If a participant has no email and no linked Telegram, the step **stops rather than skipping
them** — add their contact details and it clears itself on the next run.

The participant's own guide is [here](participant-review.md) and is written to be forwarded.

## 8. After review

Once the gate clears, the remaining steps run on their own: the video goes public, LinkedIn
posts are published, the recording is archived to cloud storage, the podcast episode is
created, and everyone gets the public links.

From your side each is just another step with a state and a note. What each one does is
documented in [the step reference](steps/README.md).

---

## When something's stuck

The short version:

- **No movement, no error** → a step is waiting. Check the inspector's Reads row for ○ inputs.
- **Red ✗** → read the note, fix the cause, then **Run Now** or reset the step.
- **"Blocked" banner on a journey step** → the step's own settings or credentials are
  broken (an expired token, a rejected mail login), so nothing on it runs for anyone.
  Fix what the banner names, then save the step's config — or press **Retry now** if you
  fixed it elsewhere. Nothing was lost: the waiting conversations resume on the next run.
- **Missing panel or button** → you don't have the access it needs.

The long version, including what reset clears and what it can never undo, is in
[Troubleshooting](troubleshooting.md).
