# Coherence API — connection skill

You are about to query the Coherence API (`/api/coherence/`) on the live METIS instance.
Full endpoint reference, auth model, and golden paths are in `docs-pub/api/coherence-PLAYBOOK.md` —
read it now before making any calls, especially if a call returns an unexpected `401`/`404`/`400`.

---

## Step 1 — Log in (reuse the METIS auth flow)

Coherence shares the same per-user login as the core METIS API. Follow the login steps in
`.claude/commands/metis.md` (Step 1) to obtain `METIS_TOKEN` — same `.env` credentials
(`API_LOGIN_SECRET`, `METIS_EMAIL`, `METIS_PASSWORD`), same `POST /api/v1/auth/login` call.
Do not duplicate or reinvent that flow here.

```bash
METIS_URL="https://app.the-gathering.earth"
METIS_API_KEY=$(grep '^API_LOGIN_SECRET=' .env | cut -d= -f2-)
METIS_EMAIL=$(grep '^METIS_EMAIL=' .env | cut -d= -f2-)
METIS_PASSWORD=$(grep '^METIS_PASSWORD=' .env | cut -d= -f2-)

METIS_TOKEN=$(curl -s -X POST "${METIS_URL}/api/v1/auth/login" \
  -H "X-Metis-Api-Key: ${METIS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"email": "'"${METIS_EMAIL}"'", "password": "'"${METIS_PASSWORD}"'"}' \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['token'])")
```

The token is valid 24 hours; reuse it for every call below rather than logging in again per-request.

Per the PLAYBOOK's current Authentication section, most Coherence endpoints accept this same
per-user token (as well as the shared `API_TOKEN` secret or a session cookie) — but a few
(`/conversation-events`, `/conversations/search`, transcript replacement, audio upload/download)
*require* a per-user token and reject the shared secret. **Re-check the Authentication section
and the endpoint's row in the Quick Reference table before assuming which auth a given endpoint
takes** — this has changed between API versions.

---

## Step 2 — List Coherence Conversation Events

```bash
curl -s "${METIS_URL}/api/coherence/conversation-events" \
  -H "Authorization: Bearer ${METIS_TOKEN}"
```

Add `?holon_slug={slug}` to scope to one holon plus its descendant tree. Returns every
Conversation Event holon (`id`, `slug`, `name`, `type`, `parent`).

---

## Step 3 — List conversations under an event/holon

```bash
curl -s "${METIS_URL}/api/coherence/conversations/search?holon_slug={slug}" \
  -H "Authorization: Bearer ${METIS_TOKEN}"
```

This is the side-effect-free operational list endpoint — no filters returns every conversation
(scheduled, unscheduled, active, completed). Optional filters combine with **AND**:

- `holon_slug` — ownership: `Conversation.event` is this holon or a descendant
- `connected_holon_slug` — participation: linked via `Conversation.connected`
- `person_id` — the Person is in `Conversation.participants`
- `sort=date_asc` — oldest first (default `date_desc`)

Each result includes event, journey/step, time bounds, participants, and connected holons, but
excludes raw `infos`/`config`/transcript. Missing filter targets return 404; valid filters with
no matches return `[]`.

---

## Step 4 — Get full info for a single conversation

```bash
curl -s "${METIS_URL}/api/coherence/conversations/{id}" \
  -H "Authorization: Bearer ${METIS_TOKEN}"
```

Returns the full `ConversationOut`: `participants`, `connected`, `infos` (publishing/YouTube
artefacts live under `infos.publishing`), `config` (internal/operational — cal.com, Enter
Coherence, Iris state), `start`/`finish`, `journey_slug`/`journey_name`, `step_slug`/`step_title`,
`texts`, `questions`. 404 if the ID doesn't exist.

To pull the YouTube URL for a conversation, read `infos.publishing.youtube.url`.

---

## Notes

- All of this is read-only browsing. If the user asks to *update* a conversation (`infos`/`config`
  patch, `enter-coherence` room state, marking `recorded`, transcript/audio replacement), read the
  corresponding Golden Path in `docs-pub/api/coherence-PLAYBOOK.md` first — those endpoints have
  namespace restrictions, concurrency guards, and idempotency caveats that matter.
- IDs throughout are positive integers; datetimes are ISO 8601 UTC.
