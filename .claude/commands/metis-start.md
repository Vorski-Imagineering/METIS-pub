---
description: Show The Gathering start-up banner, git sync status and your METIS worklist summary
allowed-tools: Bash(python3:*), Bash(git pull:*)
---

# METIS start-up

This is the same report the `SessionStart` hook produces, on demand. Use it in apps that don't
display hook messages (e.g. the desktop app) or any time mid-session.

Run:

```bash
python3 "$CLAUDE_PROJECT_DIR/scripts/session-start.py" --text
```

Show the output to the user **verbatim** inside a code block (the banner is ASCII art and needs
monospace). Don't summarise or re-format it.

If the output contains "Updates available on origin/main", tell the user updates are available
and ask whether to pull them with `git pull` before doing other work — wait for their answer.
