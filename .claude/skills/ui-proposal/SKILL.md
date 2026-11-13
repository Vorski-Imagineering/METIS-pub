---
name: ui-proposal
description: Use when the user finds a METIS page confusing or hard to use and wants ideas to improve it, or wants a UI improvement proposal written up and filed as a GitHub issue — e.g. "this page is confusing, how could we organise it", "give me ideas to make this easier for a regular user", "add info boxes to …", "file an issue with these UI suggestions for Victor". Reviews the page, lists the problems, proposes solutions (optionally with an HTML mockup), and once the user is happy files the proposal as an issue on Vorski-Imagineering/METIS-pub.
---

# UI improvement proposal → GitHub issue

The user points at a METIS page that is confusing. This skill turns that into a
proposal a developer can act on: **look → problems → solutions → (mockup) → user
approves → file the issue.** Never skip to filing; the issue is the last step and
only happens on the user's go-ahead.

## 1. Look at the page yourself

Don't propose from the URL alone.

- `app.the-gathering.earth` needs the user's login, so use the Chrome connector
  (`mcp__claude-in-chrome__*`): load the tools in one `ToolSearch`, `navigate`,
  then `computer` screenshot **and** `get_page_text` in one `browser_batch`.
  Scroll if the page is long. Close your tab when done.
- If the user is not signed in, ask them to sign in in that tab; never enter
  credentials.
- The same applies to `dev.the-gathering.earth`: new features (e.g. Asks, Janus
  editors) often exist only on dev before release, so the user may point you there.
- For behaviour you can't see (what a setting does, where data goes), check
  `docs-pub/` first (`Grep`). If the docs don't say, search the issues too
  (`gh search issues --repo Vorski-Imagineering/METIS-pub "<term>"`): unreleased
  features are specced in issues, not docs. If neither says, write it as an
  assumption for the developer to confirm, never as fact.

## 2. Problem statements

A numbered list, each one concrete and tied to something on the page. Write them
from a **regular user's** point of view. Things to check for:

| Look for | Example |
|---|---|
| Internal jargon or raw codes shown to users | "Holon", `join_holon`, `multi_select`, "Journey diagnostics" |
| No clear actions on a "settings" page | No Edit / Copy / Preview buttons |
| The most useful thing buried | Share link shown as a relative path, no copy button |
| The same setting shown twice | Same journey in two sections |
| Empty "—" rows with no reason given | Unused fields that depend on another setting |
| Flat hierarchy | Every section the same weight; the key fact in the smallest text |
| Unexplained badges or states | "locked" with no tooltip |

Include any problems the user names themselves.

## 3. Solutions

- **A proposed layout**: sections in order of what the user needs first, each
  with a plain heading phrased as an outcome ("What happens when someone signs
  up", not "Journey config").
- **Info boxes**: give the actual copy, 1–2 sentences each, written as outcomes
  ("people who sign up will…"), not configuration ("membership journey = …").
  One per section; a dismissible "how to read this page" box for first-timers.
- **Advanced / technical details** collapsed at the bottom, not deleted.
- **Quick wins**: 3–5 small changes in case the full redesign is too much.

Answer follow-up "what if…" questions (e.g. "what if someone changes the
journey?", "where do new form answers go?") as part of the proposal: describe
the flow, the warning or info text the user would see, and who is allowed to do
it. These answers go into the issue too.

## 4. Mockup (offer it, don't force it)

After the solutions, offer a visual mockup. If the user wants one:

- Ask whether to match the **current METIS look** (cream `#f6f5f0` background,
  white cards, olive `#5b6824` accents, small grey labels, Inter) or use a design
  system. Matching METIS is the usual choice: it reads as a drop-in replacement.
- For viewing, an Artifact is fine. **For the issue, always also produce one
  standalone `.html` file** (inline CSS, plain JS, no build step, works at phone
  width) in the scratchpad: that is what goes into the issue.
- To check the mockup yourself (desktop and phone width), the built-in browser
  can show a local file but can't screenshot or click it. Serve the scratchpad
  instead: `py -m http.server 8765 --bind 127.0.0.1` in the background, then
  `navigate` to `http://127.0.0.1:8765/<file>.html`. Check
  `document.documentElement.scrollWidth` equals the width at the mobile preset.
  Stop the server when the user has seen it.
- No invented data: unknown numbers are `[PLACEHOLDERS]`. Add a one-line note at
  the top saying it's a static mockup.
- Reflect every agreed change in the HTML, including answers to follow-up
  questions (e.g. a "Change journey" link, a "Saved to" column).

## 5. Wait for the user to be happy

Ask whether they want changes or are ready to file. When they say file it,
confirm in one line: the repo, the title, and who it is assigned to. Ask who
to assign if they haven't said. Victor is `vvorski`. Check the name against
the assignee list (step 6); never guess an `@`-mention.

## 6. File the issue

### GitHub CLI check: ask before installing

```bash
gh --version
```

On Windows a freshly installed `gh` is not on the current shell's PATH; also try
`"C:\Program Files\GitHub CLI\gh.exe" --version` before concluding it's missing.

**If `gh` is missing, ask the user whether to install it.** Don't install
without a yes, and don't fall back to filling GitHub's web form unless they
prefer that. On a yes:

| OS | Command |
|---|---|
| Windows | `winget install --id GitHub.cli -e --source winget --accept-source-agreements --accept-package-agreements --silent` |
| macOS | `brew install gh` |
| Linux | see https://github.com/cli/cli/blob/trunk/docs/install_linux.md |

Then check `gh auth status`. If not logged in, start
`gh auth login --hostname github.com --git-protocol https --web` **in the user's
Terminal panel** (`mcp__terminal__run_in_terminal`); it's interactive. Tell
them to press Y for "Authenticate Git", copy the one-time code, and approve in
the browser. Wait for them to say it's done, then re-run `gh auth status`.

### Create it

- Repo: `Vorski-Imagineering/METIS-pub` (its README says METIS issues go there).
- Check the assignee exists: `gh api repos/Vorski-Imagineering/METIS-pub/assignees --jq '.[].login'`.
- Write the body to a file in the scratchpad and pass `--body-file`. Never put
  it in a command-line argument.
- **GitHub rejects `.html` attachments**, so embed the mockup in the body:

  ````markdown
  <details>
  <summary>page-name-redesign.html</summary>

  ```html
  …full file…
  ```

  </details>
  ````

  Build the merged body with a script that reads both files. The body limit is
  65,536 characters. If it is over, put the HTML in a secret gist
  (`gh gist create file.html`) and link it instead.
- `gh issue create --repo Vorski-Imagineering/METIS-pub --title "…" --body-file <file> --assignee <login>`

### Verify

Read it back and check the title, assignee, body length and that the body ends
with the mockup's `</html>`. In PowerShell, parse with `ConvertFrom-Json`.
Don't use `--jq` with strings that contain `<` or quotes, because PowerShell
quoting breaks them. Then give the user the issue link.

### Linking a branch to the issue (only when asked)

If the user asks to put a branch into the issue (e.g. a skill update made
while writing the proposal):

1. Never commit on `main`: create a branch first, then commit there.
2. Push it (`git push -u origin <branch>`). A link to a branch that only
   exists locally leads nowhere.
3. Comment on the issue with `gh issue comment <n> --body-file -`, linking
   `https://github.com/Vorski-Imagineering/METIS-pub/tree/<branch>` and the
   commit hash.
4. Say plainly what the branch changes. If it doesn't implement the issue
   (a skill or docs tweak, for example), state that in the comment so whoever
   picks the issue up doesn't mistake it for the fix.
5. Later commits pushed to the same branch show up via the same link, so
   don't post a new comment for each one.

## Issue body template

```markdown
## Problem
The <page name> page (`<path>`) is hard to understand for a regular user:
1. **<problem>.** <one-line detail>
…

## Proposed layout (see mockup below)
1. **<section>:** <what it shows, what it does>
…
Info box style: <one line>

### Quick wins if a full redesign is too much
- …

## <Each follow-up question answered, as its own section>
…*(Please confirm this matches current behaviour.)* where it's an assumption.

## Mockup
Standalone static HTML with no real data (placeholders are in `[BRACKETS]`).
Save it as `<name>.html` and open it in a browser.
<details>…</details>
```

## Red flags

| Thought | Reality |
|---|---|
| "I'll file it now, they liked the ideas" | Filing waits for an explicit go-ahead. |
| "gh isn't there, I'll just use the browser form" | Ask to install `gh` first; the browser form is a fallback only if they prefer it. |
| "I'll attach the .html file" | GitHub refuses it. Embed it in `<details>` or use a gist. |
| Stating how the backend works from a guess | Check `docs-pub/`; otherwise mark it as an assumption to confirm. |
| Mockup with made-up counts or names | Use `[PLACEHOLDERS]` instead. |
| `@victor` in the body | Assign the issue to `vvorski` instead of `@`-mentioning a guessed username. |
