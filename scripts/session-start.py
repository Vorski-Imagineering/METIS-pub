#!/usr/bin/env python3
"""Session-start banner, git sync status and METIS worklist summary.

Run by the SessionStart hook in .claude/settings.json. Prints hook JSON:
`systemMessage` (banner + report) is shown to the user; `additionalContext`
(report only) is given to Claude. With `--text` it prints the banner, the report
and any incoming commits as plain text instead (used by the /metis-start command).

Read-only and bounded: every network call has a short timeout, and any failure
degrades to a one-line note instead of breaking session start. METIS
credentials come from .env (API_LOGIN_SECRET, METIS_EMAIL, METIS_PASSWORD);
without them the METIS section is skipped.
"""
import json
import subprocess
import sys
import urllib.request
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
METIS = "https://app.the-gathering.earth/api/v1"
# Cloudflare's WAF rejects Python's default User-Agent with a 403 (error 1010).
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
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
        p = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, timeout=timeout)
        return p.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def git_status():
    """Returns (line for the report, incoming commits or "")."""
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    if not branch:
        return "GitHub     couldn't read git status", ""
    git("fetch", "-q", "origin")
    on = "" if branch == "main" else f" [on branch {branch}]"
    incoming = git("log", "HEAD..origin/main", "--oneline")
    dirty = git("status", "--porcelain").splitlines()
    # Unpushed = ahead of this branch's own upstream; a branch never pushed counts every commit off main.
    upstream = "@{u}" if git("rev-parse", "--abbrev-ref", "@{u}") else "origin/main"
    ahead = git("log", f"{upstream}..HEAD", "--oneline").splitlines()
    if incoming:
        n = len(incoming.splitlines())
        return f"GitHub     {n} new commit(s) on origin/main — pull before working{on}", incoming
    if dirty or ahead:
        bits = ([f"{len(dirty)} uncommitted path(s)"] if dirty else []) + ([f"{len(ahead)} unpushed commit(s)"] if ahead else [])
        return f"GitHub     local changes ({', '.join(bits)}) — commit & push to save them{on}", ""
    return f"GitHub     up to date 👍🏼{on}", ""


# --- METIS ------------------------------------------------------------------
def env():
    vals = {}
    try:
        for line in (ROOT / ".env").read_text().splitlines():
            k, sep, v = line.partition("=")
            if sep:
                vals[k.strip()] = v.strip()
    except OSError:
        pass
    return vals


def call(path, token=None, body=None, key=None):
    headers = {"User-Agent": UA, "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if key:
        headers["X-Metis-Api-Key"] = key
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(METIS + path, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=6) as r:
        # List responses can hold invalid UTF-8 and raw control characters.
        return json.loads(r.read().decode("utf-8", "replace"), strict=False)


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


def metis_summary():
    e = env()
    key, email, pw = e.get("API_LOGIN_SECRET"), e.get("METIS_EMAIL"), e.get("METIS_PASSWORD")
    if not (key and email and pw):
        return ["METIS      no credentials in .env — run /metis-setup"]
    try:
        login = call("/auth/login", body={"email": email, "password": pw}, key=key)
        token, person = login["token"], login.get("person") or {}
        me = person.get("id")
        overdue, cut = fetch(token, me, "overdue")
        today, _ = fetch(token, me, "today")
        future, _ = fetch(token, me, "future")
        try:
            call("/auth/logout", token, body={})
        except Exception:
            pass
    except Exception as ex:  # network, auth, shape — never block the session
        return [f"METIS      couldn't load your worklist ({type(ex).__name__})"]

    first = (person.get("name") or "").split(" ")[0]
    plus = "+" if cut else ""
    out = [f"METIS      {first + ': ' if first else ''}{len(overdue)}{plus} overdue · {len(today)} due today · {len(future)} upcoming",
           ""]
    if today:
        out += ["Due today"] + [line(i) for i in today[:SHOW]]
        if len(today) > SHOW:
            out.append(f"  … and {len(today) - SHOW} more")
        out.append("")
    if overdue:
        # Most recently overdue first: the freshest threads are the most actionable.
        recent = sorted(overdue, key=lambda i: i.get("follow_up_after") or "", reverse=True)
        out += ["Most recently overdue"] + [line(i) for i in recent[:SHOW]]
        by_journey = Counter(i.get("journey_name", "?") for i in overdue).most_common(4)
        out.append("  overdue by journey: " + ", ".join(f"{j} {n}" for j, n in by_journey)
                   + f"; oldest since {recent[-1].get('follow_up_after')}")
        out.append("")
    if future:
        out += ["Coming up"] + [line(i) for i in future[:SHOW]]
        out.append("")
    if not (overdue or today or future):
        out += ["Nothing dated on your worklist. 🌱", ""]
    return out


def main():
    git_line, incoming = git_status()
    lines = [f"{date.today():%a %Y-%m-%d}", "", git_line, *metis_summary()]
    report = "\n".join(lines).rstrip()
    context = "Session-start status (scripts/session-start.py):\n" + report
    if incoming:
        context += ("\n\nThis repo has updates available on origin/main:\n" + incoming +
                    "\nTell the user updates are available and ask whether to pull them with git pull "
                    "before doing other work; wait for their answer.")
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
