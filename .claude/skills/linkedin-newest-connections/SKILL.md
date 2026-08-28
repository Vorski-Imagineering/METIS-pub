---
name: linkedin-newest-connections
description: >
  Use when the user wants their newest LinkedIn connections pulled into a METIS
  Outreach candidate list — e.g. "grab my latest connections", "add the newest
  200 connections to a list", "sync recent connections into METIS". Scrapes
  the live /mynetwork connections page (sorted by Recently added) and loads
  the result into an Outreach candidate list via the API.
---

# LinkedIn Newest Connections

Scrapes the most recently added rows off the user's live LinkedIn
`/mynetwork/invite-connect/connections/` page and loads them into a new METIS
Outreach candidate list.

## Routing

Run the `/linkedin-newest-connections` command — read
`.claude/commands/linkedin-newest-connections.md` before starting. It composes:

- **REQUIRED SUB-SKILL:** `metis` — for auth and the Outreach list/candidate
  API calls.
- **REQUIRED SUB-SKILL:** `linkedin-automation` — pacing between scroll/expand
  actions on the connections page.

## Non-obvious rules baked into the command

- **This is not the same page `linkedin-search-capture` documents.** The
  connections list carries no location, no mutuals, and no keyword snippet —
  only name, profile URL, and a connected-on date. Don't expect the richer
  search-card fields here.
- **There is no `outreach-linkedin-network` write path via API.** METIS
  rejects bulk-add to that journey (import-only, CSV via the web UI — see
  [METIS-pub#308](https://github.com/Vorski-Imagineering/METIS-pub/issues/308),
  filed after confirming this live). This command therefore loads people into
  an **Outreach candidate list** (`POST /api/v1/outreach/lists` +
  `.../candidates:bulk-add`), not the network holon directly. That's a
  deliberate, correct choice, not a shortcut — it's what the API actually
  supports, and it matches the existing `linkedin-search-*` list convention
  already used by dozens of other Outreach lists in this METIS instance.
- **List naming is fixed:** `<name> newest connections-<date>`, where `<date>`
  is today in `YYYY-MM-DD`. `<name>` **defaults to the caller's own METIS
  Person name** (`person.name` from the `/api/v1/auth/login` response) — never
  ask the user who they are before checking; the login call already tells you.
  An explicit command argument overrides the default. Check
  `GET /api/v1/outreach/lists` for an exact name match before creating —
  list creation is not idempotent, unlike the candidate bulk-add that follows
  it.
- **Extraction must survive LinkedIn's inconsistent card markup.** Some rows
  render name text as glued anchor text (`"Name• 1st • Headline"`), others
  only expose it via the avatar `<img alt="Name's profile picture">`. Try the
  `img[alt]` route first (strip the `’s profile picture...` suffix), then fall
  back to the visually-hidden `span[aria-hidden="true"]`, then the anchor's
  raw text split on `•`. Verified live on 2026-08-28: an img-alt-first
  extraction recovered clean names for cards where the naive anchor-text split
  glued the headline onto the name.
- **Always `.split('?')[0]` the profile URL** before storing or returning it —
  raw `href` attributes carry a query string and get blocked outright by
  `javascript_tool`'s cookie/query-string filter (see the "Getting more than
  1000 characters" note in the root `CLAUDE.md`).
- **Use the DOM-serialize-then-`get_page_text` pattern for bulk extraction**,
  never many small `javascript_tool` calls — the same 1000-character-per-call
  truncation documented in `linkedin-search-capture.md` applies here.
- **Dedupe by profile URL, not by row.** The connections page renders two
  anchors per card (photo + name) pointing at the same URL — expect roughly
  2 raw `a[href*="/in/"]` anchors per unique person (verified live
  2026-08-28: 85 raw anchors → 44 unique).
- **Scroll-loading can plateau well short of `count` in one sitting — this is
  not a real ceiling on the page.** Verified live 2026-08-28: repeated paced
  scroll cycles (rotating `scrollTop`, `scrollIntoView`, and synthetic
  `WheelEvent` retriggers — see the command's step 2) stalled at 85 raw
  anchors (44 unique), far short of the default `count` of 200. LinkedIn
  doesn't cap how many connections this page will show; the likely cause is
  a session-level soft throttle from prior heavy activity on the account
  that day, not a per-page limit. Take one full burst break
  (`humanDelay(300000, 120000, 600000)`) and retry before concluding the run
  is done — only stop and report the shortfall if it plateaus again after
  that break. All retrigger techniques must be JS-only via `javascript_tool`
  (never `computer`/screenshots) and paced with `linkedin-automation`'s
  `humanDelay` between every cycle — both are hard requirements for this
  skill, confirmed by explicit correction during live testing.
- **The Outreach candidates API is the safe path for re-runs.** Per the
  [Outreach API playbook](../../../docs-pub/api/outreach-PLAYBOOK.md),
  candidate matching is by LinkedIn URL/email, never name, and existing
  People are never overwritten — so re-running this command after scrolling
  further is safe and will not duplicate or corrupt anyone already on a list.
