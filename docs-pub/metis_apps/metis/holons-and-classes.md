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

### A holon's stage

Every holon has a **stage** of its own: a step on a journey. Most holons, organisations
and domains among them, sit on the generic stages **Draft**, **Live**, **Public** and
**Retired**, and a newly created one starts Live. Some kinds carry a journey of their own
instead, set by their class: a camp's, an experience's programme, a local gathering's, and
Audax's quests, missions and actions. For those, the holon's page shows three rows —
**Stage**, **Responsible** and a **Follow-up date** (a **Due date** on Audax's work). A holon
on the generic stages that can appear on the public site, such as an organisation, shows
the **Stage** row only.

### When a holon is on the public site

One rule decides it, for every kind of holon. A holon is on the public site when:

- its class allows it to be public at all (an organisation, a camp, an experience, a local
  gathering and the site's domain can be; an Audax quest cannot);
- **its stage is public**: on the generic stages that is **Public**; on a journey of its
  own, it is whichever steps that journey marks as public; and
- **the holon above it is public**, if it has one that could be. A camp under a gathering
  that is not public stays off the site, whatever its own stage says.

Live is not public. An organisation resting on Live is not on the public site; moving it to
Public puts it there. Organisations and events that were already on the public site when
this rule arrived were moved to Public for you, so nothing disappeared.

**Relationships don't publish anything.** A relationship between two holons, on a step
marked public, only decides whether a link between them is shown on public pages, and it is
shown only when **both** holons are public. Moving an organisation to "Onboarded" on a camp
hosting board, for example, shows it as the camp's host if the organisation is already
public, and does nothing if it is not. To put the organisation itself on the site, change
its own stage.

When you turn a step's **Public** flag on or off, the journey's page says which of these it
does: puts holons resting on that step on the public site, shows links on public pages, or
(on a people journey) lists people on public rosters. Boards say the same with their
**Public stage** or **Public link** mark.

### Who can change a stage

**Only the team of the holon above it moves its stage**, because that is the decision about
whether it goes on the public site. A camp's stage is moved by its gathering's team (and
staff), not by the camp's own team: the camp's team may still hand it over (Responsible) and
set its follow-up date. **A holon with nothing above it and no journey of its own** — an
organisation, for example — **has its stage changed by staff only.** Someone who may not move
a stage sees the Stage row without an edit control, the board card won't drag, and they are
told who can.

### Being responsible: what reaches you on Telegram

Whoever is **Responsible** for a holon (an action, a quest, a camp, …) hears about it on
Telegram, once they have connected their Telegram to METIS: message the METIS bot and send
it `/connect`.

- **When you are made responsible**, you get a personal message naming the item, who gave
  it to you and its due date, with a link to it. Nothing is sent when you make yourself
  responsible, or when Responsible is cleared.
- **A note with it.** After picking someone else in the Responsible row, the row says
  whether they will hear on Telegram and offers **Add a note for** them, which puts the
  cursor in the item's comment box. The note is an ordinary comment, and it arrives right
  after the message that you made them responsible.
- **Every comment on the item** reaches the responsible person's own Telegram, as well as
  any Telegram group the item is connected to.
- **The weekly update** (the METIS Weekly Update email, on Mondays) lists the items you are
  responsible for that have a due date, under **Your items due**, with anything overdue
  first. Finished items are left out.

Messages go out every few minutes, and only to someone who may still see the item: a person
who has since lost access to it is not sent its comments.

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
quest class, for example, has **Actions**, **Activity & comments**, **About** and
**Connections**. A class with tabs shows only the sections its tabs list, one tab at a time, with the tab in the
page's address (`?tab=about`), and its page leads with the holon's description (except on a
tab that shows the description itself, such as About). Local gatherings, camps and
organisations have **About** and **Invitations** tabs: Invitations lists the holon's sign-up
pages and its asks, and clicking a sign-up page's name opens its settings in the side panel.
A class whose first tab is About opens on About; one whose first tab is something else (a
quest) opens on its Overview. Someone offered only one tab — because they may not use the
others, such as Invitations — sees one long page, as for a class without tabs. Tabs are set in
the class's configuration (`tabs`, staff only) and pass down to subclasses like every other
setting. A page whose sections include **Activity & comments** shows its feed and comment box
there, and has no feed column beside the page. Every class without tabs keeps one long page.

**Connections as a section.** The section key `metis.connections` draws a holon's
Connections in its page: the people with a membership on the holon and the organisations
related to it, grouped by journey and then step, with the same **Kind** and **Group by**
controls as a place's Connections page (Group by offers Journey, Location and Sphere), each
row opening in the side panel. Its head offers **Add existing person** to who may manage the
holon's people, **Add organisation** to who may edit it, and a new person to global editors.
It shows the holon's own people and organisations, never those of the holons under it. The
quest and mission classes place it in a **Connections** tab; any other class can place it the
same way. A quest's or mission's Connections tab also lists the conversations linked to it, under
**Recorded Conversations**, for people with Coherence access.

### A holon's two views

Each holon has two pages. Its **view** is what the holon *is*: description, links, people,
events, and so on. Its **configuration** is what drives it and what has happened to it:
**Access** (who holds which capability, and the journey step that grants it),
**where this appears** on the public site,
**Journeys**, **Telegram** and **Import CSV** (and, for a class without an Invitations tab,
invitation **Pages** and **Asks**). The class decides
which sections go on which page, the same way it decides which sections appear at all; the
resolved lists are read in Settings → Classes (staff only).

The **History** tab, for anyone who may edit the holon, opens the holon's history page
(a class may also place a **Change history** button on its configuration page): one list of everything that happened to it, newest first, under day
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

For any holon that can be public, **Where this appears** says whether it is on the public
site and why: its stage and whether that stage is public, with **Change stage** (which opens
the Stage row) when you may move it; whether the holon above it is public, when that
matters; and which of its links are shown on public pages. The holon's page header carries
its stage as a chip too.

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

### Who may edit a journey: its owner

A journey can have an **owner**: the holon that maintains it. Staff choose it in the **Owner** row
of the journey's **Configuration**. Once a journey has an owner, everyone who can edit that holon
(its team, or the team of a holon above it) can edit the journey's name, texts and steps: rename a
step, change its texts, add one, reorder them. The step switches (public, team member and the
others) stay staff-only, and so does choosing the owner. While the owner's team can edit the
journey, they can also open and read it, even where they could not see it before.

A holon can own a journey only while nothing outside it uses the journey. Every holon that offers
it, every holon of a type that offers it or runs on it, and every holon with people on its steps
must be that holon or below it. Links between holons on the journey's steps are not counted on
their own: a link can only be added on a journey one of its two holons offers, and every holon
offering the journey is already counted. If any holon is outside, the owner is refused, with the
names of the holons outside. That way one holon's team can never change a journey other holons
rely on.

The same holds after the owner is chosen. Whenever the journey is used outside the owner,
however that came about, the owner's team can neither edit nor read it through the owner until
that is resolved: the use is removed, or staff choose another owner or clear it. Some ways of
adding such a use are refused up front: adding the journey to a holon or a type outside the owner
in the app's own forms, in the admin's class form and its journey audit, and through the API.
Others are not, and simply suspend the team's right: a holon below the owner moved elsewhere, a new
holon of a type that offers it created elsewhere, someone put on its steps in a holon outside, or a
type's settings changed so that it runs on the journey.

A journey with no owner keeps the earlier rule: a holon's team can edit it only when that holon is
the one place it is offered and no type offers it; anything shared is edited by staff. A
conversation journey Coherence creates or duplicates for an event is owned by that event.

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
