# Claude Code Instructions

## Session startup

At the start of every new session, run `git fetch origin main 2>&1 && git log HEAD..origin/main --oneline` to check whether the remote has new commits. (`git fetch` is non-destructive — it only updates the remote-tracking ref, never your working tree or branches.) If `git log` lists any commits, tell the user: "This repo has updates available — want me to pull them?" and wait for their answer before doing anything else.

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
