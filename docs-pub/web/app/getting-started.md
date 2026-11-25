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

Activity is the feed of what's been happening (notes, updates) for your
current Focus. On the Gathering site you land on the **welcome page** instead, which shows
your camp's chapters and the teams you are on; Activity is in the menu. With no Focus selected ("All"), it spans everything you can see; with a Focus
set, it's scoped to that holon.

## The organiser's welcome page

If you are on the team of a Local Gathering that is not marked **Past**, the Gathering
site's welcome page becomes that gathering's page. Its address carries your Focus
(`/<gathering>/welcome/`), so you can bookmark or share it.

**Which gathering** is decided by your Focus: a gathering you organise, or anything inside
it such as one of its camps, shows that gathering. A Focus on a gathering you do not
organise shows none of the blocks below. With **All**, you see your one active gathering;
if you are on the team of several, the page asks you to **Pick a gathering**.

The page shows, from the top:

- **The band** — the gathering's name, place and dates, a welcome, how many days until
  the village opens, and three counts: its camps, the camps with every chapter filled in,
  and the people on the gathering's journeys.
- **Your follow-ups due** — up to five people on the gathering you are responsible for
  whose follow-up date has come, oldest first, as the same rows as the gathering's People
  list. Edit one in place; when its date moves on, it leaves the list without a reload.
- **The team this week** — who moved how many people to which step in the last seven
  days.
- **What the team is working on** — a card for each person on the team (you first): the
  people they are responsible for, by journey and step, and how many follow-ups are
  overdue. Everyone on the team sees every card.
- **People on their way** — the gathering's three biggest journeys, each step with its
  count and how many are yours. A journey's name opens its board.
- **This week** — the gathering's week, Monday to Sunday in the gathering's own timezone
  (UTC when it has none), today marked, then **Coming up**. Each day shows how many
  follow-ups each person on the team has due that day (yours filled in, a teammate's
  outlined; today's count of yours opens **Your follow-ups due**), the open Audax actions
  held by someone on the team that you can see (each with its quest's name, highest
  priority first; shown if you use Audax), and the day the gathering opens and closes.
  Follow-ups and actions whose date has passed move to today: one line per person, with
  how many are late and the earliest date. **Coming up** lists the next five actions and
  gathering dates after Sunday, up to 30 days ahead. It updates when you change a
  follow-up in **Your follow-ups due**. On a phone the days stack one under another, and
  the days already past are left out (anything late is on today).
- **The camps** — every camp's hexagon and how many of its chapters are filled in.

Parts METIS cannot show yet (what changed since your last visit, short runs through your
follow-ups, and tickets) show in their place as **Coming soon**.

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
