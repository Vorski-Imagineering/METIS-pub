# METIS-pub repository instructions

## Git and session startup

In this repo, work **directly on `main`** — always. Never create, switch to, or leave work on a
branch (including from skills such as `ui-proposal`), and don't open PRs. Before `git pull`,
commit or push, confirm you're on `main` (`git branch --show-current`); if you're not, switch
back with `git checkout main` and tell the user. Commit straight to `main` and push to
`origin/main`.

If the startup check reports incoming commits on `origin/main`, tell the user and ask
whether to pull before doing other work. Wait for their answer.

In Codex, open the existing checkout in Local mode. The trusted `.codex/hooks.json`
startup hook checks Git only. Use `$metis-start` for the linked worklist report and
`$metis` for METIS API tasks.

## Working in this repository

Shared automation lives in `automation/` and `scripts/`. Keep client entry points in
`.agents/skills/` for Codex and `.claude/` for Claude Code. The public docs in
`docs-pub/` are synced from METIS. See `CONTRIBUTING.md` for local verification.

Keep credentials and session tokens out of chat and tool output. Read METIS credentials
inside a local client process. See `automation/metis/README.md` for setup.

After using a skill, capture any demonstrated issue or missing instruction in the
affected skill or its relevant reference. Use the skill-authoring workflow available in
the current client and tell the user what improved.

## Before saying METIS can't do something, read the whole answer

Statements like "the API can't do X", "field Y is missing" or "that filter is broken" have
sent build work after things that already existed. Before you make one, check these three
things, and say which you checked:

1. **The full live schema entry** for the endpoint, from
   `https://app.the-gathering.earth/api/v1/openapi.json`: its `description`, **every
   parameter's `description`**, and the response schema, including nested objects. The repo's
   `docs-pub/api/` copy can lag the live schema.
2. **All the keys of a real response**, not just the ones you went looking for. Print
   `list(item.keys())`, and print nested values (e.g. `config_flags` entries) before parsing them.
3. **A changed result means a supported parameter.** METIS ignores unknown query parameters
   without an error. If adding `?journey=` or `&offset=` returns the same rows, the parameter
   isn't supported. It doesn't mean the data is wrong.

If you still aren't sure after that, say "I couldn't find X" and name what you checked. Don't
say "X doesn't exist". If you're relaying another agent's claim that something exists or is
live, check it against production the same way.

## Fathom transcripts and summaries

When reading a Fathom call page and adding its content as a note or message, always copy the full text verbatim — do not condense, trim, or summarize. Only produce a shorter version if the user explicitly asks for a summary. Always include the Fathom share link at the top of the note.

## Browser automation

LinkedIn and Google Docs browser workflows require the live Claude in Chrome connector
(`mcp__claude-in-chrome__*`). See `CLAUDE.md` for the connector details. If it is
unavailable, report that limit. Never fetch or scrape these pages through web search or
an HTTP client.

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

### This applies to you too, right now — not just to the commands you write

Pacing documented inside a command file only protects the user who runs that command later.
It does nothing during your own live exploration, testing, or debugging — and that gap is
exactly what got a LinkedIn account throttled during development of these skills. Root cause:
dozens of rapid page loads, repeated revisits to the same profiles within an hour, and a
scroll-hydration loop firing ~20 background requests in under 20 seconds, all done at
dev-testing speed with no delay between actions. LinkedIn's detection responds to burst
pattern and revisit frequency, not just a daily total — so "I only touched a handful of
profiles" is not a defense if it happened in a tight burst.

**So: apply `humanDelay()` to yourself, live, whenever you touch LinkedIn** — not only when
writing a loop into a command file for someone else to run later. This means, concretely:
- Testing a selector or extraction script against a real profile is one visit; testing it
  three more times to iterate is three more visits, each of which should still be paced.
  Batch your checks into one script per visit instead of revisiting to check one thing at a
  time.
- Don't revisit the same profile repeatedly within a short window "just to check" — if you
  need to confirm something changed, that revisit still counts and still needs the delay.
- A scroll-hydration loop is not one request — treat each round of scrolling as a burst of
  requests, so don't chain several profiles' hydration loops back to back without a gap
  between profiles, even mid-debugging.
- If you notice yourself moving fast because you're mid-investigation and want the next data
  point immediately, that urgency is exactly the moment to slow down instead — it is the
  same pressure a real bulk-automation user would feel, and the account doesn't know the
  difference between "testing" traffic and "production" traffic.

## `uploads/` folder — do not touch

`uploads/` holds screenshots referenced by an external automated issue-creation flow, not by
anything in this repo. Files in there will look orphaned (no repo file links to them, no commit
history context) — that's expected. Never delete, move, rename, or "clean up" anything under
`uploads/`, even if a repo audit or reorg would otherwise flag it as dead weight.
