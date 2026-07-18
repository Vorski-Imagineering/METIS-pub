# Getting Started — Navigating METIS

This orients a brand-new user in the METIS shell. Other guides link back here for the
navigation and Focus vocabulary rather than re-explaining it.

METIS is the platform The Gathering runs on: a CRM for people and organisations, plus
product apps built on top of it — **Coherence** (conversations and the IRIS publishing
pipeline), **The Gathering** (camps and local gatherings), **Audax** (quests and missions),
and **Outreach** (LinkedIn outreach). What you see depends on your access; not everyone has
every app.

> Some UI details below (exact labels, icons) are described from the app's structure. If
> anything doesn't match what you see, trust the app — layouts evolve.

---

## The sidenav

Everything is reached from the **sidenav** on the left. Top to bottom:

- **Focus selector** — at the very top: a holon logo (or a globe for "All") next to a
  **Focus** label and a dropdown. This sets your current scope and is important enough to
  have [its own guide](focus-and-scoping.md).
- **Search** — global search across the app (see below).
- **Activity** and **Calendar** — these are *focus-scoped* (bound to your current Focus,
  shown with a left accent line).
- **People** and **Orgs** — the core CRM lists. They appear only when your current Focus
  actually has people or organisations under it.
- **Per-app nav groups** — Coherence, Gathering, Audax, Outreach, etc. Each group only
  appears if you have access to that app *and* your current Focus has the relevant records.
- **Footer** — **Admin** (Django admin, staff only), **Report** (report a bug or request a
  feature — opens in a new tab), **Settings**, and **Logout**.

Because most nav items are focus-scoped, switching your Focus changes where these links take
you and which of them appear at all. That's covered in the [Focus guide](focus-and-scoping.md).

## Search

Search finds People and Holons (organisations, camps, events, …) by name. Results are
grouped by kind; pick one to jump to its detail page.

## Activity

Activity is your landing page — the feed of what's been happening (notes, updates) for your
current Focus. With no Focus selected ("All"), it spans everything you can see; with a Focus
set, it's scoped to that holon.

## Calendar

The Calendar shows dated items (for example, camp and gathering dates). It offers a list
view and a calendar view; what populates it depends on your current Focus.

## Settings

Settings holds per-app configuration cards. Which cards you see depends on your access — for
example, the Journeys settings card and the Chrome extension download card appear only for
users with broad edit rights. See [Access and permissions](../../core/access-and-permissions.md)
for why a card or nav group might not be visible to you.

## Reporting a bug or requesting a feature

The **Report** item in the footer opens a form for bugs and feature requests. Use it
whenever something's broken or missing.

---

## Where to go next

- [Focus: the holon scoping model](focus-and-scoping.md) — the one concept everything else
  assumes.
- [Working with people & orgs](../../metis_apps/metis/people-and-orgs.md) — the core CRM
  workflow.
- [Access and permissions](../../core/access-and-permissions.md) — why you can (or can't)
  see certain things.
