# Camps & Local Gatherings

The Gathering app manages two holon classes — **Camps** and **Local Gatherings** — as part of
running The Gathering. This is the usage guide; the field *schema* behind a camp's custom
fields is documented separately in [Additional fields](../metis/info-fields.md).

Everything here is scoped by your current **Focus** — see
[Focus](../../web/app/focus-and-scoping.md). New to the shell? Start with
[Getting started](../../web/app/getting-started.md).

---

## Access

The Gathering nav group appears only for users with **Gathering access** — superusers and
members of the `gathering_users` group. Being staff or a broad editor does **not**
automatically grant it (it's a deliberate opt-in). If you don't see the Gathering group, ask
an administrator to add you. See [Access & permissions](../../core/access-and-permissions.md).

Within the group, the **Camps** and **Gatherings** nav items each appear only when your
current Focus actually has camps / local gatherings under it.

## Creating a Local Gathering vs. a Camp

Each has its own creation page, reached from the **+** button on its list. Both create the
new holon under your current **Focus**, so with no Focus set the page tells you to pick one
first. They differ over the journey:

- **Local Gathering** — the journey is optional. If the Focus holon offers relationship
  journeys you may pick one, and the new gathering is related to its parent on that journey;
  choose **— No journey —** and it is simply created under the Focus. **Responsible** and
  **Follow-up Date** belong to that relationship, so they are only saved when you pick a
  journey.
- **Camp** — has a few more requirements:
  - The Focus holon must have a **configured relationship journey** — the journey new camps
    are placed on. Without one, creation is blocked with a message to configure it.
  - You choose the **camp class** (a camp subclass — different events use their own camp
    subclass so each can carry its own fields), a **journey** and starting **step**, a
    **responsible** person (from the Focus holon's active team), and an optional **follow-up**
    date.

Anyone who can edit the Focus holon can create a camp or a Local Gathering under it — a
broad editor, or a member of its team (the same people who can add an event from the
holon's own Events section). Creating a Local Gathering also needs **Gathering access**.
See [Access & permissions](../../core/access-and-permissions.md).

## Camp info fields in practice

A camp's custom **Additional fields** (format, capacity, theme, videos, photo slideshows, …)
are defined on the camp *class* and filled in per camp on its detail page. Fields marked
public show on the camp's public page. The how-to is in
[Additional fields](../metis/info-fields.md); the class/config model is in
[Holons and classes](../metis/holons-and-classes.md).

## A camp's public page

Each published camp has its own page on the public site, in the same look as its
gathering's page. From top to bottom it shows:

1. **The opening.** On the left: "A camp at" the gathering, with its dates and place; the
   camp's name; its "why" (the camp's reason for being, when the camp class has a public
   field for it); then its description, themes and links. On the right: the camp's video,
   its hosts with their photos and short bios, the organisation that brings it, and a
   **Get your ticket** button. On a phone the right-hand column comes between the name and
   the description.
2. **Other public fields** the opening does not already show, such as photos.
3. **Each organisation** behind the camp, headed "Brought by", with its whole description
   and its links.
4. **The programme, day by day**: the camp's public experiences, one line each, time first,
   grouped under the days they happen. Only days with something on are shown; experiences
   without a day come last. A link opens the camp's full programme.

The ticket button uses the camp's own ticket link when it has a public one, and otherwise
the gathering's. It is not shown once the gathering is over. When the gathering itself is
not published, the camp page does not show its dates, place or ticket link.

**Upright or wide video.** A camp's video is drawn tall and narrow, the shape of a phone
held upright, because most camps film that way. If your camp's video is a landscape film,
open the camp in the CRM and set **Video shape** to **Wide**: the page then draws it wide
and gives the right-hand column more room. Leave it empty for an upright video. The setting
is never shown on the public page itself.

## List and kanban views

Both **Camps** and **Gatherings** offer a list view and a **kanban** view, scoped to your
Focus:

- The **list** has column controls (Links, Journey, Responsible, Follow Up, Info) and
  filters; applied filters live in the URL so the view is bookmarkable and shareable.
- The **kanban** columns are journey steps; drag a card to move that camp/gathering to a
  different step (the same as changing its step on the detail page).

## Journeys and step progression

Camps and local gatherings sit on **journeys** like other holons — each has a current step
that tracks where it is in its lifecycle. Move them through steps from the kanban board or
the detail page. See [Journeys](../../core/JOURNEY.md) for the underlying model.

## A note on the Calendar

The shell **Calendar** is a **follow-up agenda**, not an events-by-date calendar: it lists
flows (memberships and relationships) that have a **follow-up date**, grouped into Overdue /
Today / Tomorrow / This Week / Next Week / Later / No Date. So a camp appears on the Calendar
when its flow has a **follow-up date set** (for example, the follow-up you set when creating
it) — it does **not** plot camps by their event dates. Use the follow-up date to keep a camp
on your radar; use the Camps list/kanban to see them all by status.

## Settings

The Gathering settings cards (for example, **Locations** and **Spheres**) appear on the
Settings page for users with Gathering access, and let you manage the shared tags camps and
gatherings can be labelled with.
