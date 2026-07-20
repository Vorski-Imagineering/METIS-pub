# Experiences (Camp Programme)

An **Experience** is one thing a camp offers — a workshop, ceremony, practice session,
performance, or any other item in the camp's programme. Together, a camp's experiences form
its **Programme**; the programmes of all camps in a Gathering form that Gathering's
programme.

Experiences are the *catalogue*: what's on offer and who's behind it. They deliberately
carry **no date, time, capacity, or registration** — the programme describes offerings, it
doesn't schedule or sell them.

This guide covers creating and configuring experiences. It assumes you know the basics of
[camps and local gatherings](camps-and-gatherings.md) and
[holons and classes](../metis/holons-and-classes.md).

---

## How an experience relates to its camp

Every experience belongs to **exactly one camp** — the camp that offers it. That ownership
is the experience's place in the holon tree (the camp is its parent), and it's
organisational, not geographical: an experience can happen away from the camp's physical
location and still be part of that camp's programme.

The Gathering context comes through the camp: an experience under a camp under the
Portugal 2026 gathering is part of the Portugal 2026 programme, automatically.

An experience can additionally be *related* to other holons — a partner organisation, a
co-hosting camp — through standard holon relationships, without changing which camp owns
it.

## Where experiences appear

- **On the camp's page** — camps show an **Experiences** section: a card grid of the
  experiences that camp owns, each showing its image (or a generated tile), a short
  description, and its configured tags. Click a card to open the experience.
- **In the Experiences list** — users with Gathering access get an **Experiences** nav item
  whenever their current [Focus](../../web/app/focus-and-scoping.md) contains experiences.
  It's the standard list view: filters live in the URL, so a filtered view can be
  bookmarked and shared.
- **On the experience's own page** — the standard holon detail page: description, links,
  additional fields, team, and related holons.

## Creating an experience

Use **Add Experience** on a camp's page (the camp comes preselected and locked), or the
create button on the Experiences list. You can create experiences under any camp you may
edit — as a member of the camp's team or of its Gathering's team; you don't need to be a
global editor.

The form asks only for:

1. **Camp** — the owner; preselected when you start from a camp page.
2. **Name** — what it's called on programme cards.
3. **Description** — used in full on the experience's page, and automatically shortened
   for the compact cards. There is no separate "teaser" field to maintain.
4. Any **configured fields** the experience class defines (see below).

Everything else — images, people, related organisations — can be added afterwards on the
experience's page.

Which class of experience the form creates is controlled by the **camp class**
configuration (its `allowed_child_class_slugs`). Out of the box, camps allow the generic
**Experience** class and the form shows no class choice; an event-specific camp class can
instead allow its own experience subclass(es), in which case a class picker appears. The
administrator setup is covered step by step in
[Experience configuration](experience-config.md).

## Configuring experience fields

Descriptive attributes (topics, format, venue, access, and so on) are **not** built-in
experience fields. They're defined by an administrator on the experience *class* as
[Additional fields](../metis/info-fields.md), so each event can decide what its programme
collects — and the create/edit forms stay exactly as short as the configuration.

Two things are worth knowing beyond the standard additional-fields guide:

### Select options can carry icons

A select field's options can be plain strings, or objects with a stable stored value, a
display label, and an optional icon:

```json
{
  "key": "dimension",
  "type": "select",
  "label": "Dimension",
  "options": [
    {"value": "mind", "label": "Mind", "icon": "brain"},
    {"value": "heart", "label": "Heart", "icon": "heart"},
    {"value": "body", "label": "Body", "icon": "body"}
  ],
  "public_visible": true
}
```

The icon shows next to the label on cards, chips, and detail pages; the stored value stays
the stable `"mind"` / `"heart"` / `"body"` string. Icons always accompany the text label —
they never replace it — and an unknown icon key simply falls back to the label alone.
Existing string options keep working unchanged and act as both value and label.

This option shape works for select fields on **any** holon class, not just experiences.

### Keep the first form short

Configure only fields you will actually display or filter by. Long forms reduce
submissions and produce low-quality data; a programme with names, descriptions, and one or
two well-chosen selects beats one with ten half-filled fields.

## People and related holons

- **People** join an experience through standard memberships, exactly as on camps. They're
  grouped and labelled by the journey they're on — there are no hard-coded experience
  roles. An experience doesn't need any people attached to be part of the programme.
- **Organisations, other camps, and other holons** connect through standard holon
  relationships, also grouped by journey name. Relating another camp does *not* change
  which camp owns the experience.

See [Journeys](../../core/JOURNEY.md) for how journeys and steps work.

## Publishing and public pages

Whether an experience is publicly visible is a **journey state**, not a checkbox: the
camp↔experience programme relationship moves through a configured journey, and steps (or
whole journeys) marked public-visible publish the experience — the same mechanism that
already controls which organisations appear on public camp pages.

A published experience appears on four public surfaces, all sharing one artwork and card
treatment:

- the **Gathering page** shows a programme teaser — a count summary and a slider with a
  small balanced sample of experiences across camps, linking to the full programme
- the **Gathering programme** page (`…/programme/`) lists every published experience,
  filterable by camp, by any public select field, and by text search — all filters live in
  the URL, so a filtered view can be shared
- the **camp page** shows a preview and links to that camp's full programme page
- each experience has its own **shareable detail page** with artwork hero, description,
  links, public fields, people, and related organisations

A non-published experience's public URL returns 404 — it never leaks through any public
page. Cards without an uploaded image automatically use a background from the camp's or
Gathering's configured image library, chosen once at creation so it stays stable; see
[Experience configuration](experience-config.md).

## Deliberate non-features

By design, experiences have no:

- date, time, or calendar scheduling
- capacity or registration
- pricing or purchasing

If you find yourself wanting these on the programme, that's a product conversation, not a
configuration option.
