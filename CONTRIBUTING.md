# Contributing

This repo is a collection of Claude Code automation tools. The goal is that a non-programmer
can use them by typing a slash command, and that the team can add new tools collaboratively
without the structure turning into a junk drawer.

## Repo layout

The guiding rule: **`.claude/` holds only what Claude Code loads. The repo root holds what humans read.**

```
.claude/
  commands/      Slash commands — the executable workflows (/accept-one, /metis, ...)
  skills/        Auto-loaded routers — let Claude pick the right command from plain English
  settings.json  Permissions + hooks

automation/                       All module code, scripts, and setup examples live here
  linkedin-automation/            LinkedIn module: README, scripts/, setup/ examples
  metis/                          METIS module: README (usage guide)
  google-sheets/                  Google Sheets module: README, CLI script, requirements

docs-pub/               Direct mirror of docs/pub/ from the METIS repo — synced by an external
                        publish flow, not edited here. Its own README.md is the canonical index
                        (whatever top-level folders exist there — currently api/, core/,
                        extension/, metis_apps/, web/ — reflect METIS's own taxonomy and can
                        change without notice on either side)
uploads/                Screenshots used by an external issue-creation flow — do not touch

README.md        Front door for users
CLAUDE.md        Instructions Claude reads at session start
CONTRIBUTING.md  This file
mkdocs.yml       Docs site config — published to docs.the-gathering.earth on every push to main
```

Everything under `docs-pub/`, the module `README.md` files (in `automation/*/`), `README.md`, and
`CONTRIBUTING.md` gets published to the docs site automatically. `docs-pub/` is copied wholesale
and the site only links to `docs-pub/README.md` in `mkdocs.yml` — that file is METIS's own
maintained index and links to everything else in the tree, so new files never need a workflow
or nav change. If you link to a specific `docs-pub/` file from a command or skill (e.g. the
coherence playbook), double check the path still exists after a sync — METIS can rename or
reorganize files under `docs-pub/` without warning.

Never put human-facing docs, scripts, or assets under `.claude/` — they belong under `automation/`.
`.claude/` is configuration only: it's what Claude Code auto-loads, not what a person reads or
runs by hand. Scripts like `sheets_cli.py` need to stay readable and runnable independent of
Claude Code (a person `pip install`s and invokes them directly per the module README), so they
live in `automation/`, not bundled into a skill folder.

## Commands vs. skills

- **Command** (`.claude/commands/<name>.md`): runs when the user types `/<name>`. This is where
  the actual step-by-step workflow lives.
- **Skill** (`.claude/skills/<name>/SKILL.md`): loaded automatically every session. Claude reads
  its `description` and invokes it when the user describes the task in plain language, then routes
  to the right command. Skills are how casual users avoid memorizing command names.

A module typically has **one skill** (the router) and **one or more commands** (the workflows).

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

- Open the repo in Claude Code and run the command end-to-end.
- For skills, confirm a plain-language phrase (not the slash name) triggers the right command.
- Commit on a branch and open a PR. Note any secrets or `.env` keys a reviewer needs to test.
