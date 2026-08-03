---
name: linkedin-automation
description: >
  LinkedIn automation workflows for accepting connection invitations, messaging connections,
  listing pending invites, extracting people search results to a Google Sheet or a JSON file,
  and sending connection requests from a Google Sheet. Use this skill whenever the user wants
  to do anything with LinkedIn — accepting invites, bulk accepting, messaging connections,
  checking pending invitations, scraping search results to a spreadsheet, capturing a filtered
  people search by keyword/location/degree, enriching a profile with its full About text and
  recent activity, or sending outreach connection requests from a spreadsheet.
  Trigger on phrases like: "accept LinkedIn invites", "message my connections", "check my pending invitations",
  "how many invites do I have", "save LinkedIn search results", "bulk accept", "send connection requests
  from my sheet", "connect with people in the spreadsheet", "search LinkedIn for people in
  <place>", "find my connections in <place>", "capture this LinkedIn search", "enrich this
  profile", "get their About / bio / recent post", or any request involving LinkedIn
  connection management or outreach automation.
---

# LinkedIn Automation

This skill automates LinkedIn connection management and outreach using the Chrome browser connector.
All workflows require the Chrome extension to be active with a LinkedIn session open.

## Workspace paths

All file operations use paths relative to the user's workspace folder. Resolve the actual mounted path for that folder at the start of each session — do not hardcode session-specific paths.

- **Message template**: `{workspace}/texts/accept-invite.txt`
- **Messaged log**: `{workspace}/messaged-log.txt`

## Workflow routing

Read the user's message and pick the right workflow:

| Intent | Command file |
|---|---|
| "List / show my pending invitations" | `{workspace}/.claude/commands/invites.md` |
| "Accept one invitation" | `{workspace}/.claude/commands/accept-one.md` |
| "Accept N invitations" / "bulk accept" | `{workspace}/.claude/commands/accept-many.md` |
| "Message N connections" | `{workspace}/.claude/commands/message-connections.md` |
| "Search LinkedIn / extract search results to a Google Sheet" | `{workspace}/.claude/commands/search-to-sheet.md` |
| "Search LinkedIn people by keyword / location / degree and capture the results" | `{workspace}/.claude/commands/linkedin-search-capture.md` |
| "Find a person's LinkedIn URL by name" / "fill empty LinkedIn column" | `{workspace}/.claude/commands/linkedin-find-person.md` |
| "Send connection requests from a spreadsheet / sheet" | `{workspace}/.claude/commands/connect-from-sheet.md` |
| "Enrich / look up a LinkedIn profile's About / bio / recent post" | `{workspace}/.claude/commands/linkedin-enrich-profile.md` |

Read the appropriate command file before starting work.

## Pacing — mandatory for every workflow

**Never loop over people without a delay between them.** LinkedIn throttles fast automation,
and the throttled response is silent: it returns HTTP 200 with the right name, headline and
location, and simply omits About, follower counts, company and school. A fast run therefore
*looks* successful while writing empty fields for most people. Pacing is what keeps the data
honest, not just what keeps the account safe.

### The delay function

Use an **exponential** distribution, not a fixed sleep. Human activity is a Poisson process,
so the gaps between actions are exponentially distributed: mostly short, occasionally long.
A constant delay — or a uniform random one — is itself a recognisable machine signature.

```javascript
// Exponential inter-action delay, in ms. Inverse-transform sampling.
// ~10% of the time, add a heavier "got distracted" pause on top.
const humanDelay = (meanMs, minMs, maxMs) => {
  // Shifted exponential. Do NOT clamp at the minimum instead: clamping puts ~30%
  // of draws on the exact same value, which is itself a machine fingerprint.
  const scale = Math.max(1, (meanMs - minMs) / 1.2);
  let d = minMs - scale * Math.log(1 - Math.random());
  if (Math.random() < 0.1) d += -scale * 2 * Math.log(1 - Math.random());  // distracted
  return Math.min(maxMs, Math.round(d));
};
const pause = ms => new Promise(r => setTimeout(r, ms));

await pause(humanDelay(45000, 20000, 300000));  // e.g. between profile visits
```

### Pacing from the agent loop (not in-page JS)

The `humanDelay`/`pause` pair above runs *inside* a page via `javascript_tool` — it does nothing
when you (the agent) are the one looping over people between separate tool calls, e.g. calling
`/message-person` once per person in a Bash/tool-call loop. In that case there is no in-page
JS context to `await` in.

A standalone `sleep N` in the `Bash` tool is blocked by the harness ("Blocked: standalone sleep
N ... use run_in_background"). The working pattern: compute the delay in Python using the same
distribution as `humanDelay`, then run the sleep via `Bash` with `run_in_background: true` —
this returns immediately and a task-notification arrives when the wait is over, which is when
you resume and message the next person.

```python
import random, math
def human_delay(mean_ms, min_ms, max_ms):
    scale = max(1, (mean_ms - min_ms) / 1.2)
    d = min_ms - scale * math.log(1 - random.random())
    if random.random() < 0.1:
        d += -scale * 2 * math.log(1 - random.random())
    return min(max_ms, round(d))
print(human_delay(90000, 40000, 600000))  # seconds to sleep, per the means table below
```

Then `Bash({command: "sleep <seconds>", run_in_background: true})` and wait for its
notification before the next send. Do not chain multiple short sleeps to fake this — one
background sleep per gap.

**Do not delegate a paced run like this to a background fork/subagent expecting it to
finish unattended.** Confirmed live: a fork sent message 1/22, started a ~67s background
sleep before person 2, and then sat idle for ~50 minutes — its own "actively running"
self-report was wrong, and it only moved again once the parent explicitly sent it a message
to resume it. Polling it via `TaskOutput` also failed once its background bash child had
already finished (task ID not found) — there's no reliable way to check on a stalled fork
short of resuming it, and resuming it is indistinguishable from just doing the work yourself.
The pattern above (background sleep, wait for its notification, act on it) works when *you*
— the agent the user is talking to — are driving the loop, because the harness reliably wakes
*you* on that notification. It does not reliably wake a forked/background subagent left to run
on its own. Run person-by-person outreach loops in the foreground of the main conversation,
not delegated to a background agent, even though that means the pacing waits are visible in
the conversation instead of hidden.

### Means by action class

Read actions are cheaper than writes; writes are what get accounts restricted.

| Action | mean | min | max |
|---|---|---|---|
| Search results page → next page | 12 s | 5 s | 90 s |
| Profile visit (read/enrich) | 45 s | 20 s | 5 min |
| Accept an invitation | 30 s | 12 s | 3 min |
| Send a message | 90 s | 40 s | 10 min |
| Send a connection request | 120 s | 45 s | 15 min |

### Burst breaks

After every **8–15 actions** (re-randomise the threshold each time), take a long break:
`humanDelay(300000, 120000, 600000)` — 2 to 10 minutes.

Run size is the user's call. Do the number they asked for; don't impose a limit of your own.
If a run looks large enough to be worth a second thought, say so up front with the expected
duration and let them decide — then run what they asked for.

### Keep the user informed about waiting

Long silences look like a hang. The user must never be left guessing whether the run is
working or stuck.

- **Before starting**, state the expected duration and the pacing:
  `Sending 20 connection requests, ~2 min apart with breaks — expect roughly 45–60 minutes.`
- **Before every long break**, announce it with the actual duration and where the run is:
  `[8/20] Taking a 6 min break to stay within LinkedIn's limits — resuming after.`
- **Do not announce every short inter-action delay** — that is just noise. Per-item progress
  lines already show the run is alive.
- **If a run is stopped** by throttle detection, say so explicitly, with the count completed
  and how to resume. Silence after the last item reads as a crash.

### FIRST: is the tab actually visible?

**LinkedIn does not render the profile body in a background tab.** A hidden tab gets the
topcard and Activity and nothing else — no About, no Experience, no Education — and the
markup for those sections is absent from the DOM entirely, not merely hidden. It is
indistinguishable from throttling by every structural signal below.

Confirmed live, and it cost a whole run: three profiles plus the operator's *own* profile all
came back at `scrollHeight` 1270–1686 with sections `[name, Activity]`, surviving reloads,
scroll passes and ~40 minutes. It was diagnosed as an account-level throttle. It was not — the
MCP tab was simply in the background. The moment the tab was brought to the foreground the
same URL rendered at 2351 → 5388 with About, Featured, Experience, Education and six more
sections, on the same account, seconds later.

So before concluding anything about a sparse or throttled page:

```javascript
JSON.stringify({ visibility: document.visibilityState, focus: document.hasFocus() })
```

`visibilityState` must be `'visible'`. **`hasFocus()` does not matter** — extraction works
fine with `hasFocus: false`, i.e. Chrome itself can be in the background as long as the
profile tab is the active tab within its own window. If it reports `'hidden'`, the fix is to
activate that tab, not to wait 30 minutes. Tell the user to leave the tab in the foreground
for the duration of a batch run, and never report throttling without having checked this
first.

### Detecting throttling

Only once `visibilityState` is `'visible'`. A **throttled** profile page looks like this:

| | Healthy | Throttled |
|---|---|---|
| `MAIN#workspace` scrollHeight | ~3000+ | ~1650–1750 |
| Sections present | Highlights, About, Featured, Activity | name + Activity only |
| Topcard | shows followers / connections | shows neither |

The follower/connection count is *a* signal — a genuine profile with no About usually still
shows it — but **it is not sufficient on its own.** Confirmed live on two profiles minutes
apart: both served a complete topcard including "500+ connections" and a follower count while
rendering no About, no Experience and no Education, with `scrollHeight` stuck at 1270 and
1637 through a reload and repeated scroll passes. So treat a page as throttled when the
structure has collapsed **and** either the counts are missing **or** there is no body section
at all. Two collapsed profiles in a row means the account is throttled, not that both people
have empty profiles.

**To confirm throttling in one step, load your own profile** (`https://www.linkedin.com/in/me/`).
LinkedIn never hides your own About/Experience from you, and visiting it notifies nobody, so it
is a free control: if your own profile also renders only `[name, Activity]` with no
`>Experience<` anywhere in `document.documentElement.outerHTML`, the account is throttled and
no amount of scrolling, reloading or selector-fixing will help. Confirmed live — own profile
came back at `scrollHeight` 1686 with the profile body absent from the HTML entirely, at the
same time as two target profiles collapsed at 1270 and 1637.

**On detection: stop the run.** Report how many were completed and the last one processed so
the run can resume later. Never record a throttled page's empty fields as real data, and
never retry immediately — backoff means at least 15–30 minutes, and repeated hits mean stop
for the day.

## General notes

- **The message compose `<iframe>` is reused across navigations — never trust it for
  duplicate-checks.** When there's no existing thread, clicking Message opens a full "New
  message" page whose composer lives in `<iframe src=".../preload/?_bprMode=vanilla">`
  (same-origin, reachable via `frame.contentDocument`). That iframe element persists in the
  DOM across page navigations within the same tab, and after a successful send its
  `contentDocument` can still hold the *previous* person's message text even once you've
  navigated to a new profile and opened their thread. Confirmed live and it cost a run: a
  duplicate-check read `iframe.contentDocument.body.innerText` and found the just-sent invite
  text — but it was leftover from the prior person's send, not this person's actual thread,
  producing a false "already messaged" for someone who had never been contacted.
  **Always check for prior messages via the real thread DOM instead:**
  `document.getElementById('interop-outlet').shadowRoot` — this reflects what's actually
  rendered and was verified correct across multiple live sends in the same session. The
  iframe is fine for *typing* into a fresh "New message" compose box; it is never the right
  place to check existing-thread text. When a thread already has history, Message instead
  opens a **docked panel** whose composer is a `[contenteditable="true"][role="textbox"]`
  inside that same shadowRoot (not the iframe) — see message-person.md step 6 for
  disambiguating multiple stale/minimized panels there by bounding-rect `top`/`w`.
- **Debug mode is always ON.** If any step fails, stop immediately and report the exact error. Do not try fallbacks or workarounds.
- LinkedIn uses obfuscated CSS class names — prefer `aria-label`, `role`, and text content to locate elements.
- Use Promise-based polling (not `await` or `sleep`) for all wait loops.
- Always use `tabs_context_mcp` first to get a valid tab ID before any browser operations.
- **`window.scrollTo` is a no-op on profile pages.** The scroll container is `MAIN#workspace`.
  Set `document.getElementById('workspace').scrollTop` instead. Profile sections are
  virtualised and only render while in view, so extract as you scroll, not afterwards.
- **Never click "…more" / "see more" page-wide.** Recommendation cards contain their own, and
  clicking one navigates away from the profile. Always scope expansion to a named section.
- **Profile-page parsing lives in one place:**
  `automation/linkedin-automation/scripts/linkedin-profile-extract.js`, ported from METIS's
  Chrome-extension parser. Inject that file and call `window.LinkedInProfile.*` — do not write
  new inline extraction JavaScript for profile pages. It covers topcard fields, About,
  experience, education, photo, other sections, hydration, throttle detection and the
  `get_page_text` payload hand-off, and it has a jsdom test suite next to it
  (`linkedin-profile-extract.test.js`). Fix bugs there, with a test.
