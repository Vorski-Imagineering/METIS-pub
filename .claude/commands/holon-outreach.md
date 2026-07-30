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

### 2. Find candidates

```bash
curl -s -G "${METIS_URL}/api/v1/holons/${HOLON_ID}/memberships" \
  -H "Authorization: Bearer ${METIS_TOKEN}" \
  --data-urlencode "journey=<journey slug>" \
  --data-urlencode "step_slug=<step slug>" \
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

#### 6c. Open the thread and check for a prior send BEFORE typing anything

Click Message, then read the existing thread text:

```javascript
const shadow = document.getElementById('interop-outlet').shadowRoot;
const host = shadow.firstElementChild;
host.innerText || host.textContent || '';
```

Search that text for a distinctive substring of the message (e.g. its first sentence, or a
unique URL it contains). If found, the person was **already messaged this content** — do not
send again. Close the panel, and in step 6e advance their membership with a note saying so
instead of a "sent" note.

This check exists because it happens in practice: a thread can already hold the exact invite
text from an earlier manual or automated run, and resending duplicates it.

#### 6d. Send (only if 6c found nothing)

Follow `.claude/commands/message-person.md` steps 6–8 for typing into the correct editor,
verifying visually, and clicking Send scoped to the right conversation container. Confirm the
composer cleared afterward — don't trust the click alone.

#### 6e. Advance the membership, always with a note

```bash
curl -s -X POST "${METIS_URL}/api/v1/memberships/${MEMBERSHIP_ID}/update" \
  -H "Authorization: Bearer ${METIS_TOKEN}" -H "Content-Type: application/json" \
  -d '{"step_slug": "<next step slug>", "note": "<what happened>"}'
```

`note` is required and must be non-empty — use one of:
- `"Outreach message sent via LinkedIn."` (6d ran and the send verified)
- `"Thread already contained this invite; marked as invited without resending."` (6c found a match)

Skip this call entirely for people skipped in 6b/6d (no channel, not 1st-degree, send failed) —
their step should stay where it is so they surface again later, and say why in the summary.

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
