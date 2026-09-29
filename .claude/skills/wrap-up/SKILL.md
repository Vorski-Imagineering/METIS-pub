---
name: wrap-up
description: Use when the user is about to close a session, or asks "are we ok to close", "anything outstanding", "should we store any learnings", or invokes /wrap-up. Finds work left hanging, captures what this session learned in the right place, and gives one verdict on whether it is safe to close.
---

# Wrapping up a session

The user closes sessions. Anything this session leaves hanging, or learned and
did not write down, is lost when they do. This skill makes the pre-close check
the same every time, instead of depending on the user remembering to ask.

Three parts, in order: **find what's hanging → capture learnings → verdict.**
Do the checks; don't answer from memory of the conversation. "I don't think I
left anything" is the failure this skill exists to replace.

## 1. Find what's hanging

Run every check. Report each one, even when it is clean; a silent check
can't be told apart from one you skipped.

**Separate this session's work from what was already there.** The session
opened with a `gitStatus` snapshot. Compare against it. Pre-existing changes
are named as such and left alone; never commit, stash or discard them as
part of wrapping up.

| Check | How |
|---|---|
| METIS-pub working tree | From the repo root: `git status --short` and `git log @{u}.. --oneline 2>/dev/null` (unpushed commits). The checkout lives in a different place on each machine (the server, a laptop), so never hard-code its path. The branch name too: work left on a feature branch is fine if the user knows it's there. |
| Worktrees | `git worktree list`. More than one line means one of them needs an owner or removal (CLAUDE.md: no worktrees unless asked). |
| Background work | Background shell tasks, `Monitor`s, subagents, workflows and scheduled wakeups this session started. `ListAgents` for agents. Say which are still running and whether it matters: a read-only search dying is harmless; a half-finished write (a METIS API call, a file outside the repo) is not. |
| METIS writes | Anything this session wrote to the live METIS instance via the API (holon updates, memberships, relationships, notes) or to LinkedIn. These have no local diff to check — scan the conversation for API/skill calls that mutated state and confirm each one finished and did what was intended. |
| Local files outside the repo | Anything written under `~/Documents`, the scratchpad, or elsewhere per repo convention (e.g. outreach message files, exported CSVs) that the user still needs the path to. |
| Tracker | Every GitHub issue created or edited this session in `Vorski-Imagineering/METIS-pub` (or a linked METIS issue): body carries the substance (not left only in a comment), labels make sense, and comments that now contradict a later edit are fixed, not left as two stories. |
| Docs site | If `docs-pub/`, `site-overlay/`, or `automation/*/README.md` changed, confirm the nav entry (`site-overlay/SUMMARY.md`) and any tag mapping (`site-overlay/tags.yml`) were added, and that a push triggered the `Deploy Docs` GitHub Action successfully (`gh run list` for the branch). |
| Promises | Scan your own replies for "I'll", "next", "later", "follow-up", "want me to". Each one is done, handed to an issue, or listed as open. Offers the user didn't take up are not open items; list them only if the user might have missed the question. |
| Artifacts | Anything published or pinned this session that the user still needs the link to. |

## 2. Capture learnings

Go through the session looking for three kinds of thing:
- **corrections** the user gave (including quiet ones: an answer that rejected your framing);
- **approaches they confirmed**;
- **facts** about the project or its people that aren't in the code or git history.

Put each one in exactly one place:

| It is… | Goes to | Rule |
|---|---|---|
| How the user wants *me* to work, or a project fact that isn't in the repo | **Memory**: the memory directory named in the system prompt (its path differs per machine), one file per fact, plus a line in `MEMORY.md` | Check the index for an existing file first and update it rather than duplicating. Wrong or outdated memories get fixed or deleted now. Follow the memory format in the system prompt. |
| A rule everyone working in the repo should follow, a skill that misled you, a doc that was wrong | **The repo**: `CLAUDE.md`, a `.claude/skills/*` file, `automation/*/README.md` | **Propose, don't write.** These are shared; show the exact text and where it goes, and let the user say yes. If it is bigger than a few lines, it becomes a GitHub issue. |
| A problem with Claude Code itself | **`SendFeedback`** (drafts only; the user approves sending) | Only for a real product or model-behaviour issue seen this session. |
| Only mattered to this session | **Nowhere** | Say so. Not everything is a learning. |

Don't save to memory what the repo already records (code structure, past
fixes, git history, CLAUDE.md), and don't write a memory that restates a rule
already in `CLAUDE.md`.

Save memories without asking; that's what memory is for. Name each one in the
report so the user can object.

## 3. Verdict: resist by default

The user asked for this skill to **push back hard** when things aren't clean.
Closing a session with work hanging is the expensive mistake; one extra
exchange is cheap. So the default answer is **Not yet**, and **Safe to close**
has to be earned by every check in §1 coming back clean.

**Blocks closing** (the verdict is *Not yet*):
- anything this session changed that isn't committed, or is committed but not pushed;
- a background task, agent or workflow still running that writes anything (files, DB, GitHub, METIS, LinkedIn);
- a METIS write this session started that hasn't been confirmed to have finished cleanly;
- an issue this session touched whose body, label and comments disagree;
- a promise from §1 that's neither done nor handed to an issue;
- a learning found in §2 and not yet saved (memory), or not yet put to the user (repo).

**Doesn't block, but is named every time:** pre-existing uncommitted changes
from before the session, with their files. Name them in one line, not as a
reason to refuse. They stay the user's call, and the next wrap-up will name
them again until they're resolved, so they can't quietly go stale.

Write the verdict as:

- **Not yet.** Lead with it, as the first line, in bold. Then a numbered list:
  what is open, what is lost if the session closes now, and the one action
  that closes it. Do the ones you can when the user says so, then **run the
  checks again**; don't carry the old results forward.
- **Safe to close.** Only when nothing blocks. One line per check proving it,
  plus the pre-existing line if there is one.

**If the user wants to close anyway:** don't soften the verdict and don't
suddenly find the problems minor. Say once, plainly, exactly what will be lost
or left dangling, and ask them to confirm that specific list. Their explicit
"yes, close anyway" is the override; your own reassurance never is. Then stop
arguing: it's their session.

Keep the report short: a line per check, the learnings with where each went,
the verdict. Don't bury the answer under a session recap.

## Red flags

| Thought | Reality |
|---|---|
| "I remember what I changed" | Run `git status`. The conversation doesn't show edits made by subagents or hooks. |
| "Those uncommitted files aren't mine, so skip them" | Report them as pre-existing, in one line. The user decides; silence looks like a clean tree. |
| "Nothing worth saving" without having looked | Scan for corrections first. A session where the user redirected you and nothing was saved is the usual miss. |
| Writing to `CLAUDE.md` or a skill during wrap-up | Propose it. Shared files get a yes first. |
| Committing, stashing or pushing to make the tree look clean | Never, as part of wrap-up. Report it and offer; the user decides. |
| "The background task will probably finish" | Say what it is and what happens if the session dies mid-way. |
| "It's basically clean, just one small thing" | One small thing is *Not yet*. Say it that way. |
| The user sounds keen to go, so lead with the good news | Lead with the verdict. Wanting to close is the moment the check matters most. |
| "Safe to close" with a check you didn't run | That's a guess. Run it or report it as unchecked, and unchecked blocks. |
