---
description: Message everyone at a given Holon/Journey/step via LinkedIn, then advance their membership with a note
allowed-tools: Read, Bash, mcp__claude-in-chrome__tabs_context_mcp, mcp__claude-in-chrome__tabs_create_mcp, mcp__claude-in-chrome__navigate, mcp__claude-in-chrome__javascript_tool, mcp__claude-in-chrome__computer, mcp__claude-in-chrome__read_page
---

Message people who share a METIS Holon, Journey, and step, using an existing message text
file, then advance each Membership to record the outcome.

`$ARGUMENTS`: `<holon name or slug> <journey slug> <step slug> <message file> [count N]`
Example: `2026-usa-california person-outreach to_contact texts/TGUSA26-Invite-1.txt 15`

> **Debug mode is ON.** If any step fails or returns an unexpected result, stop immediately
> and report the exact error. Do not try fallbacks or workarounds.

## Steps

### 1. Resolve the holon — never guess

Run the auth flow from `.claude/commands/metis.md`, then:

```bash
curl -s -G "${METIS_URL}/api/v1/holons" -H "Authorization: Bearer ${METIS_TOKEN}" \
  --data-urlencode "q=<name>"
```

If the query is already an exact slug, `GET /holons/by-slug/{slug}` works directly instead.

- **Zero matches on the literal name**: broaden the query (drop a word) and try again — don't
  assume the holon doesn't exist. "USA Gathering" returns nothing; "USA" or "Gathering" surfaces
  "2026 USA California" as the actual match.
- **More than one plausible match, or the match isn't an obvious exact name**: show the
  candidate(s) (id, name, slug, type, parent) to the user and stop — get explicit confirmation
  of the holon id before doing anything that messages real people under it.
- Proceed only once you have one confirmed `holon_id`.

### 2. Find candidates — always scoped to the logged-in user's own worklist

**Always filter by `responsible_person_id` set to the authenticated caller's own person id**
(the `person.id` returned by the login call in step 1 of `.claude/commands/metis.md`), unless
the user explicitly names someone else's list ("run Christine's outreach", "message everyone
regardless of owner"). Without this filter, `GET /holons/{holon_id}/memberships` returns *every*
membership at that step across all owners — messaging or advancing someone else's assigned
contact from your own LinkedIn account, without their involvement, is exactly the failure mode
this guards against.

```bash
curl -s -G "${METIS_URL}/api/v1/holons/${HOLON_ID}/memberships" \
  -H "Authorization: Bearer ${METIS_TOKEN}" \
  --data-urlencode "journey=<journey slug>" \
  --data-urlencode "step_slug=<step slug>" \
  --data-urlencode "responsible_person_id=<caller's own person id>" \
  --data-urlencode "limit=<N, max 200>"
```

Collect `membership_id`, `person.id`, `person.name` for each item. If `has_more` is true, tell
the user how many total candidates exist vs. how many you're about to process (the page you
fetched, or the requested count N — whichever is smaller).

### 3. Read the message

Use `Read` on the given message file path under `texts/`. Use it verbatim — do not paraphrase,
shorten, or "improve" it. If the path doesn't exist, stop and ask the user which file to use;
do not invent replacement copy.

### 4. Look up contact info per candidate

```bash
curl -s "${METIS_URL}/api/v1/people/${PERSON_ID}" -H "Authorization: Bearer ${METIS_TOKEN}"
```

Take `contact.linkedin`. If missing, skip this person (no channel available) and record it in
the final summary — don't advance their membership, since nothing happened.

### 5. Before starting, tell the user the plan

State: candidate count, message file used, and expected duration at ~90s mean per send plus
occasional longer breaks (see `.claude/skills/linkedin-automation/SKILL.md`'s Pacing section —
follow its `humanDelay` distribution and burst-break cadence exactly; don't re-derive your own
numbers).

### 6. For each candidate

#### 6a. Open the profile in the foreground

Navigate the tab to the LinkedIn URL. Before doing anything else, confirm:

```javascript
document.visibilityState
```

Must be `'visible'`. If not, that tab needs to be the active tab — fix it before continuing
(see linkedin-automation's "FIRST: is the tab actually visible?").

#### 6b. Confirm 1st-degree and locate Message

Take a screenshot (JS calls to find/click the Message button can silently return `{}` — verify
visually, per linkedin-automation's known quirks). Confirm the profile shows "· 1st" and a
Message button is present. If not 1st-degree, **do not send a connection request** — this
command only messages existing connections. Skip and record in the summary.

**Read the degree from the topcard, not the whole page.** A body-wide
`document.body.innerText.match(/·\s*(1st|2nd)/)` matches the "More profiles for you" sidebar
and reports a stranger's degree as the target's. Anchor to the name instead:

```javascript
const txt = (document.body.innerText || '').replace(/\s+/g, ' ');
const i = txt.indexOf(TARGET_NAME);                       // first occurrence = topcard
const degree = (txt.slice(i, i + 320).match(/·\s*(1st|2nd|3rd\+?)/) || [])[1] || null;
const buttons = [...new Set(Array.from(document.querySelectorAll('a,button'))
  .map(b => b.textContent.trim())
  .filter(t => ['Message','Connect','Pending','Follow','More'].includes(t)))];
JSON.stringify({ degree, buttons });
```

Widen the slice for people with long headlines — a 200-char window missed the marker on one
profile whose headline listed five roles. A **`Pending`** button means a connection request is
already outstanding: still a skip, but worth noting so it can be retried after acceptance.
A "Message" button existing does **not** prove 1st-degree — it appears for 2nd-degree
profiles too and leads to InMail.

#### 6c. Open the thread and check for a prior send BEFORE typing anything

Click Message, then read the existing thread text — **scoped to this person's pane**:

```javascript
// Works on both UIs: pick the composer, then walk up to the FIRST ancestor naming the target.
const frame = Array.from(document.querySelectorAll('iframe'))
  .find(f => (f.src || '').includes('/preload/'));
const doc = frame ? frame.contentDocument
  : document.getElementById('interop-outlet').shadowRoot;
const box = doc.querySelector('[contenteditable="true"][role="textbox"]');
let node = box, pane = null;
for (let i = 0; i < 12; i++) {
  node = node.parentElement; if (!node) break;
  if ((node.innerText || '').includes(TARGET_NAME)) { pane = node; break; }
}
const thread = (pane ? pane.innerText : '').replace(/\s+/g, ' ').trim();
```

> **Do NOT use `shadow.firstElementChild`.** It is a `<style>` element: it returns ~2.6 MB of
> CSS, never the conversation. A check written against it silently matches nothing, so every
> person looks un-messaged and everyone gets a duplicate. Confirmed live on 2026-08-10.

`pane === null` means you failed to isolate the conversation — **stop**, don't fall back to
the whole document. A fixed-depth parent walk escapes into the shared overlay and returns a
*different* person's thread; on the first live run that surfaced an unrelated contact's
messages while a third person's panel sat docked alongside.

**Search for more than one invite variant.** Match on the stable, distinctive parts — the
campaign URL (e.g. `regenworld.net`) and a landmark phrase (e.g. `California Redwoods`) —
not the current file's opening sentence. Earlier campaigns used different copy for the same
invitation; on 2026-08-10 two people (Liz Brittle, Melanie Larkins) already held a July
variant that shared the URL and landmark but none of the current wording. If found, **do not
resend** — in 6e advance the membership with the "already contained" note instead.

#### 6d. Send (only if 6c found nothing)

Follow `.claude/commands/message-person.md` steps 6–8 for typing into the correct editor,
verifying visually, and clicking Send scoped to the right conversation container. Confirm the
composer cleared afterward — don't trust the click alone.

#### 6e. Advance the membership, always with a note that includes the message text

`note` is required, must be non-empty, and — for a "sent" outcome — must include the literal
message text that was sent (the exact content read in step 3), not just a generic label. A
note that only says "message sent" is not enough to audit later: the user (or a future run)
needs to see *what* was sent without re-opening the LinkedIn thread.

```bash
curl -s -X POST "${METIS_URL}/api/v1/memberships/${MEMBERSHIP_ID}/update" \
  -H "Authorization: Bearer ${METIS_TOKEN}" -H "Content-Type: application/json" \
  -d "$(python3 -c "
import json
print(json.dumps({
  'step_slug': '<next step slug>',
  'note': 'Outreach message sent via LinkedIn:\n\n' + open('<message file path>').read()
}))
")"
```

Use one of these note bodies:
- `"Outreach message sent via LinkedIn:\n\n<full message text>"` (6d ran and the send verified)
- `"Thread already contained this invite; marked as invited without resending."` (6c found a match — no new text was sent, so there's nothing to quote)

Skip this call entirely for people skipped in 6b/6d (no channel, not 1st-degree, send failed) —
their step should stay where it is so they surface again later, and say why in the summary.

**METIS has no note-edit endpoint.** `POST /memberships/{id}/update` always *creates* a new
note — it never edits an existing one (confirmed in `docs-pub/api/v1-PLAYBOOK.md`). If a note
was already written without the message text (e.g. from an earlier version of this skill) and
needs correcting after the fact, call update again with **only** `note` set — omit `step_slug`
and `advance_step` — which attaches a supplementary note without moving the step again.

#### 6f. Print progress and pace before the next person

```
[i/total] ✓ Messaged {name}   (or: already-messaged / skipped: {reason})
```

Wait a human-paced delay before the next person using the agent-loop pattern from
linkedin-automation's SKILL.md ("Pacing from the agent loop" — background `sleep`, not
in-page `setTimeout`), with the **"Send a message"** row's mean/min/max (90s / 40s / 10min).
Take the 2–10 min burst break after every 8–15 sends, and announce it before it starts.

**Stop the run immediately** on any throttle signal from linkedin-automation's detection
table (collapsed profile structure, missing connection counts on two profiles in a row). Report
how many were completed and the last person processed so the run can resume later.

### 7. Final summary

```
Done — messaged {N}, already-messaged (advanced only) {M}, skipped: {name (reason)}, …
```
