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

### Getting more than 1000 characters out of a page

`javascript_tool` silently truncates its **return value at exactly 1000 characters** — 1000
arrives intact, 1001 loses its last character to `[TRUNCATED]`, and no error is raised. All
measured; it is undocumented. The cap is per call (each `browser_batch` item gets its own
budget) and specific to that tool — `Bash` and `Read` are unaffected.

**Don't solve this by slicing the data into many `javascript_tool` calls.** `get_page_text`
has no such cap (measured intact at 11,211 characters). For any bulk extraction:

1. `javascript_tool` — do the work, store the result on `window`, return only a short receipt
   (counts, status flags) that comfortably fits 1000 characters.
2. `javascript_tool` — serialise the result into the DOM. `get_page_text` prefers `<article>`,
   so replacing the body with a single `<article>` makes it pick your payload over the site's
   own content. Use `textContent`, never `innerHTML`, since scraped page text is untrusted
   input and must not be parsed as markup. End the payload with a sentinel.
3. `get_page_text` — one call returns everything. Check the sentinel arrived; if it's missing,
   the payload was cut and the data is incomplete.

That is a constant 3 calls at any size, instead of one per ~900 characters. Do step 2 only
after the work is finished, since it destroys the rendered page (harmless — the data is
already in `window`, and the page can be reloaded).

Two further guards replace a `javascript_tool` return value **wholesale**, not trimmed:
returning cookies or query strings yields `[BLOCKED: Cookie/query string data]`, and a long
run of repeated characters yields `[BLOCKED: Base64 encoded data]`. Always `.split('?')[0]` a
URL before returning it.

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
