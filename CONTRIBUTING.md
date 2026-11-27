# Contributing

This repo contains automation tools for Codex and Claude Code. People can start a workflow with a
skill, a slash command, or a plain-language request.

## Repo layout

Keep client configuration in its client directory and put shared scripts in `automation/` or `scripts/`.

```
.claude/
  commands/      Slash commands — the executable workflows (/accept-one, /metis, ...)
  skills/        Auto-loaded routers — let Claude pick the right command from plain English
  settings.json  Permissions + hooks

.agents/skills/  Codex project skills ($metis, $metis-start)
.codex/hooks.json  Codex startup hook configuration
scripts/         Shared startup report and METIS API client

automation/                       All module code, scripts, and setup examples live here
  linkedin-automation/            LinkedIn module: README, scripts/, setup/ examples
  metis/                          METIS module: README (usage guide)
  google-sheets/                  Google Sheets module: README, CLI script, requirements

docs-pub/               Direct mirror of docs/pub/ from the METIS repo — synced by an external
                        publish flow, not edited here. Its own README.md is the canonical index
                        (whatever top-level folders exist there — currently api/, core/,
                        extension/, metis_apps/, web/ — reflect METIS's own taxonomy and can
                        change without notice on either side)
site-overlay/           The docs site's own layer over docs-pub/ — nav (SUMMARY.md), the METIS
                        Docs index page, and the tag map. Lives here because docs-pub/ is
                        overwritten on every sync
uploads/                Screenshots used by an external issue-creation flow — do not touch

README.md            Front door for users
AGENTS.md            Shared repository instructions
CLAUDE.md            Claude Code instructions, including the shared rules
CONTRIBUTING.md      This file
DOCS-CONVENTIONS.md  How the docs site is built and how to write a page for it
mkdocs.yml           Docs site config — published to docs.the-gathering.earth on every push to main
```

Everything under `docs-pub/`, the module `README.md` files (in `automation/*/`), `README.md`, and
`CONTRIBUTING.md` gets published to the docs site automatically. `docs-pub/` is copied wholesale,
but a new page **must** also be added to `site-overlay/SUMMARY.md` — CI fails otherwise, because a
page that publishes with no nav entry is unreachable in practice. See **[DOCS-CONVENTIONS.md](DOCS-CONVENTIONS.md)**
for the build pipeline and the page-writing conventions. If you link to a specific `docs-pub/` file
from a command or skill (e.g. the coherence playbook), double check the path still exists after a
sync — METIS can rename or reorganize files under `docs-pub/` without warning.

Put user-facing setup and usage docs in `automation/`. Keep reusable scripts runnable outside either
client so skills and commands can share them. For example, `sheets_cli.py` lives in its automation module.

## Commands vs. skills

- **Command** (`.claude/commands/<name>.md`): runs when the user types `/<name>`. This is where
  the actual step-by-step workflow lives.
- **Skill** (`.claude/skills/<name>/SKILL.md`): loaded automatically every session. Claude reads
  its `description` and invokes it when the user describes the task in plain language, then routes
  to the right command. Skills are how casual users avoid memorizing command names.

In Claude Code, a module typically has a routing skill and one or more commands. For Codex, add a
folder with `SKILL.md` under `.agents/skills/`. Use its description to explain when it applies and
refer to the existing scripts and references for workflow details.

## Adding a new slash command

1. Create `.claude/commands/<name>.md` with frontmatter:

   ```markdown
   ---
   description: One line shown in the /command menu and to Claude. Be specific.
   allowed-tools: Read, Bash  # least privilege — list only what the command needs
   ---

   What this command does, in one sentence.

   ## Steps

   ### 1. ...
   ### 2. ...
   ```

2. If the command belongs to a module that has a skill, add a row to that skill's routing table
   so plain-language requests reach it.

3. Update the module README and the root README's command list.

### Conventions

- **Least-privilege tools.** Only list the `allowed-tools` the command actually uses.
- **Debug mode is ON.** If a step fails or returns something unexpected, stop and report the exact
  error — do not invent fallbacks or workarounds. (See `accept-one.md` for the pattern.)
- **Browser steps** use the Claude in Chrome connector (`mcp__claude-in-chrome__*`) and prefer
  `aria-label`/`role`/text over CSS classes (LinkedIn obfuscates class names).
- **Keep one source of truth.** Reference shared docs (e.g. `docs-pub/api/PLAYBOOK.md`) instead of
  copying their content into a command.

## Adding a new module

1. Make a folder `automation/<module>/` with a `README.md` (setup + usage).
2. Add the commands under `.claude/commands/`.
3. Add a skill at `.claude/skills/<module>/SKILL.md` that routes intent → commands.
4. Link the module from the root `README.md`.

## Testing a change

- Open the existing `main` checkout in Codex Local or Claude Code. Verify the changed skill or command through its normal entry point.
- For skills, check both explicit invocation and a plain-language request.
- Run `python3 -m unittest discover -s scripts/tests` for the shared METIS client and startup checks.
- Use fixtures for tests of writes or external workflows. For docs, run the assembly, nav, and strict build checks in `.github/workflows/docs.yml`.
- Follow the Git rules in `AGENTS.md`. Commit directly on `main` and push to `origin/main`.
