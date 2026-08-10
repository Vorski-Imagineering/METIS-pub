---
name: holon-outreach
description: >
  Use when the user wants to message a batch of METIS people who share a specific holon,
  Journey, and step — e.g. "message the people awaiting outreach on <holon>", "contact
  everyone at 'To Contact' for <gathering>", "run outreach for <holon>'s Outreach journey".
  Combines METIS worklist lookup with paced LinkedIn messaging and journey-step advancement.
  Trigger on: "find/message people awaiting outreach", "who's at step X on <holon>", "advance
  their journey after messaging", "bulk invite people in <holon>".
---

# Holon Outreach

Finds METIS people at a given Holon + Journey + step, messages each on LinkedIn using an
existing message file, and advances their Membership with a note recording what happened.

## Routing

Run the `/holon-outreach` command — read `.claude/commands/holon-outreach.md` before starting.
It composes two other skills rather than reimplementing them:

- **REQUIRED SUB-SKILL:** `metis` — for holon/membership lookup and membership updates.
- **REQUIRED SUB-SKILL:** `linkedin-automation` — for pacing rules (`humanDelay`, burst
  breaks, foreground-tab/throttle detection). Read its **Pacing** section before looping over
  people; do not re-derive delay numbers here.

## Non-obvious rules baked into the command (learned the hard way)

- **Never guess which holon.** A name like "USA Gathering" can fail to exact-match anything
  in `GET /holons?q=`, while a near-variant ("2026 USA California") does. Always show the
  matched candidate(s) and get explicit confirmation before running outreach against it —
  see the command's holon-resolution step.
- **Check the thread before sending.** A person's LinkedIn message thread can already contain
  the exact invite text from a prior manual or automated send. Sending again duplicates it.
  Always read the thread's existing text first; if the message (or a close match) is already
  there, don't resend — just advance the Membership with a note explaining why.
- **Message copy comes from a file, never invented inline** — so the wording stays exactly what
  the user prepared. **Take the path from the user; don't assume `texts/`.** This repo has no
  `texts/` directory at all; the TGUSA26 copy lives at
  `/Users/vvorski/Documents/Outreach/TGUSA26-Invite-1.txt`. Accept an absolute path and use it.
- **Personalise via a `{first_name}` placeholder in the file**, not by editing copy inline.
  Derive the first name from the METIS name with trailing credentials and emoji stripped
  (`Kim ‘Oceana’ Nadel, ASID, LEED AP` → `Kim`). Preserve the person's own styling — a name
  written lowercase (`mileece i'anson`) stays lowercase in the greeting.
- **Two messaging UIs exist and LinkedIn switches between them mid-run.** The `#interop-outlet`
  overlay worked for eleven consecutive sends on 2026-08-10, then every later profile — a fresh
  tab included — routed to the full `/messaging/thread/new/` page, where the composer sits in
  the `/preload/` iframe instead. Detect which UI you're on before each send; the detector and
  both send paths are in `.claude/commands/message-person.md`. Select that iframe by `src`,
  never by index — it moves between `iframes[1]` and `iframes[0]` as ad frames come and go.
- **A send can look failed and be fine.** After a successful send the "New message" header and
  recipient chip may persist and the URL may stay on `.../new/`. Verify from the thread
  contents or a screenshot showing the delivered check — never from the header state alone.
- **Expect people who were already invited under older copy.** Two of the first fifteen had a
  July variant of the same invitation, sharing the campaign URL but none of the current
  wording. Match on the URL and a landmark phrase, not the current file's opening sentence.
- **A journey-step advance always needs a non-empty note.** `POST /memberships/{id}/update`
  400s without one — record what actually happened (sent / already-sent / skipped-reason).
- **The "sent" note must include the actual message text, not just a label.** A note saying
  only "Outreach message sent via LinkedIn." can't be audited later without re-opening the
  LinkedIn thread. Quote the full message (read in the message-copy step) in the note body.
- **There is no note-edit endpoint.** Every call to `POST /memberships/{id}/update` creates a
  *new* note — it never edits an existing one. To correct/enrich a note after the fact without
  moving the step again, call update again with only `note` set (omit `step_slug` and
  `advance_step`); this attaches a supplementary note while leaving the current step unchanged.
