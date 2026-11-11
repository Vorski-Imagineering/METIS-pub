---
description: Show The Gathering start-up banner, git sync status and your METIS worklist summary
allowed-tools: Bash(python3:*), Bash(py:*), Bash(PYTHONIOENCODING=utf-8 py:*), Bash(git rev-parse:*), Bash(git pull:*)
---

# METIS start-up

This is the same report the `SessionStart` hook produces, on demand. Use it in apps that don't
display hook messages (e.g. the desktop app) or any time mid-session.

Run:

```bash
python3 "$(git rev-parse --show-toplevel)/scripts/session-start.py" --text
```

**Windows fallback:** `python3` there is often just a Microsoft Store shortcut that exits with
code 49 ("Python was not found"). If that happens, use the `py` launcher instead, and force UTF-8
output — otherwise the banner's box-drawing characters crash with a cp1252 `UnicodeEncodeError`:

```bash
cd "$(git rev-parse --show-toplevel)" && PYTHONIOENCODING=utf-8 py scripts/session-start.py --text
```

Don't use `$CLAUDE_PROJECT_DIR` here: it is set for hooks, not in Claude's Bash tool, so the
path collapses to `/scripts/session-start.py` and fails.

Show the output to the user **verbatim** inside a code block (the banner is ASCII art and needs
monospace). Don't summarise or re-format it.

If the output contains "Updates available on origin/main", tell the user updates are available
and ask whether to pull them with `git pull` before doing other work — wait for their answer.
