# CoCo Agent

CoCo is a chatbot that answers questions using your Coherence conversation content — a
standing assistant, not something tied to any one recorded conversation. It's a different
feature from IRIS: IRIS turns a single conversation into publishable content; CoCo lets you
*ask questions* across everything IRIS (and other conversation content) has produced over
time.

## What CoCo is

CoCo is a regular METIS **Agent** — the same chat infrastructure used for any AI assistant in
METIS — configured with a knowledge base ("corpus") built from a Google Drive folder of
conversation content. When you ask CoCo something, it answers grounded in that corpus rather
than from general knowledge, so its answers reflect what's actually in your conversations.

## Talking to CoCo

CoCo works like any other METIS agent:

- **Web chat** — open the agent chat hub and select CoCo from the sidebar. Chat history is
  kept per-conversation, same as any agent thread.
- **Telegram** — if CoCo is linked to Telegram, you can DM it directly and get the same
  answers there. Linking a Telegram account is a one-time self-service step (a confirmation
  link from the bot); ask an admin if you're not sure whether it's set up.

## How the knowledge base stays current

CoCo's corpus is kept in sync with a Google Drive folder on a recurring schedule — new or
updated files in that folder get pulled in, files removed from the folder get pulled out of
the corpus. This isn't instant: expect CoCo's answers to reflect Drive content from the most
recent sync, not the current second. If you just added something to the folder and CoCo
doesn't know about it yet, that's normal — it'll show up after the next sync cycle.

## Configuration

Setting CoCo up is a one-time admin task, not something you do per conversation. It needs:

- A Google Cloud project with Vertex AI configured, and a RAG corpus created there.
- A Drive folder shared with CoCo's service account, whose contents become the corpus.
- Agent configuration (model, project, corpus ID, folder) set once in the admin.

This is genuinely infrastructure setup, so it's documented for engineers/admins rather than
here:

- `docs/dev/agents/AGENTS_SETUP.md` — creating an Agent and its config shape.
- `docs/dev/agents/GOOGLE.md` — RAG corpus creation and how the sync job behaves.
- `docs/dev/metis_apps/coherence/coco-google-connect.md` — the one-time Google Cloud
  service-account setup.

## Common gotchas

- **Answers seem out of date** — the corpus sync hasn't picked up recent Drive changes yet,
  or the Drive folder's sharing permissions changed. Ask an admin to check the sync job.
- **CoCo doesn't respond at all** — this is usually a general agent-configuration issue (not
  CoCo-specific) — check the agent is set up and, for Telegram, that your account is linked.
