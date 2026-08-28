---
description: Run holon-outreach as a daily-paced batch for several days from this session, sleeping ~22h between days
allowed-tools: Read, Bash, mcp__claude-in-chrome__tabs_context_mcp, mcp__claude-in-chrome__tabs_create_mcp, mcp__claude-in-chrome__navigate, mcp__claude-in-chrome__javascript_tool, mcp__claude-in-chrome__computer, mcp__claude-in-chrome__read_page, mcp__claude-in-chrome__file_upload
---

Work down a large `holon-outreach` backlog over several days without the user re-invoking the
command each day. Read `.claude/skills/auto-message-gogogo/SKILL.md` first — in particular the
**hard constraint** section: this only works because this interactive session (and its
Claude-in-Chrome connection) stays open and self-reschedules. It is not a cron job.

`$ARGUMENTS`: `<holon name or slug> <journey slug> <step slug> <message file> [--image path] [daily_cap N] [days N]`
Defaults: `daily_cap` = 30, `days` = 7.
Example: `camp-audax-usa-2026 person-outreach to_contact media/CampAudax2026-Invite-1.txt --image media/camp-audax-invite.jpg daily_cap 30 days 7`

## Before starting

State the plan to the user and get confirmation before the first send: holon, message file,
image (if any), daily cap, number of days, and that this requires the session to stay open the
whole time. This is a multi-day, many-message commitment — don't start it on an ambiguous ask.

## Daily loop

Repeat the following for up to `days` iterations, or until the candidate pool for this
holon/journey/step is exhausted, or a hard-stop condition fires:

### 1. Check for interruption

Before anything else, check whether the user has sent any message since the last day's batch
that asks to stop, pause, change the holon/message/cap, or otherwise redirect. If so, stop the
loop and follow the new instruction instead of silently continuing.

### 2. Re-authenticate and re-fetch, always

Run the METIS auth flow fresh (`.claude/commands/metis.md`) — do not reuse a token from a
previous day. Re-fetch the `to_contact` candidate list fresh via
`.claude/commands/holon-outreach.md` step 2 — do not reuse a cached list. Take up to
`daily_cap` candidates from the current caller-owned worklist.

If the fetch returns zero candidates, the backlog is done — report totals across all days and
stop the loop (don't sleep and retry).

### 3. Run one batch, with graceful degradation

Follow `holon-outreach` steps 3–6 (read message, look up contact info, tell the user the plan,
per-candidate send) with one change to step 6's failure handling:

- **Clear cases proceed exactly as `holon-outreach` describes** — 1st-degree confirmed, no
  prior invite found, image + text send verified, membership advanced with a note quoting the
  message.
- **Ambiguous cases are skipped, not stopped on.** If degree can't be read cleanly, if the
  thread-duplicate check can't isolate the right pane, if the messaging UI is in an unexpected
  state, or any other check comes back unclear rather than a clean yes/no — do not guess, do
  not send, and do not halt the run. Advance nothing (leave their step alone) and record them
  in the day's summary as "skipped — needs manual review: `<reason>`" so a human can look at
  them later. Move on to the next candidate.
- **Genuine throttle signals still stop the run.** Per `linkedin-automation`'s detection table
  (collapsed profile structure, missing connection counts on two profiles in a row, etc.) —
  stop the entire multi-day loop immediately, not just today's batch, and report where it
  stopped. Do not schedule the next day's sleep.

Apply `linkedin-automation` pacing and burst-breaks within the batch exactly as
`holon-outreach` does — the daily cap does not relax per-send pacing.

### 4. End-of-day summary

Post the same breakdown `holon-outreach` uses (messaged / already-invited / skipped-dead-link /
skipped-ambiguous), plus: which day this was out of `days`, and an estimate of candidates
remaining in the backlog.

### 5. Sleep until the next day

If this was the last day, or the candidate pool is now empty, stop — do not sleep. Otherwise:

```python
import random
base = 22 * 3600  # 22 hours
jitter = random.randint(-3600, 3600)  # +/- 1h so the daily start time actually moves around
print(base + jitter)
```

Then `Bash({command: "sleep <seconds>", run_in_background: true})`. When the notification
arrives, that is the signal to start the next day's iteration at step 1 — do not poll or check
in early.

## Final summary

When the loop ends (days exhausted, backlog empty, throttle stop, or user interruption), report
totals across the whole run: days completed, messaged, already-invited, skipped-dead-link,
skipped-ambiguous (with enough detail the user can follow up), and candidates still remaining
in the backlog if any.
