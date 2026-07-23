# Claude Code Instructions

## Session startup

A `SessionStart` hook (in `.claude/settings.json`) automatically checks whether `origin/main` has
new commits and, if so, injects that into context. When you see that notice, tell the user updates
are available and ask whether to pull them before doing other work — wait for their answer.

## Skill learning process

After executing any skill, evaluate whether it worked well. If a skill produced errors, required workarounds, gave incomplete results, or needed clarification mid-execution, **always update it before ending the conversation**:

1. Identify what went wrong or could be clearer (missing context, wrong assumptions, broken steps, edge cases not handled)
2. Invoke the `superpowers:writing-skills` skill to update the affected skill with the fix
3. Briefly tell the user what was improved

This applies to all skills — built-in superpowers skills, project skills (like `metis`, `message-person`), and any others. The goal is that each execution makes the next one smoother.

## Fathom transcripts and summaries

When reading a Fathom call page and adding its content as a note or message, always copy the full text verbatim — do not condense, trim, or summarize. Only produce a shorter version if the user explicitly asks for a summary. Always include the Fathom share link at the top of the note.

## Browser automation

Always use the Chrome connector (`mcp__claude-in-chrome__*` tools) when working with:
- `linkedin.com` — any LinkedIn page (search, connections, messaging, profiles, invitations)
- `docs.google.com` — any Google Docs/Sheets/Drive page

Never attempt to fetch or scrape these pages with `WebFetch` or `WebSearch`. Always navigate to them in the live browser via `mcp__claude-in-chrome__navigate` and interact using `mcp__claude-in-chrome__javascript_tool`, `mcp__claude-in-chrome__read_page`, etc.

## Be a respectful automation client

These tools drive a real, logged-in account against someone else's service. Act like a
considerate human using the site, not a scraper racing a rate limiter.

**Never loop over people, pages, or profiles without a randomised delay between iterations.**
Use an exponential (Poisson) delay rather than a fixed or uniform sleep — real human gaps are
mostly short with occasional long ones, and a constant interval is itself a machine
fingerprint. The canonical `humanDelay()` implementation, the per-action means and the burst
breaks live in the **Pacing** section of
`.claude/skills/linkedin-automation/SKILL.md`. Read it before writing any loop that touches
LinkedIn, and reuse it rather than inventing a new delay scheme.

Two things this protects against, in order of importance:

1. **Silent data corruption.** LinkedIn's throttled response is not an error — it returns
   HTTP 200 with the right name and headline and silently drops About, follower counts and
   company. A fast run looks like it succeeded while writing empty fields for most people.
   Always verify a positive signal (e.g. the follower count) is present before recording a
   field as genuinely absent.
2. **The account.** Sustained fast automation gets accounts restricted, and write actions
   (connection requests, messages) far more than reads.

Also remember that reads are not invisible: **visiting a profile notifies that person.**
Before a bulk enrichment run, say how many profiles will be visited and that each visit is
visible to them. Prefer small batches, write results incrementally so a run is resumable,
and stop and report on the first sign of throttling rather than pushing through.

## `uploads/` folder — do not touch

`uploads/` holds screenshots referenced by an external automated issue-creation flow, not by
anything in this repo. Files in there will look orphaned (no repo file links to them, no commit
history context) — that's expected. Never delete, move, rename, or "clean up" anything under
`uploads/`, even if a repo audit or reorg would otherwise flag it as dead weight.
