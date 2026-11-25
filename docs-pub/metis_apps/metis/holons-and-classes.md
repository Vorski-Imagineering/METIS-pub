# Holons and Classes

This guide explains two of the core ideas in METIS — **holons** and their **classes** — and
how a class's configuration decides what each holon shows and can do. It is written for
admins and power users setting things up, not developers. No code required.

For the deep dive on one specific piece of class configuration — custom "additional fields" —
see [Additional fields](info-fields.md).

---

## What a holon is

A **holon** is the general building block METIS uses for anything that isn't a person: an
organisation, an event, a camp, a local gathering, a domain, and so on. People are attached
*to* holons (as team members, participants, contacts…), but the holon itself is the entity
that has a detail page, relationships, journeys, and its own information.

Holons are arranged in a **containment tree**: a camp can sit inside a local gathering, which
sits inside a domain. This is the "which holon is inside which" structure you see when you
browse children and subtrees.

Every holon also has a **lifecycle stage** of its own: Draft, Live or Retired. Holons that
existed before stages were introduced are all Live, and a newly created holon starts Live.
Nothing uses the stage yet: it does not change what is listed, published or who can see a
holon. Staff can see it, read-only, in the holon's admin page.

---

## What a class is

Every holon has a **class**. The class is what decides how the holon behaves and what appears
on its page — a Camp looks and behaves differently from an Organisation because they are
different classes, not because anyone configured each holon by hand.

Classes themselves form a **family tree**. A specific class is a *kind of* a more general
one: `Portugal 2026 Camp` is a kind of `Camp`, which is a kind of the base holon class.
Configuration **flows down** this tree — a specific class inherits everything from its parent
and only needs to state what is *different*. So you can set something once on `Camp` and every
camp subclass gets it automatically.

> **Two different trees — keep them apart.**
>
> - **Class tree** — which *class* is a kind of which (`Portugal 2026 Camp` → `Camp`). Drives
>   what settings and journeys a holon inherits.
> - **Containment tree** — which *holon* sits inside which (a camp inside a local gathering).
>   Drives children and subtree listings.

### Grouping (abstract) classes

Some classes exist only to **group** other classes rather than to be used directly. For
example, an abstract `Event` class can sit above `Camp`, `Local Gathering`, and `Conversation`
so that a single "Events" view can reach all of them at once. You won't create holons of a
grouping class directly — but it's useful to know they're why one section can pull together
several different event kinds.

---

## What a class's configuration controls

A class's configuration is where the useful behaviour lives. The main things it decides:

| Setting | What it controls |
|---|---|
| **Detail-page sections** | Which sections appear on a holon's page — Description, Links, People/Team, Additional fields, Events, Conversations, Children, and more. This is the primary "what shows up" switch. |
| **Additional fields** | Custom structured fields for this class (format, capacity, theme, videos, photo slideshows…). Covered in depth in [Additional fields](info-fields.md). |
| **Link fields** | Which link inputs the profile offers (website, LinkedIn, …) and their icons. |
| **Allowed child classes** | Which kinds of holon can be created *underneath* a holon of this class — a listed class or any class under it. A holon gets only the child types its class lists, for staff too: if the list is empty, nothing can be created beneath it, and the page says which setting to change. A class with no list of its own inherits its parent's; a class that sets its own list does not get its parent's, because the own list replaces the inherited one. So to allow one more child class on a class, copy the list it shows now and add to it. |
| **Journeys** | Which journeys attach to this class — the progression tracks its holons and their relationships can move through. A journey can also be added to a *single* holon, on that holon's own page; it then applies to that holon only, on top of whatever its class offers. See [Journeys](../../core/JOURNEY.md). |
| **Label, icon, colour** | The display name (singular and plural), the class's icon, and its badge/pill colour. |

Because settings inherit down the class tree, most of these are set on a general class and
left alone on its subclasses — a subclass only overrides a setting when it genuinely needs to
differ.

---

## Detail-page sections in more detail

The list of sections a class shows is the setting you'll reach for most often. Some sections
are built in (Description, Links, People, Children, Additional fields), and some are
contributed by specific product areas — for example the **Events** section, the
**Conversations** section (visible to people with Coherence access), and Audax's **Quests** /
**Missions**.

A section appears on a holon's page when its class's configuration lists that section. Turning
a section on or off for a whole class is done by changing that class's configuration (see
below), not by editing each holon.

**Tabs.** A class can also split its page into tabs, each holding some of its sections: the
quest class, for example, has **Actions**, **Activity & comments**, **About** and **Team**. A
class with tabs shows only the sections its tabs list, one tab at a time, with the tab in the
page's address (`?tab=about`), and its page leads with the holon's description. Tabs are set in
the class's configuration (`tabs`, staff only) and pass down to subclasses like every other
setting. A page whose sections include **Activity & comments** shows its feed and comment box
there, and has no feed column beside the page. Every class without tabs keeps one long page.

### A holon's two views

Each holon has two pages. Its **view** is what the holon *is*: description, links, people,
events, and so on. Its **configuration** is what drives it and what has happened to it:
**Access** (who holds which capability, and the journey step that grants it), its
**relationship to the holon above it** and **where this appears** on the public site,
**Journeys**, invitation **Pages**, **Telegram**, **Import CSV** and **Change history**. The class decides
which sections go on which page, the same way it decides which sections appear at all; the
resolved lists are read in Settings → Classes (staff only).

**Change history** on the configuration page is a **Show history** button. It opens the
holon's history page: one list of everything that happened to it, newest first, under day
headings (*Today*, *Yesterday*, then dates), 50 lines to a page. Each line starts with who
did it and says in a few words what happened: a field they changed, a stage the holon or
one of its relationships moved to, or a shared note filed on the holon. Private notes
never appear, nor moves on relationships to holons you cannot see.

- **Only what changed.** A changed field shows its old and new value. A list of items,
  such as a camp's places, names each item that was added, removed or changed and what
  changed in it ("Yaxunah: map changed"), not the whole list twice. Press **details** on
  a line to see the full before and after.
- **Runs of edits fold.** Edits by the same person to the same field, each within an hour
  of the last, show as one line with a count and the time span ("(7 edits) 22:10–23:08").
  Every edit is still behind **details**; notes and stage moves never fold.
- **Filters.** **All**, **Edits**, **Stage moves** and **Notes** narrow the list to one
  kind, and **Who** to one person. The filters are in the page's address, so a reload or a
  shared link shows the same list.

A person's history (**History** on their configuration page) is the same list for that
person: their edits, their memberships' stage moves and the shared notes on them. Only
people who can edit the holon (or the person) see the button and the page.

A holon's **relationship to the holon above it** is on that configuration page, with the
journey and step it rests on. That relationship is usually what decides whether the holon
is on the public site, so **Where this appears** sits directly beneath it. The holon's own
page carries a short summary of the same thing, on the line under "Part of …": the journey,
the step, and a mark when that step publishes. Clicking it opens the configuration page at the
relationship.

To open configuration, click the small grey tab with the gear that hangs from the top of the
holon's page. It appears only if you can edit the holon's content or manage its team (see
[Permissions](../../core/PERMISSIONS.md)). Each section inside keeps its own rule, so you may see
only some of them. Close it with the round X in the frame's top border, or press Esc.

---

## Viewing and changing a class's configuration

Open **Settings → Classes** (staff only). Each class shows its current configuration.

You can edit these directly in the panel, per class:

- **Label**, **plural label**, **description** — inline text fields
- **Icon** — file upload
- **Journeys** — choose which journeys attach to the class; the panel shows the full inherited
  catalogue so you can see what a subclass gets from its parents. To offer a journey on one
  holon rather than every holon of a type, add it in the **Journeys** section of that holon's
  own configuration page instead — it shows the class's journeys first, then "Added on this holon",
  and both are offered when someone is added to that holon

The deeper behaviour settings — which sections appear on each of a holon's two pages, additional-field schemas, link fields,
and allowed child classes — are shown **read-only**. These are changed through a reviewed
process by the team, deliberately: because a change to a *class* affects every holon of that
class, class-behaviour changes go through review rather than being edited live. If you need one
of these changed, request it with the specific class and the change you want.

---

## Things worth knowing

- **A change to a class affects every holon of that class.** That's the point of classes — but
  it means "just tweak this one camp's sections" isn't how it works; you either change the
  class, or (for per-holon data) fill in that holon's own fields and values.
- **Subclasses inherit; they don't copy.** If you change a setting on a general class, every
  subclass that hasn't overridden it updates too.
- **Per-event variation uses subclasses.** When two events need different fields on their
  camps, each event gets its own camp subclass with its own field schema, rather than one
  shared camp class being edited back and forth.
- **'Nothing can be created here' is a class setting, not a fault.** The message names the
  class whose Allowed child classes list does not include what you tried to create. Staff can
  see the list in Settings → Classes, under **Child classes**. When the class inherits the
  list, that heading names the class it is inherited from; a class's own list has no such
  note. A class whose list is empty, or names no existing class, shows no Child classes
  section at all: that is what a class that allows nothing looks like. Agents and
  scripts can read it as `config.allowed_child_class_slugs` in
  `GET /api/v1/classes/holon/{slug}`. To change it, request it as described above, naming the
  class.
