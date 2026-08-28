---
name: auto-message-gogogo
description: >
  Use when the user wants a large holon-outreach backlog worked down automatically over
  several days from this same session — e.g. "run this for a week", "auto-message the rest
  of the backlog", "let it sleep between batches and keep going". Runs one paced daily batch
  of holon-outreach, sleeps ~22h in this session, and repeats for N days.
---

# Auto Message Gogogo

A multi-day wrapper around `holon-outreach` for working down a large backlog without the user
re-invoking the command every day. It does **not** run unsupervised in the background-cron
sense — see the hard constraint below.

## Routing

Run the `/auto-message-gogogo` command — read `.claude/commands/auto-message-gogogo.md` before
starting. It composes:

- **REQUIRED SUB-SKILL:** `holon-outreach` — this *is* the per-day batch; read it first, this
  skill only changes the failure-handling and adds the multi-day loop around it.
- **REQUIRED SUB-SKILL:** `linkedin-automation` — pacing and throttle detection, unchanged.

## Hard constraint: this cannot run headless

Every check in `holon-outreach` (degree, thread-duplicate detection, image upload, send
verification) runs through the Claude-in-Chrome browser connector, which requires **this live
interactive session** with the user's browser open. A scheduled/cron job running in the
background (`CronCreate`) does **not** have that connector — it would fail on the first
profile visit. Do not build this as a cron job. The only way to "run it for a week" is to keep
*this* session alive and self-reschedule with a long `Bash` background `sleep`, exactly as
described in the command file. If the user's machine sleeps, the terminal closes, or the
session otherwise ends, the loop stops — that's an inherent limitation, not a bug to route
around.

## Non-obvious rules baked into the command

- **Never hard-stop the whole week's run over one ambiguous person.** `holon-outreach`'s
  "Debug mode is ON — stop immediately on any unexpected result" is right for a single
  human-watched batch, but wrong here: a week-long run must survive one confusing profile.
  Ambiguous cases (thread-duplicate match unclear, degree marker unclear, LinkedIn UI acting
  up) get **skipped with a note explaining the uncertainty** and the run continues — never
  guess and send, never grind the whole run to a halt. Only a genuine throttle signal (per
  `linkedin-automation`'s detection table) stops the run early.
- **Daily cap defaults to 30**, matching `holon-outreach`'s single-run ceiling. The user has
  explicitly chosen this over a more conservative daily cap, accepting the added risk that
  sustained day-over-day volume is itself a recognizable automation signature (this account has
  been throttled once before from sustained activity — see project memory). Let the user
  override it lower or higher via `daily_cap` if they change their mind.
- **Re-authenticate and re-fetch the candidate list every day, never reuse cached data.** The
  METIS token is valid 24h — a 22h sleep leaves little margin, so always re-login at the start
  of each day's batch. Also re-fetch `to_contact` fresh each day: other team members' activity,
  prior days' advances, or manual work by the user can all change who's actually still waiting.
- **The user can interrupt between days.** The loop only "sleeps" via a backgrounded `Bash`
  `sleep`; it is not blocking in a way that prevents the user from sending a new message. Before
  starting each new day's batch, check whether the user's most recent message asked to stop,
  pause, or change scope — don't blindly continue into day 4 if they said something in day 2.
- **End-of-day summary, not silence.** After each day's batch, post the same
  messaged/already-invited/skipped-ambiguous/skipped-dead-link breakdown `holon-outreach` uses,
  plus how many days/candidates remain. A week of silence with no visible progress is as bad as
  a week of no progress.
- **Vary the start time day to day, not just the sleep duration.** A fixed 22h interval means
  every day's batch starts within the same narrow clock window — itself a machine-like pattern.
  The ±1h jitter on the sleep (see the command's step 5) exists specifically to walk the start
  time around rather than pin it.
