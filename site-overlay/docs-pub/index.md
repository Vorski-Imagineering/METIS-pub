# METIS Documentation

Public documentation for METIS — the platform behind The Gathering. This covers the core
concepts you configure and work with, the apps built on top of them, IRIS (the
conversation-publishing pipeline), and the REST API.

!!! info "How this tree is maintained"

    The pages below are published automatically from the METIS source repository — this is
    the user- and integrator-facing manual. Internal engineering and operations docs live
    elsewhere and are not published here. This index page is the one exception: it is
    maintained alongside the site, in `site-overlay/`.

## Start here

<div class="grid cards" markdown>

-   :material-compass-outline: **[Getting started](web/app/getting-started.md)**

    The orientation tour — the shell, the sidenav, and where everything lives.
    The fastest way to get your bearings.

-   :material-crosshairs-gps: **[Focus & scoping](web/app/focus-and-scoping.md)**

    How the currently focused holon scopes what you see and do. The one concept
    every other guide assumes.

-   :material-graph-outline: **[Concepts diagram](core/concepts-diagram.md)**

    A visual map of how holons, persons, classes, journeys, and memberships fit
    together, with a worked example.

</div>

## Core

The shared platform: the CRM, the structural model, and access.

| Page | What it covers | Read it if |
|---|---|---|
| [Working with people & orgs](metis_apps/metis/people-and-orgs.md) | Day-to-day CRM: finding, adding, and tracking people and organisations; journeys, kanban, mentions, relationships. | You manage contacts and want to track their progress. |
| [Apps](web/app/apps.md) | METIS is composed of independent apps, and different holons use different ones. | You wonder why features differ between holons. |
| [Holons and classes](metis_apps/metis/holons-and-classes.md) | What holons are, how classes work, and how a class's configuration decides what a holon shows and can do. | You want to know how records are typed, or you're setting up a new class. |
| [Additional fields](metis_apps/metis/info-fields.md) | Defining custom structured fields on a holon class and filling them in per holon. | You need to add or fill custom fields on your records. |
| [Journeys](core/JOURNEY.md) | The progression model behind kanban-style pipelines, and how to create new journeys. | You want to model stages of a relationship or process. |
| [Access & permissions (user view)](core/access-and-permissions.md) | Plain-language answer to why you can — or can't — see and do certain things. | Something is hidden or greyed out and you want to know why. |
| [Permissions and roles](core/PERMISSIONS.md) | The full model: groups, config-flag permissions, public visibility. | You administer access across the system. |
| [Using the Chrome extension](extension/using-the-extension.md) | Capturing LinkedIn profiles and companies straight into METIS from your browser. | You want LinkedIn people and companies in METIS without manual entry. |

## Coherence

Coherence covers three distinct things: the Events/Conversations side of the CRM,
**IRIS** — the pipeline that turns a recorded conversation into published media — and
**CoCo**, a chatbot that answers from your conversation content.

| Page | What it covers | Read it if |
|---|---|---|
| [Events & conversations](metis_apps/coherence/events-and-conversations.md) | What a Coherence Event is, how to create one, where Conversations come from, and the cal.com booking webhook. | You're setting up events or wondering how conversations get into METIS. |
| [CoCo agent](metis_apps/coherence/coco-agent.md) | What CoCo is, how to talk to it, and how its knowledge base stays current. | You want to use the chatbot or understand where its answers come from. |

### IRIS

| Page | What it covers | Read it if |
|---|---|---|
| [What IRIS does](metis_apps/coherence/iris/user-benefit-iris.md) | The value and workflow overview for the publishing pipeline. *Start here.* | You want to know what IRIS is for and what it produces. |
| [Using IRIS — walkthrough](metis_apps/coherence/iris/using-iris.md) | The click-path for staff running a conversation through the pipeline. | You're operating IRIS and need to know what to click, and when. |
| [Participant review guide](metis_apps/coherence/iris/participant-approval.md) | Written for participants asked to review and approve what gets published. | You've been asked to approve a conversation, or you support people who were. |
| [Job reference](metis_apps/coherence/iris/jobs/index.md) | One page per pipeline stage — what it does, depends on, reads and writes, and how to tell it's working. Includes the [prompt authoring guide](metis_apps/coherence/iris/jobs/content-generator-prompts.md) and [YouTube setup](metis_apps/coherence/iris/jobs/youtube-uploader-setup.md). | A stage is misbehaving, you want to change how IRIS writes content, or you're connecting a YouTube channel. |

## The Gathering

| Page | What it covers | Read it if |
|---|---|---|
| [Camps & local gatherings](metis_apps/gathering/camps-and-gatherings.md) | Running The Gathering's camps and local gatherings. | You're organising a camp or a local gathering. |
| [Experiences (camp programme)](metis_apps/gathering/experiences.md) | Creating experiences, configuring their fields, and how people, publishing, and the public programme pages work. | You're building a camp's programme. |
| [Experience configuration](metis_apps/gathering/experience-config.md) | The administrator checklist — classes, programme journey, publication flags, artwork libraries — with a worked example. | You're configuring the programme rather than filling it in. |
| [Experience images — how-to](metis_apps/gathering/experience-images-howto.md) | Step-by-step for giving experiences good artwork. | Your programme pages look bare and you want images on them. |

## Other apps

| Page | What it covers | Read it if |
|---|---|---|
| [Audax — quests & missions](metis_apps/audax/quests-and-missions.md) | The Audax quests and missions workflow. **Placeholder — guide not written yet.** | You work with Audax (and can wait for the guide). |
| [Outreach — LinkedIn](metis_apps/outreach/linkedin-outreach.md) | LinkedIn imports and Outreach campaigns. **Placeholder — guide not written yet.** | You run LinkedIn outreach through METIS. |
| [Invite — signup](web/invite/signup.md) | The invitee signup experience. **Placeholder — guide not written yet.** | You want to understand the invite and signup flow. |

## API reference

The OpenAPI schema is generated and served live; these playbooks cover the conventions,
auth, and narrative that the schema doesn't.

| Page | Surface | Read it if |
|---|---|---|
| [The METIS API](api/API.md) | `/api/v1/` | You're integrating with METIS from outside. **This is the one you want.** |
| [App API playbook](api/PLAYBOOK.md) | `/api/` | You're working with the endpoints METIS's own apps expose — agent records and integration webhooks. Not a version of `/api/v1/`. |
| [Coherence API playbook](api/coherence-PLAYBOOK.md) | `/api/` (Coherence) | You're calling the Coherence endpoints specifically. |
| [Outreach API playbook](api/outreach-PLAYBOOK.md) | `/api/` (Outreach) | You're calling the Outreach endpoints specifically. |
| [Conversation JSON fields](api/CONVERSATION_JSON_FIELDS.md) | Reference | You need the meaning and ownership of `infos`/`config` fields on conversations. |
