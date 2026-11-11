---
description: Show The Gathering start-up banner, git sync status and your METIS worklist summary
argument-hint: "[N|all]  rows per section (default 5)"
allowed-tools: Bash(python3:*), Bash(py:*), Bash(PYTHONIOENCODING=utf-8 py:*), Bash(git rev-parse:*), Bash(git pull:*)
---

# METIS start-up

This is the same report the `SessionStart` hook produces, on demand, but formatted as Markdown
tables with links into METIS. Use it in apps that don't display hook messages (e.g. the desktop
app) or any time mid-session.

Arguments: `$ARGUMENTS`

- Empty → 5 rows per section (the default; omit `--show`).
- A positive number or `all` → pass it as `--show <value>`, e.g. `/metis-start 10`, `/metis-start all`.
- Anything else → ignore it and use the default, and tell the user the accepted values.

Run (add `--show <value>` when an argument was given):

```bash
python3 "$(git rev-parse --show-toplevel)/scripts/session-start.py" --markdown
```

**Windows fallback:** `python3` there is often just a Microsoft Store shortcut that exits with
code 49 ("Python was not found"). If that happens, use the `py` launcher instead, and force UTF-8
output — otherwise the banner's box-drawing characters crash with a cp1252 `UnicodeEncodeError`:

```bash
cd "$(git rev-parse --show-toplevel)" && PYTHONIOENCODING=utf-8 py scripts/session-start.py --markdown
```

Don't use `$CLAUDE_PROJECT_DIR` here: it is set for hooks, not in Claude's Bash tool, so the
path collapses to `/scripts/session-start.py` and fails.

The output is already Markdown: the banner sits in its own ```` ```text ```` block and the
worklist is tables with links. Reproduce it **exactly as printed, as Markdown** — do **not** wrap
the whole thing in another code block (that would show the tables as raw `|` text and kill the
links), and don't summarise, reorder or drop rows.

If the output contains "Updates available on origin/main", tell the user updates are available
and ask whether to pull them with `git pull` before doing other work — wait for their answer.

`--text` still prints the plain-text version (the same as the hook's banner), if that's ever
wanted instead.
