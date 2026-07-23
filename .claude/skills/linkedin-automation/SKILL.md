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

### Detecting throttling

Check after each profile visit. A **throttled** profile page looks like this:

| | Healthy | Throttled |
|---|---|---|
| `MAIN#workspace` scrollHeight | ~3000+ | ~1650–1750 |
| Sections present | Highlights, About, Featured, Activity | name + Activity only |
| Topcard | shows followers / connections | shows neither |

The distinguishing signal is the **follower/connection count**: a genuine profile with no
About still shows it. Missing About *and* missing follower count together means throttled,
not empty.

**On detection: stop the run.** Report how many were completed and the last one processed so
the run can resume later. Never record a throttled page's empty fields as real data, and
never retry immediately — backoff means at least 15–30 minutes, and repeated hits mean stop
for the day.

## General notes

- **Debug mode is always ON.** If any step fails, stop immediately and report the exact error. Do not try fallbacks or workarounds.
- LinkedIn uses obfuscated CSS class names — prefer `aria-label`, `role`, and text content to locate elements.
- Use Promise-based polling (not `await` or `sleep`) for all wait loops.
- Always use `tabs_context_mcp` first to get a valid tab ID before any browser operations.
- **`window.scrollTo` is a no-op on profile pages.** The scroll container is `MAIN#workspace`.
  Set `document.getElementById('workspace').scrollTop` instead. Profile sections are
  virtualised and only render while in view, so extract as you scroll, not afterwards.
- **Never click "…more" / "see more" page-wide.** Recommendation cards contain their own, and
  clicking one navigates away from the profile. Always scope expansion to a named section.
