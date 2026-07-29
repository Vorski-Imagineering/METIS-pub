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

IRIS is the pipeline that turns a recorded conversation into published media. It has its own
[documentation index](metis_apps/coherence/iris/README.md) — start there if you're not sure
which page you need.

#### 2.2.1 What IRIS does

[What IRIS does](metis_apps/coherence/iris/what-iris-does.md) is the plain-English overview:
what goes in, what comes out, and where people stay in charge.

*Read — if you want to understand what IRIS is for and what it produces.*

#### 2.2.2 How IRIS works

[How IRIS works](metis_apps/coherence/iris/how-iris-works.md) explains the machinery: a
conversation sits on a step, each step's job runs on a timer, and each run either finishes and
moves the conversation on, waits quietly, or fails with a note. It also covers why IRIS is
built that way. *(The one page worth reading before the others.)*

*Read — if you want to understand why a conversation is or isn't moving, before you need
to.*

#### 2.2.3 Using IRIS — staff walkthrough

[Using IRIS](metis_apps/coherence/iris/using-iris.md) is the click-path for staff running a
conversation through the pipeline: which panel, which button, at which stage.

*Read — if you're operating IRIS and need to know exactly what to click and when.*

#### 2.2.4 Participant review guide

[Participant review guide](metis_apps/coherence/iris/participant-review.md) is written for the
people asked to review and approve what's published about them. Safe to forward.

*Read — if you've been asked to approve a conversation, or you support people who
have.*

#### 2.2.5 Troubleshooting

[Troubleshooting](metis_apps/coherence/iris/troubleshooting.md) covers why a conversation isn't
moving, what error notes mean, and what resetting a step does — and can't undo.

*Read — if something is stuck, red, or missing.*

#### 2.2.6 The pipeline steps

[The pipeline steps](metis_apps/coherence/iris/steps/README.md) is one reference page per stage
of the pipeline: what it does, what it needs, what it produces, and step-specific
troubleshooting. The index groups the steps into the order a journey runs them.

*Read — if you're designing a journey, or you need to understand one stage deeply.*

#### 2.2.7 Configuration guides

[Writing prompts](metis_apps/coherence/iris/writing-prompts.md) covers customising the AI
instructions that generate titles, descriptions, LinkedIn copy and quotes, including injecting
live conversation context. [YouTube setup](metis_apps/coherence/iris/youtube-setup.md) covers
connecting a journey to a YouTube channel, and the Google account permissions that most often
trip people up.

*Read — if you're changing how IRIS writes, or wiring up YouTube publishing.*

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

Not sure which surface you want? [`api/API.md`](api/API.md) is a short index over all
of them.

### 7.1 The METIS API — `/api/v1/`

[The METIS API playbook](api/v1-PLAYBOOK.md) is the open API for external systems
integrating with METIS: authentication, the access model, and every endpoint,
alongside the live schema.

*Read — if you're integrating with METIS from outside. This is the one you want.*

### 7.2 Public API — `/public/`

[Public API playbook](api/public-PLAYBOOK.md) covers `/public/`, a fully open,
unauthenticated read-only JSON projection of exactly the data already public on the
site's `/view/*` pages — for frontends (React apps, embeds) to consume as JSON.

*Read — if you're building a view (React or otherwise) over METIS's public site data
and don't need to log in or hold a token.*

### 7.3 App API playbook — `/api/`

[App API playbook](api/PLAYBOOK.md) covers the separate `/api/` surface, where METIS's own
apps expose service endpoints — agent records and integration webhooks.

*Read — only if you're working with those app endpoints; `/api/v1/` is not documented
here and is not a version of this surface.*

### 7.4 Coherence API playbook

[Coherence API playbook](api/coherence-PLAYBOOK.md) covers the Coherence-specific API
conventions and narrative. It's the counterpart playbook for Coherence endpoints.

*Read — if you're working with the Coherence API endpoints specifically.*
