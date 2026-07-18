# METIS Documentation

Public documentation for METIS — the platform behind The Gathering. This covers the core
concepts you configure and work with, the IRIS conversation-publishing pipeline, and the
REST API.

> This tree is published automatically from the METIS source repository. It is the
> user- and integrator-facing manual; internal engineering and operations docs live
> elsewhere and are not published here.

---

## 1. METIS Core

The shared platform: navigation, the core CRM, and the concepts everything else builds on.

**Navigation & usage**
- [Getting started — navigating METIS](web/app/getting-started.md) — the shell, the sidenav,
  and where everything lives. *(Start here.)*
- [Focus: the holon scoping model](web/app/focus-and-scoping.md) — the one concept every
  other guide assumes.
- [Working with people & orgs](metis_apps/metis/people-and-orgs.md) — finding, adding, and
  tracking people and organisations; journeys, kanban, mentions, relationships.
- [Access & permissions (user view)](core/access-and-permissions.md) — why you can (or
  can't) see and do things.
- [Using the Chrome extension](extension/using-the-extension.md) — capturing LinkedIn
  profiles and companies into METIS.

**Concepts & configuration**
- [Apps](web/app/apps.md) — METIS is made of independent pieces of functionality called
  apps; different holons use different apps.
- [Holons and classes](metis_apps/metis/holons-and-classes.md) — what holons are, how
  classes work, and how a class's configuration decides what each holon shows and can do.
- [Additional fields](metis_apps/metis/info-fields.md) — defining custom structured fields
  on a holon class and filling in their values per holon.
- [Journeys](core/JOURNEY.md) — the progression model for tracking where a person or holon
  sits in a relationship, and how to create new journeys.
- [Permissions and roles](core/PERMISSIONS.md) — the full model: groups, config-flag
  permissions, and public visibility.

## 2. METIS App: Coherence

Conversations and **IRIS**, the pipeline that turns a recorded conversation into published
media.

- [What IRIS does](metis_apps/coherence/iris/user-benefit-iris.md) — the value and
  workflow overview.
- [Using IRIS — conversations walkthrough](metis_apps/coherence/iris/using-iris.md) — the
  click-path for staff running a conversation through the pipeline.
- [Participant approval guide](metis_apps/coherence/iris/participant-approval.md) — for
  conversation participants asked to review and approve what's published.
- [Prompt authoring guide](metis_apps/coherence/iris/prompt.md) — customising the AI
  instructions and injecting live conversation context into prompts.
- [YouTube uploader setup](metis_apps/coherence/iris/youtube-upload-config.md) — connecting
  a journey step to a YouTube channel.
- API: [Coherence API playbook](api/coherence-PLAYBOOK.md) ·
  [Conversation JSON fields](api/CONVERSATION_JSON_FIELDS.md).

## 3. METIS App: The Gathering

- [Camps & local gatherings](metis_apps/gathering/camps-and-gatherings.md) — running The
  Gathering's camps and local gatherings.

## 4. METIS App: Audax

- [Quests & missions](metis_apps/audax/quests-and-missions.md) — *placeholder; usage guide
  not written yet.*

## 5. METIS App: Outreach

- [LinkedIn outreach](metis_apps/outreach/linkedin-outreach.md) — *placeholder; usage guide
  not written yet.*

## 6. METIS App: Invite

- [Signup](web/invite/signup.md) — *placeholder; the invitee usage guide is not written yet.*

## API reference

The OpenAPI schema is generated and served live; these playbooks cover conventions, auth,
and narrative that the schema doesn't.

- [API overview](api/API.md) — surfaces, base URLs, and where to find the live schema.
- [Core API playbook](api/PLAYBOOK.md)
- [Coherence API playbook](api/coherence-PLAYBOOK.md)
- [Extension API playbook](api/extension-PLAYBOOK.md)
- [Conversation JSON fields](api/CONVERSATION_JSON_FIELDS.md) — `infos`/`config` field
  ownership on conversations.
