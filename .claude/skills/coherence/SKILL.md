---
name: coherence
description: >
  Query the METIS Coherence API — list Coherence Conversation Events, browse conversations
  under an event/holon, and fetch full details (participants, journey, publishing/YouTube
  info) for a single conversation. Use this skill whenever the user wants to look up
  Coherence conversation events or conversations in METIS. Trigger on phrases like:
  "list coherence conversation events", "show conversations in ... event", "read conversation
  ...", "get the YouTube URL of conversation ...", or any request involving Coherence
  conversations, conversation events, or journeys in METIS.
---

# Coherence

This skill connects Claude Code to the live METIS instance's Coherence API
(`https://app.the-gathering.earth/api/coherence/`). It reuses the METIS per-user login flow,
then makes authenticated `curl` calls to browse Conversation Events and Conversations. No
browser needed.

## Routing

1. **Not logged in yet this session** → the `/coherence` command's Step 1 performs the login
   (same flow as `.claude/commands/metis.md`), reusing `.env` credentials.
2. **List Conversation Events** (all, or scoped to a holon) → `/coherence` command Step 2.
3. **List conversations under an event/holon** (optionally filter by connected holon or person) →
   `/coherence` command Step 3.
4. **Get full details on one conversation by ID** (participants, journey, YouTube/publishing
   info, infos/config) → `/coherence` command Step 4.

Read `.claude/commands/coherence.md` before making any calls — it has the exact `curl` commands
and current filter/auth semantics.

## References

- **Command with exact API calls**: `.claude/commands/coherence.md`
- **Full API reference** (auth model, all endpoints, golden paths, field reference,
  namespace rules for writes): `docs-pub/api/coherence/PLAYBOOK.md`
- **Core METIS login flow this skill reuses**: `.claude/commands/metis.md` (Step 1)

## General notes

- Auth requirements differ per endpoint and have changed between API versions — re-check the
  PLAYBOOK's Authentication section and Endpoint Quick Reference table rather than assuming.
- This skill is read-only browsing. For updates (patching `infos`/`config`, `enter-coherence`
  room state, marking a conversation `recorded`, transcript/audio replacement), read the
  matching Golden Path in `docs-pub/api/coherence/PLAYBOOK.md` first — those endpoints have
  namespace restrictions and concurrency guards.
