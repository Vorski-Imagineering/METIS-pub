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
  **Read this check from `#interop-outlet`'s shadowRoot, never from the compose `<iframe>`** —
  see linkedin-automation's General notes for why the iframe gives false positives. Confirmed
  live: this cost a person (marked already-invited, then had to be reverted and actually
  messaged) when the check read stale iframe content instead.
- **Message copy comes from a file, never invented inline.** Read it from `texts/` (e.g.
  `texts/TGUSA26-Invite-1.txt`) so the wording stays exactly what the user prepared.
- **A journey-step advance always needs a non-empty note.** `POST /memberships/{id}/update`
  400s without one — record what actually happened (sent / already-sent / skipped-reason).
  **When a message was actually sent, the note must include its full verbatim text**, not just
  "message sent" — the note is the record of exactly what the person received. See the
  command's step 6e for the exact format.
