# Claude Code instructions

@AGENTS.md

## Session startup

A `SessionStart` hook (in `.claude/settings.json`) runs `scripts/session-start.py`. It shows the
user a "THE GATHERING" banner, the git sync status, and a summary of their METIS worklist
(`GET /responsible` filtered to them: overdue, due today, upcoming), and puts the same report into
your context. If `origin/main` has new commits, the context also says so. When you see that notice,
tell the user updates are available and ask whether to pull them before doing other work — wait for
their answer.

Some apps (e.g. the desktop app) run the hook but don't display its `systemMessage`, so the user
never sees the banner. `/metis-start` prints the same report on demand
(`scripts/session-start.py --markdown`, as linked tables; `/metis-start 10` or `all` for more rows).

## Skill learning process

After executing any skill, evaluate whether it worked well. If a skill produced errors, required workarounds, gave incomplete results, or needed clarification mid-execution, **always update it before ending the conversation**:

1. Identify what went wrong or could be clearer (missing context, wrong assumptions, broken steps, edge cases not handled)
2. Invoke the `superpowers:writing-skills` skill to update the affected skill with the fix
3. Briefly tell the user what was improved

This applies to all skills — built-in superpowers skills, project skills (like `metis`, `message-person`), and any others. The goal is that each execution makes the next one smoother.

## Browser automation

Always use the Chrome connector (`mcp__claude-in-chrome__*` tools) when working with:
- `linkedin.com` — any LinkedIn page (search, connections, messaging, profiles, invitations)
- `docs.google.com` — any Google Docs/Sheets/Drive page

Never attempt to fetch or scrape these pages with `WebFetch` or `WebSearch`. Always navigate to them in the live browser via `mcp__claude-in-chrome__navigate` and interact using `mcp__claude-in-chrome__javascript_tool`, `mcp__claude-in-chrome__read_page`, etc.

### Getting more than 1000 characters out of a page

`javascript_tool` silently truncates its **return value at exactly 1000 characters** — 1000
arrives intact, 1001 loses its last character to `[TRUNCATED]`, and no error is raised. The
cap is per call (each `browser_batch` item gets its own budget) and specific to that tool —
`Bash` and `Read` are unaffected.

**All of the above is measured, not documented.** A search of the official Claude Code and
Claude in Chrome docs found no mention of a `javascript_tool` output limit, and no setting to
raise it. The documented MCP result cap is a different, far larger layer —
`MAX_MCP_OUTPUT_TOKENS`, default 25,000 *tokens* (~100k chars) — so it is not what's biting
here; the 1000-char cut happens well inside that budget, in the Chrome MCP server itself.
Being undocumented, it may change without notice: if bulk extraction starts behaving oddly,
re-measure the boundary before trusting these numbers.

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
