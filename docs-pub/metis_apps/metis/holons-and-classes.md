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
| **Allowed child classes** | Which kinds of holon can be created *underneath* a holon of this class. |
| **Journeys** | Which journeys attach to this class — the progression tracks its holons and their relationships can move through. See [Journeys](../../core/JOURNEY.md). |
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

---

## Viewing and changing a class's configuration

Open **Settings → Classes** (staff only). Each class shows its current configuration.

You can edit these directly in the panel, per class:

- **Label**, **plural label**, **description** — inline text fields
- **Icon** — file upload
- **Journeys** — choose which journeys attach to the class; the panel shows the full inherited
  catalogue so you can see what a subclass gets from its parents

The deeper behaviour settings — detail-page sections, additional-field schemas, link fields,
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
