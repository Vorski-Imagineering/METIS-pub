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

They're created differently:

- **Local Gathering** — created through the standard holon-creation flow, like any other
  organisation-style holon.
- **Camp** — has its own dedicated creation flow with a few requirements:
  - You must have a **Focus set** — a camp is created under your current Focus holon. With no
    Focus, the create page tells you to pick one first.
  - The Focus holon must have a **configured relationship journey** — the journey new camps
    are placed on. Without one, creation is blocked with a message to configure it.
  - You choose the **camp class** (a camp subclass — different events use their own camp
    subclass so each can carry its own fields), a **journey** and starting **step**, a
    **responsible** person (from the Focus holon's active team), and an optional **follow-up**
    date.

Creating a camp needs holon-create permission (a broad-editor action) — see
[Access & permissions](../../core/access-and-permissions.md).

## Camp info fields in practice

A camp's custom **Additional fields** (format, capacity, theme, videos, photo slideshows, …)
are defined on the camp *class* and filled in per camp on its detail page. Fields marked
public show on the camp's public page. The how-to is in
[Additional fields](../metis/info-fields.md); the class/config model is in
[Holons and classes](../metis/holons-and-classes.md).

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
