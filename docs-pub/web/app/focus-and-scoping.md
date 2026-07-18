# Focus: The Holon Scoping Model

**Focus** is the single most load-bearing idea in METIS. It scopes nearly every list, shapes
almost every URL, and gates what you can create. Understanding it makes the rest of the app
make sense. This page is referenced by every other guide, so it's explained here once, in
full.

New to the shell? Read [Getting Started](getting-started.md) first for the sidenav
vocabulary.

---

## What a Focus holon is

Your **Focus** is the holon (an organisation, camp, event, …) you're currently scoped to —
your "I'm working within this" setting. The alternative is **"All"** (unfocused), where you
see everything you have access to, across all holons.

The Focus selector sits at the top of the sidenav: the focused holon's logo (or a **globe**
for "All") next to the **Focus** label and a dropdown.

## How to switch Focus

Open the Focus dropdown. It lists the holons **you're a member of**, plus — if you're
allowed to unfocus — an **All** option (the globe). Pick one to focus on it; pick **All** to
clear Focus.

Some users (broad editors) can always clear to "All"; others are scoped and stay within
their own holons. If you don't see an "All" option, your account is scoped to your holons by
design.

## What changes when you switch

Switching Focus re-scopes the app to that holon:

- **Activity** and **Calendar** show that holon's items.
- **People** and **Orgs** list the people and organisations under that Focus — and these nav
  items only appear when the Focus actually has people/holons.
- **App sections** (Camps & Gatherings, Quests & Missions, Conversations, …) list records
  under that Focus, and each app's nav group only shows when the Focus has those records.

In **"All"** mode you see everything you have access to, unscoped.

## Why the Focus lives in the URL

Your Focus is carried **in the page URL** as a slug — for example `/<org-slug>/people/`
rather than just `/people/`. This is deliberate and has real benefits:

- **Bookmarking** a focused view reopens it with the same scope.
- **Sharing a link** with a teammate resolves to the identical view for them (subject to
  their access).
- **Reloading** the page keeps your scope instead of dropping it.

Because the URL is the source of truth for Focus, the app keeps it in sync as you navigate:
change Focus and the page re-projects itself onto its canonical `/<slug>/...` address.

## Bare vs. focused URLs

The same page exists at both `/<route>` and `/<focus-slug>/<route>`. A link that carries an
org slug is a *focused* link; one without is the *bare* (unfocused / "All") version. Seeing a
link with or without a slug is expected — it's not a bug, it just reflects whether a Focus
was set when the link was made. Opening a bare focusable page redirects you to its canonical
focused address when a Focus applies.

## Creating things while focused

Focus also determines **where new things are created**. When you create a record that lives
under a holon (a camp, a quest, a mission, …) while focused, it's parented to your current
Focus automatically. If a create flow needs a parent and you have **no Focus set**, either
set a Focus first or expect the flow to ask you to — creating a child holon with nothing to
attach it to doesn't make sense.

## Focus vs. permissions

These are two different things and both matter:

- **Focus** controls *scope* — which records you're currently looking at.
- **Permissions** control *visibility and rights* — which apps and nav items you can reach at
  all, and what you can do with them.

A nav group can be missing because you lack access to that app (permissions) **or** because
your current Focus has none of those records (scope). See
[Access and permissions](../../core/access-and-permissions.md) to tell the two apart.

## Common gotchas

- **"Why don't I see this record?"** — usually the wrong Focus is selected. Check the Focus
  chip at the top of the sidenav; switch to the right holon or to "All".
- **"Why can't I create this?"** — often no Focus is set when the flow needs a parent holon.
  Set a Focus and try again.
- **Lost scope after being away** — if your session timed out and you logged back in, your
  Focus may have reset; the sidenav chip tells you your current Focus at a glance.
