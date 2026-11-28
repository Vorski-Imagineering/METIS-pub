# Focus: The Holon Scoping Model

**Focus** is the single most load-bearing idea in METIS. It scopes nearly every list, shapes
almost every URL, and gates what you can create. Understanding it makes the rest of the app
make sense. This page is referenced by every other guide, so it's explained here once, in
full.

New to the shell? Read [Getting Started](getting-started.md) first for the strip, the
band and their tabs.

---

## What a Focus holon is

Your **Focus** is the holon (an organisation, camp, event, …) you're currently scoped to —
your "I'm working within this" setting, which the screen calls your **place**. Besides a
holon, there are two places that are not a holon:

- **You** — your own pages: Start, My actions and Outreach.
- **All** — everything you have access to, across all holons.

Both mean "no Focus". Which of the two you see depends on the page: your own pages show
You, every other page with no Focus shows All.

The place switcher sits at the left of the dark strip at the top of every page. It names
your place, with its picture (your own for You, a **globe** for All). Under the strip, the
band repeats the place's picture, kind and name, with the place's tabs.

## How to switch Focus

Open the place switcher. It lists **You** first, then **your places** (the holons you're a
member of), then **All** (the globe). Pick a holon to focus on it. Pick **All** to clear
Focus. Pick **You** to clear Focus and open your Start page.

From inside a place you can also go one level down: a record that is itself a holon (a
quest, a camp) opens as a card whose top row has a **Go in →** button. It makes that holon
your Focus and opens its Overview.

## METIS remembers your Focus

The Focus you choose in the switcher (or with **Go in →**) is remembered on your account,
not just in one browser: sign in on another device, or after a long time away, and you
start where you left off. Choosing **All** or **You** is remembered too, as no Focus.

Only the switcher and **Go in →** change what is remembered. Following someone's link to a focused page
shows you that page, but your next sign-in still starts on the Focus you chose yourself.

When you have never chosen a Focus, METIS picks a starting Focus for you when you sign in:
the gathering whose team you are on, if there is exactly one that is not over (marked
**Past**), or otherwise the one holon whose team you are on. If you are on several teams and
none of these settles it, you start on **All**. Either way it is only a start: choose
another Focus and that is what is remembered. With no Focus, you land on You › Start.

## What changes when you switch

Switching Focus re-scopes the app to that holon, and the band's tabs follow it:

- **Overview** is the holon's own page.
- **Feed** and **Calendar** show that holon's items.
- **People** and **Organisations** list the people and organisations under that Focus — and
  these tabs only appear when the Focus actually has people/holons.
- **App sections** (Camps, Gatherings, Quests, Conversations, …) list records under that
  Focus, and each tab only shows when the Focus has those records.

In **All** you see everything you have access to, unscoped, with the same tabs except
Overview. **You** has its own tabs: Start, My actions and Outreach. Outreach lists the
people and organisations you are responsible for, from every place.

## Why the Focus lives in the URL

Every page address says **whose page it is, then the tab**:

| Address | Whose page |
|---|---|
| `/me/`, `/me/actions/`, `/me/outreach/`, `/me/profile/` | Home: your own |
| `/all/connections/`, `/all/outreach/`, … | All: no place, everything you may see |
| `/<place>/`, `/<place>/about/`, `/<place>/connections/`, `/<place>/calendar/`, … | A place, by its readable name (its slug) |
| `/<place>/<holon>/`, `/<place>/<holon>/about/` | A holon opened inside a place (a quest in its organisation) |
| `/person/<number>/`, `/<place>/person/<number>/` | A person, on their own or opened inside a place |
| `/settings/` | Your own settings: your account |
| `/all/settings/`, `/all/settings/<page>/` | The system's settings (journeys, classes, apps, agents, …) |

This is deliberate and has real benefits:

- **Bookmarking** a page reopens it with the same place.
- **Sharing a link** with a teammate opens the identical view for them (subject to
  their access).
- **Reloading** keeps the place, even if you chose another place in a different tab.

Changing Focus in the switcher opens the new place's own address. Addresses used before
this layout (such as `/core/people/` or `/welcome/`) no longer open anything: update any
bookmarks you kept.

## Creating things while focused

Focus also determines **where new things are created**. When you create a record that lives
under a holon (a camp, a quest, a mission, …) while focused, it's parented to your current
Focus automatically. If a create flow needs a parent and you have **no Focus set**, either
set a Focus first or expect the flow to ask you to — creating a child holon with nothing to
attach it to doesn't make sense.

## Focus vs. permissions

These are two different things and both matter:

- **Focus** controls *scope* — which records you're currently looking at.
- **Permissions** control *visibility and rights* — which apps and tabs you can reach at
  all, and what you can do with them.

A tab can be missing because you lack access to that app (permissions) **or** because
your current Focus has none of those records (scope). See
[Access and permissions](../../core/access-and-permissions.md) to tell the two apart.

## Common gotchas

- **"Why don't I see this record?"** — usually the wrong Focus is selected. Check the place
  switcher at the top left; switch to the right holon or to **All**.
- **"Why can't I create this?"** — often no Focus is set when the flow needs a parent holon.
  Set a Focus and try again.
- **A different scope after signing in** — you start on the Focus you last chose in the
  switcher, even if you were browsing another holon through a link before you signed out.
  The place switcher and the band tell you your current Focus at a glance.
