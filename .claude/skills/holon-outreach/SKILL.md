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
- **Message copy comes from a file, never invented inline.** Read it from `texts/` (e.g.
  `texts/TGUSA26-Invite-1.txt`) so the wording stays exactly what the user prepared.
- **A journey-step advance always needs a non-empty note.** `POST /memberships/{id}/update`
  400s without one — record what actually happened (sent / already-sent / skipped-reason).
- **The "sent" note must include the actual message text, not just a label.** A note saying
  only "Outreach message sent via LinkedIn." can't be audited later without re-opening the
  LinkedIn thread. Quote the full message (read in the message-copy step) in the note body.
- **There is no note-edit endpoint.** Every call to `POST /memberships/{id}/update` creates a
  *new* note — it never edits an existing one. To correct/enrich a note after the fact without
  moving the step again, call update again with only `note` set (omit `step_slug` and
  `advance_step`); this attaches a supplementary note while leaving the current step unchanged.
