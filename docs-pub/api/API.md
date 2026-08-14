# METIS API

This page is an index only — pick the surface that matches your audience, then go
read *that* surface's playbook. Nothing below duplicates a request/response shape,
auth rule, or limit; those live exactly once, in the linked playbook and the live
OpenAPI schema.

## Which surface you want

**`/api/v1/` is the METIS API** — the open surface for external systems that want to
engage with METIS. If you are integrating with METIS from outside, this is the one
you want. See [`v1-PLAYBOOK.md`](v1-PLAYBOOK.md).

**`/public/`** is a fully open, unauthenticated read-only JSON projection of the data
already public on the site's `/view/*` pages, for external frontends (React apps,
embeds) to build their own views on. No login, no token, no API key. See
[`public-PLAYBOOK.md`](public-PLAYBOOK.md).

**`/api/`** is used by METIS's own product apps for their operational needs —
Coherence, the agent chat record, and integration webhooks such as Telegram. It is
not a general-purpose API and it does not mirror `/api/v1/`. See
[`PLAYBOOK.md`](PLAYBOOK.md), and [`coherence-PLAYBOOK.md`](coherence-PLAYBOOK.md)
for Coherence's routes specifically.

Despite the paths, `/api/v1/` is **not** a versioned edition of `/api/`: they are
independent surfaces with different authentication and error shapes.

Any other prefix you may encounter (e.g. `/eapi/`) is internal and unsupported —
not documented under `docs/pub/`.

## App-owned routes

Some apps expose their own routes on top of a shared surface, documented alongside
their owning app rather than here:

- **Outreach** — `/api/v1/outreach/*` for action queues, LinkedIn enrichment, and
  candidate lists (the one route besides `POST /people` that can create People — on
  Outreach access rather than global edit, and reusing an existing Person rather than
  refusing). See
  [`outreach-PLAYBOOK.md`](outreach-PLAYBOOK.md) for the client flow, and
  [`../metis_apps/outreach/linkedin-outreach.md`](../metis_apps/outreach/linkedin-outreach.md)
  for the web import and campaign guide.
