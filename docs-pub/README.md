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

### 1.1 Getting started — navigating METIS

[Getting started — navigating METIS](web/app/getting-started.md) is the orientation tour: the
shell, the sidenav, and where everything lives. It is the fastest way to get your bearings
before diving into any specific feature. *(Start here.)*

*Read — if you're new to METIS and want to know where things are and how to move
around.*

### 1.2 Focus: the holon scoping model

[Focus: the holon scoping model](web/app/focus-and-scoping.md) explains how the currently
focused holon scopes what you see and do across the whole app. It is the one concept every
other guide assumes you understand.

*Read — if pages seem to show a different slice of data than you expected, or you
want to understand what "focus" controls.*

### 1.3 Working with people & orgs

[Working with people & orgs](metis_apps/metis/people-and-orgs.md) covers the day-to-day CRM:
finding, adding, and tracking people and organisations. It also walks through journeys,
kanban, mentions, and relationships between records.

*Read — if you want to know how to manage contacts and organisations and track their
progress.*

### 1.4 Access & permissions (user view)

[Access & permissions (user view)](core/access-and-permissions.md) is the plain-language
answer to why you can — or can't — see and do certain things. It stays at the everyday level
rather than the full permission model.

*Read — if something is hidden or greyed out and you want to understand why.*

### 1.5 Using the Chrome extension

[Using the Chrome extension](extension/using-the-extension.md) shows how to capture LinkedIn
profiles and companies straight into METIS from your browser. It covers installing the
extension and the capture workflow.

*Read — if you want to pull LinkedIn people and companies into METIS without manual
data entry.*

### 1.6 Apps

[Apps](web/app/apps.md) explains that METIS is made of independent pieces of functionality
called apps, and that different holons use different apps. It sets up the vocabulary the rest
of the docs use when they refer to a specific app.

*Read — if you want to understand how METIS is composed and why features differ
between holons.*

### 1.7 Holons and classes

[Holons and classes](metis_apps/metis/holons-and-classes.md) defines what holons are, how
classes work, and how a class's configuration decides what each holon shows and can do. This
is the structural backbone of how data is organised.

*Read — if you want to understand how records are typed and configured, or you're
about to set up a new class.*

### 1.8 Holon Additional Fields

[Holon Additional Fields](metis_apps/metis/info-fields.md) covers defining custom structured
fields on a holon class and filling in their values per holon. It's the practical companion to
the holons-and-classes concept — for example, configuring custom information for a camp in
The Gathering (dates, capacity, location) as additional fields on the camp holon class.

*Read — if you need to add or fill in custom fields on your records.*

### 1.9 Journeys

[Journeys](core/JOURNEY.md) describes the progression model for tracking where a person or
holon sits in a relationship, and how to create new journeys. It's the mechanism behind
kanban-style pipelines.

*Read — if you want to model and track stages of a relationship or process.*

### 1.10 Permissions and roles

[Permissions and roles](core/PERMISSIONS.md) is the full model: groups, config-flag
permissions, and public visibility. It goes deeper than the user-view access guide for people
who administer access.

*Read — if you're configuring who can access and edit data across the system.*

### 1.11 Concepts diagram

[Concepts diagram](core/concepts-diagram.md) is a visual, plain-English map of how Holons,
Persons, Classes, Journeys, Memberships, and Holon Relationships fit together, with a worked
example. It's the "big picture" companion to the individual concept docs above.

*Read — if the individual concept pages make sense on their own but you want to see how
they connect, or you're brand new and want the shape of the model before the details.*

## 2. METIS App: Coherence

Coherence covers three distinct things: the Events/Conversations side of the CRM, **IRIS** —
the pipeline that turns a recorded conversation into published media, and **CoCo** — a
chatbot that answers from your conversation content.

### 2.1 Coherence Conversations

#### 2.1.1 Events & Conversations

[Events & Conversations](metis_apps/coherence/events-and-conversations.md) explains what a
Coherence Event is, how to create one, and where Conversations come from. It also covers
wiring up the cal.com booking webhook.

*Read — if you're setting up events or want to understand how conversations get into
METIS.*

### 2.2 IRIS

#### 2.2.1 What IRIS does

[What IRIS does](metis_apps/coherence/iris/user-benefit-iris.md) gives the value and workflow
overview for the conversation-publishing pipeline. It's the high-level picture before any of
the operational detail. *(Start here.)*

*Read — if you want to understand what IRIS is for and what it produces.*

#### 2.2.2 Using IRIS — conversations walkthrough

[Using IRIS — conversations walkthrough](metis_apps/coherence/iris/using-iris.md) is the
click-path for staff running a conversation through the pipeline. It follows the workflow step
by step.

*Read — if you're operating IRIS and need to know exactly what to click and when.*

#### 2.2.3 Participant approval guide

[Participant approval guide](metis_apps/coherence/iris/participant-approval.md) is written for
conversation participants asked to review and approve what's published. It explains the
approval request and what happens next.

*Read — if you've been asked to approve a conversation, or you support people who
have.*

#### 2.2.4 Job Steps

[Job Steps](metis_apps/coherence/iris/jobs/README.md) is one reference page per IRIS pipeline
stage: what each does, what it depends on, what it reads and writes, and how to tell it's
working. It's the detailed operator reference for the pipeline internals — the
[Content Generator](metis_apps/coherence/iris/jobs/content-generator.md) page links out to a
dedicated
[prompt authoring guide](metis_apps/coherence/iris/jobs/content-generator-prompts.md) for
customising the AI instructions and injecting live conversation context, and the
[YouTube Uploader](metis_apps/coherence/iris/jobs/youtube-uploader.md) page links out to a
dedicated
[YouTube uploader setup guide](metis_apps/coherence/iris/jobs/youtube-uploader-setup.md) for
connecting a journey step to a YouTube channel (GCP OAuth client, per-step authorisation).

*Read — if a pipeline stage isn't behaving and you need to understand exactly what it
does, you want to change how IRIS writes content, or you're setting up YouTube publishing.*

*(2.2.5 IRIS Pipeline Testing Guide is an internal engineering doc, not published here.)*

### 2.3 CoCo Agent

#### 2.3.1 CoCo Agent

[CoCo Agent](metis_apps/coherence/coco-agent.md) explains what CoCo is, how to talk to it, and
how its knowledge base stays current. It answers questions from your conversation content.

*Read — if you want to use the chatbot or understand where its answers come from.*

## 3. METIS App: The Gathering

### 3.1 Camps & local gatherings

[Camps & local gatherings](metis_apps/gathering/camps-and-gatherings.md) covers running The
Gathering's camps and local gatherings. It's the app-specific guide for those event types.

*Read — if you're organising a camp or a local gathering.*

### 3.2 Experiences (camp programme)

[Experiences](metis_apps/gathering/experiences.md) covers a camp's programme: creating
experiences, configuring their fields (including icon-bearing select options), and how
people, related holons, publishing, and the public programme pages work.
[Experience configuration](metis_apps/gathering/experience-config.md) is the
administrator checklist — classes, programme journey, publication flags, and artwork
libraries — with a complete worked example.

*Read — if you're building or configuring a camp's programme.*

## 4. METIS App: Audax

### 4.1 Quests & missions

[Quests & missions](metis_apps/audax/quests-and-missions.md) will cover the Audax quests and
missions workflow. *(Placeholder; usage guide not written yet.)*

*Read — if you're working with Audax quests and missions (guide pending).*

## 5. METIS App: Outreach

### 5.1 LinkedIn outreach

[LinkedIn outreach](metis_apps/outreach/linkedin-outreach.md) will cover the Outreach app's
LinkedIn workflow. *(Placeholder; usage guide not written yet.)*

*Read — if you're running LinkedIn outreach through METIS (guide pending).*

## 6. METIS App: Invite

### 6.1 Signup

[Signup](web/invite/signup.md) will cover the invitee signup experience. *(Placeholder; the
invitee usage guide is not written yet.)*

*Read — if you want to understand the invite and signup flow (guide pending).*

## 7. API Reference

The OpenAPI schema is generated and served live; these playbooks cover conventions, auth,
and narrative that the schema doesn't.

### 7.1 The METIS API — `/api/v1/`

[The METIS API](api/API.md) is the open API for external systems integrating with METIS:
authentication, the access model, and every endpoint, alongside the live schema.

*Read — if you're integrating with METIS from outside. This is the one you want.*

### 7.2 App API playbook — `/api/`

[App API playbook](api/PLAYBOOK.md) covers the separate `/api/` surface, where METIS's own
apps expose service endpoints — agent records and integration webhooks.

*Read — only if you're working with those app endpoints; `/api/v1/` is not documented
here and is not a version of this surface.*

### 7.3 Coherence API playbook

[Coherence API playbook](api/coherence-PLAYBOOK.md) covers the Coherence-specific API
conventions and narrative. It's the counterpart playbook for Coherence endpoints.

*Read — if you're working with the Coherence API endpoints specifically.*

### 7.4 Conversation JSON fields

[Conversation JSON fields](api/CONVERSATION_JSON_FIELDS.md) documents `infos`/`config` field
ownership on conversations. It clarifies which fields belong to what and how they're used.

*Read — if you need to know the meaning and ownership of conversation JSON fields.*
