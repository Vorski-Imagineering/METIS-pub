#!/usr/bin/env python3
"""Session-start banner, git sync status and METIS worklist summary.

Run by the SessionStart hook in .claude/settings.json. Prints hook JSON:
`systemMessage` (banner + report) is shown to the user; `additionalContext`
(report only) is given to Claude. `--codex-hook` checks only Git for Codex startup.
`--text` prints the full report as plain text. `--markdown [--show N|all]` prints
the full report with linked worklist tables for either client.

Read-only and bounded: every network call has a short timeout, and any failure
degrades to a one-line note instead of breaking session start. METIS
credentials come from .env (API_LOGIN_SECRET, METIS_EMAIL, METIS_PASSWORD);
without them the METIS section is skipped.
"""
import json
import os
import subprocess
import sys
from collections import Counter
from datetime import date

from metis_api import ROOT, call, missing_credentials, read_credentials, session

MAX_PAGES = 8  # per `when` bucket, 100 items a page
SHOW = 5       # items listed per section

# --- banner -----------------------------------------------------------------
GLYPHS = {
    "T": ["█████", "  █  ", "  █  ", "  █  ", "  █  "],
    "H": ["█   █", "█   █", "█████", "█   █", "█   █"],
    "E": ["█████", "█    ", "████ ", "█    ", "█████"],
    "G": [" ████", "█    ", "█  ██", "█   █", " ████"],
    "A": [" ███ ", "█   █", "█████", "█   █", "█   █"],
    "R": ["████ ", "█   █", "████ ", "█  █ ", "█   █"],
    "I": ["███", " █ ", " █ ", " █ ", "███"],
    "N": ["█   █", "██  █", "█ █ █", "█  ██", "█   █"],
    " ": ["  "] * 5,
}


def banner(text="THE GATHERING"):
    rows = [" ".join(GLYPHS[c][r] for c in text).rstrip() for r in range(5)]
    rule = "─" * max(len(r) for r in rows)
    return "\n".join([rule, *rows, rule])


# --- git --------------------------------------------------------------------
def git(*args, timeout=8):
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), *args], stdin=subprocess.DEVNULL, capture_output=True,
            encoding="utf-8", errors="replace", timeout=timeout,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def git_status():
    """Returns (line for the report, incoming commits or "")."""
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    if not branch:
        return "GitHub     couldn't read git status", ""
    on = "" if branch == "main" else f" [on branch {branch}]"
    if git("fetch", "--quiet", "--no-tags", "--no-write-fetch-head", "origin",
           "+refs/heads/main:refs/remotes/origin/main") is None:
        return f"GitHub     couldn't check origin/main (fetch failed){on}", ""
    counts = git("rev-list", "--left-right", "--count", "HEAD...origin/main")
    if counts is None:
        return f"GitHub     couldn't compare HEAD with origin/main{on}", ""
    ahead, behind = map(int, counts.split())
    if behind:
        incoming = git("log", "HEAD..origin/main", "--oneline")
        return f"GitHub     {behind} new commit(s) on origin/main{on}", incoming or "(Commit details unavailable.)"
    status = git("status", "--porcelain")
    if status is None:
        return f"GitHub     couldn't read the working tree status{on}", ""
    dirty = len(status.splitlines())
    if dirty or ahead:
        bits = ([f"{dirty} uncommitted path(s)"] if dirty else []) + ([f"{ahead} unpushed commit(s)"] if ahead else [])
        return f"GitHub     local changes ({', '.join(bits)}){on}", ""
    return f"GitHub     up to date 👍🏼{on}", ""


# --- METIS ------------------------------------------------------------------
def fetch(token, me, when):
    items = []
    for page in range(MAX_PAGES):
        d = call(f"/responsible?responsible={me}&when={when}&limit=100&offset={page * 100}", token)
        items += d.get("items", [])
        if not d.get("has_more"):
            return items, False
    return items, True


def name(obj, width=32):
    n = (obj or {}).get("name") or "?"
    return n if len(n) <= width else n[: width - 1].rstrip() + "…"


def who(i):
    if i.get("kind") == "person":
        return f"{name(i.get('person'))} @ {name(i.get('holon'))}"
    return f"{name(i.get('from_holon'))} → {name(i.get('to_holon'))}"


def line(i):
    return f"  {i.get('follow_up_after') or '—':<10}  {who(i)} · {i.get('journey_name', '?')} / {i.get('step_title', '?')}"


def load_worklist():
    """Returns (data, None) or (None, error line). Never raises."""
    try:
        credentials = read_credentials()
        if missing_credentials(credentials):
            return None, "METIS      missing credentials in .env (see automation/metis/README.md)"
        with session(credentials) as (token, person):
            me = person.get("id")
            if not isinstance(me, int) or me < 1:
                raise ValueError("METIS login returned no valid person ID")
            overdue, cut = fetch(token, me, "overdue")
            today, _ = fetch(token, me, "today")
            future, _ = fetch(token, me, "future")
    except Exception as ex:  # network, auth, shape — never block the session
        return None, f"METIS      couldn't load your worklist ({type(ex).__name__})"
    # Most recently overdue first: the freshest threads are the most actionable.
    overdue = sorted(overdue, key=lambda i: i.get("follow_up_after") or "", reverse=True)
    return {"person": person, "overdue": overdue, "cut": cut, "today": today, "future": future}, None


def headline(w):
    first = (w["person"].get("name") or "").split(" ")[0]
    plus = "+" if w["cut"] else ""
    return (f"{first + ': ' if first else ''}{len(w['overdue'])}{plus} overdue · "
            f"{len(w['today'])} due today · {len(w['future'])} upcoming")


def by_journey(w):
    counts = Counter(i.get("journey_name", "?") for i in w["overdue"]).most_common(4)
    return (", ".join(f"{j} {n}" for j, n in counts)
            + f"; oldest since {w['overdue'][-1].get('follow_up_after')}")


def metis_summary(w, err):
    """Plain-text lines, for the hook and --text."""
    if err:
        return [err]
    out = [f"METIS      {headline(w)}", ""]
    if w["today"]:
        out += ["Due today"] + [line(i) for i in w["today"][:SHOW]]
        if len(w["today"]) > SHOW:
            out.append(f"  … and {len(w['today']) - SHOW} more")
        out.append("")
    if w["overdue"]:
        out += ["Most recently overdue"] + [line(i) for i in w["overdue"][:SHOW]]
        out += ["  overdue by journey: " + by_journey(w), ""]
    if w["future"]:
        out += ["Coming up"] + [line(i) for i in w["future"][:SHOW]] + [""]
    if not (w["overdue"] or w["today"] or w["future"]):
        out += ["Nothing dated on your worklist. 🌱", ""]
    return out


# --- markdown (metis-start) -------------------------------------------------
WEB = "https://app.the-gathering.earth"


def md_escape(text):
    return str(text).replace("\\", "\\\\").replace("|", "\\|").replace("[", "\\[").replace("]", "\\]").replace("\n", " ")


def md_link(obj, kind):
    """kind is 'person' or 'holon', matching the web app's /person/<id>/ and /holon/<id>/ routes."""
    obj = obj or {}
    label = md_escape(name(obj, width=40))
    return f"[{label}]({WEB}/{kind}/{obj['id']}/)" if obj.get("id") else label


def relative(day):
    if not day:
        return ""
    try:
        delta = (date.fromisoformat(day) - date.today()).days
    except ValueError:
        return ""
    n = abs(delta)
    if n == 0:
        return "today"
    if n == 1:
        span = "1 day"
    elif n < 14:
        span = f"{n} days"
    elif n < 60:
        span = f"{n // 7} weeks"
    elif n < 365:
        span = f"{n // 30} months"
    else:
        span = f"{n // 365} year{'s' if n >= 730 else ''}"
    return f"in {span}" if delta > 0 else f"{span} ago"


def md_table(items, show):
    rows = ["| Due | When | Who | Where | Journey · Step |", "|---|---|---|---|---|"]
    for i in items[:show]:
        if i.get("kind") == "person":
            a, b = md_link(i.get("person"), "person"), md_link(i.get("holon"), "holon")
        else:
            a, b = md_link(i.get("from_holon"), "holon"), "→ " + md_link(i.get("to_holon"), "holon")
        step = md_escape(f"{i.get('journey_name') or '?'} · {i.get('step_title') or '?'}")
        rows.append(f"| {i.get('follow_up_after') or '—'} | {relative(i.get('follow_up_after'))} | {a} | {b} | {step} |")
    if len(items) > show:
        rows.append(f"\n_… and {len(items) - show} more. Run the report with `--show all` to expand this section._")
    return rows


def markdown(git_line, incoming, w, err, show):
    out = ["```text", banner(), "```", "", f"**{date.today():%a %Y-%m-%d}**", "",
           f"**GitHub** · {git_line.removeprefix('GitHub').strip()}", ""]
    if incoming:
        out += ["Updates available on origin/main:", "```text", incoming, "```", ""]
    if err:
        return "\n".join(out + [f"**METIS** · {err.removeprefix('METIS').strip()}"])
    out += [f"**METIS** · {headline(w)}", ""]
    for title, items in (("Due today", w["today"]), ("Most recently overdue", w["overdue"]), ("Coming up", w["future"])):
        if items:
            out += [f"### {title}", "", *md_table(items, show), ""]
            if title == "Most recently overdue":
                out += [f"Overdue by journey: {by_journey(w)}", ""]
    if not (w["overdue"] or w["today"] or w["future"]):
        out.append("Nothing dated on your worklist. 🌱")
    return "\n".join(out).rstrip()


def parse_show(argv):
    """`--show N` or `--show all`; defaults to SHOW."""
    if "--show" in argv:
        i = argv.index("--show")
        val = argv[i + 1] if i + 1 < len(argv) else ""
        if val == "all":
            return 10 ** 6
        if val.isdigit() and int(val) > 0:
            return int(val)
    return SHOW


def main():
    git_line, incoming = git_status()
    pull_rule = "Tell the user and ask whether to pull before doing other work. Wait for their answer."
    if "--codex-hook" in sys.argv:
        context = "METIS-pub startup check:\n" + git_line
        if incoming:
            context += "\n" + pull_rule
        output = {"hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }}
        if incoming:
            output["systemMessage"] = "Updates available on origin/main."
        print(json.dumps(output, ensure_ascii=False))
        return

    w, err = load_worklist()
    if "--markdown" in sys.argv:
        print(markdown(git_line, incoming, w, err, parse_show(sys.argv)))
        return
    lines = [f"{date.today():%a %Y-%m-%d}", "", git_line, *metis_summary(w, err)]
    report = "\n".join(lines).rstrip()
    context = "Session-start status (scripts/session-start.py):\n" + report
    if incoming:
        context += "\n\nUpdates available on origin/main:\n" + incoming + "\n" + pull_rule
    if "--text" in sys.argv:
        print(banner() + "\n\n" + report)
        if incoming:
            print("\nUpdates available on origin/main:\n" + incoming)
        return
    print(json.dumps({
        "systemMessage": banner() + "\n\n" + report,
        "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context},
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
