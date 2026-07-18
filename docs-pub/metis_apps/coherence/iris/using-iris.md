# Using IRIS — Conversations Walkthrough

A click-path companion for staff running conversations through IRIS. For *why* IRIS exists
and what it produces, see [What IRIS does](user-benefit-iris.md); this page is the "where do
I click" version.

IRIS runs on **Conversations** in Coherence. A conversation moves through a **Journey** of
steps, and each IRIS stage is a step that processes the conversation and advances it. You
watch and steer all of this from the **conversation detail page**.

> This page assumes you can already find your way around the app (see
> [Getting started](../../../web/app/getting-started.md) and
> [Focus](../../../web/app/focus-and-scoping.md)) and have Coherence access. If a Coherence
> nav item or conversation isn't visible to you, that's a permissions matter, not a bug.

---

## 1. Start from a conversation on a publishing Journey

This walkthrough picks up once a conversation already exists. Conversations normally arrive
automatically via the cal.com booking webhook, not a manual create form — see
[Events & Conversations](../events-and-conversations.md) for where they come from and how
that's wired up. What matters for IRIS is that the conversation sits on a publishing Journey
(the standard one is cloned from the *IRIS Standard Journey* template) with its
**participants** attached — the People who took part, which IRIS uses to resolve speakers,
personalise LinkedIn drafts, and send approval links later — and any relevant **holons**
(the organisation or event) connected, since generation prompts can pull them in as context.

## 2. Read the conversation's progress

On the conversation detail page you can see:

- **Where it sits in its Journey** — the current step is the IRIS stage it's waiting on or
  running.
- **The Activity timeline / notes** — every IRIS stage writes a note when it completes, and
  an **error note** if it fails. This is the first place to look when something's stuck: a
  failed stage leaves the conversation on its step with a note explaining why.

Each stage advances the conversation automatically on success. If a stage is simply waiting
on something (a recording still processing, an approval outstanding), it quietly retries on
its schedule — no error, it just hasn't moved yet.

## 3. Recording capture

Once the meeting recording is ready, IRIS downloads it and attaches it to the conversation
(from RealtimeKit). Recordings become available a few minutes after a meeting ends; until
then the download stage simply keeps waiting. Nothing for you to do here beyond confirming
the recording has landed.

## 4. Review and edit the generated draft

When generation runs, IRIS produces a **Publishing Draft** on the conversation from the
transcript: title, subtitle, summary, YouTube description, LinkedIn post drafts (host and
guest), and key quotes. In the Publishing Draft panel you can:

- Review and **edit any field** inline.
- **Regenerate** — clears the current draft and re-runs generation. Use this after the
  transcript improves (e.g. speakers get matched to real people) or after you change the
  prompts. You can enter a reason, which is recorded in the activity trail.

If the transcript is too short or speakers still need matching, IRIS **stops and leaves a
note** instead of generating weak content — fix the underlying issue, then regenerate.

## 5. Tune the generation prompts

The instructions IRIS gives the AI are configurable per journey step through the web UI — no
developer needed. You can adjust the prompt for each output (title, description, LinkedIn
posts, quotes, and shared base instructions) and inject live conversation context. Full
detail: [Content Generator — Prompt Authoring Guide](jobs/content-generator-prompts.md).

## 6. Cover images and hosted video

- **Cover images** — IRIS renders branded thumbnail, LinkedIn header, and quote-card images
  from the approved content. The Cover Images panel shows their status and previews; you can
  **re-render** if you changed the content, and **retry** a failed render.
- **Hosted video** — IRIS uploads the recording to YouTube as an **unlisted** video, so
  reviewers approve the real hosted video rather than a local file. The Hosted Video panel
  shows upload/processing status, with **Retry Upload** (if the upload failed) and **Sync
  Status** (re-poll processing without re-uploading). Setup for connecting a channel is in
  [YouTube uploader setup](jobs/youtube-uploader-setup.md).

## 7. Participant approval

IRIS can send each participant a personal **approval link** to review the hosted video,
title, subtitle, thumbnail, quotes, and their own LinkedIn draft (which they can edit before
approving). While any required approval is outstanding, the conversation shows as **waiting
on approval** and doesn't advance. Once all required approvals are in, it moves on. The
participant's side of this is documented in the
[Participant Approval Guide](participant-approval.md).

## 8. After approval

Once approved, IRIS carries the operational work forward through further stages — archiving
the recording to cloud storage, preparing the podcast episode, queuing LinkedIn posts for
participants, and creating a Telegram distribution note. From your side each is just another
stage on the conversation with its own status and notes; you don't run them by hand. What
happens inside each is documented per stage in the developer job reference, but as a user you
only need the conversation's timeline: each stage reports success, waiting, or a clear error.

---

## When something's stuck

- **It hasn't moved but there's no error** — a stage is waiting on something (recording,
  approval, an upstream step). Give it time; it retries on schedule.
- **There's an error note** — read it; it names the cause. Fix the underlying issue, then use
  the relevant panel's Regenerate/Retry, or ask an admin to re-trigger the step.
- **A whole panel is missing** — you may not have the access it requires.
