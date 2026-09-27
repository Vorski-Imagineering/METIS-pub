# Experiences (Camp Programme)

An **Experience** is one thing a camp offers — a workshop, ceremony, practice session,
performance, or any other item in the camp's programme. Together, a camp's experiences form
its **Programme**; the programmes of all camps in a Gathering form that Gathering's
programme.

Experiences are the *catalogue*: what's on offer and who's behind it. Each one also carries
a **day** and a **start time** — one of each, because one experience is one session — so the
public programme can open **by day**. They deliberately carry **no capacity or
registration**: the programme describes offerings, it doesn't sell them.

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
- **On the gathering's page** — the same section shows the whole programme: every
  experience owned by any of the gathering's camps, each card naming its camp. When
  there are more than twelve, the first twelve are shown with a **See all N
  experiences** link to the full list. That list needs Gathering access; without
  it you see up to sixty cards and a line saying how many there are in all.
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
- the **Gathering programme** page (`…/programme/`) opens **by day** (see below); its
  **All experiences** tab (`…/programme/?view=all`) lists every published experience,
  filterable by camp, by any public select field, and by text search — all filters live in
  the URL, so a filtered view can be shared
- the **camp page** shows a preview and links to that camp's full programme page, which
  opens by day too
- each experience has its own **shareable detail page** with artwork hero, description,
  links, public fields, people, and related organisations

A non-published experience's public URL returns 404 — it never leaks through any public
page.

### Artwork resolution order

Every card and hero image resolves in the same fixed order, with no randomness at render
time:

1. **The experience's own uploaded image**, if set — always wins.
2. Otherwise, a **background chosen once at creation** from the nearest non-empty image
   library (the experience's own, else its camp's, else its Gathering's) — persisted so the
   same experience always shows the same background, even across page loads.
3. With no image and no library anywhere, a **branded colour treatment** — never a broken
   image tile.

Uploading an image later always overrides the assigned background immediately. For a
click-by-click walkthrough aimed at organisers, see
[Giving experiences nice images](experience-images-howto.md); the administrator setup of the
image libraries is in [Experience configuration](experience-config.md).

### The programme by day

Every experience has a **Day** and a **Starts** field, in its **When** group. Set them in
the CRM like any other field: the day with the date picker, the time as 24-hour `HH:MM`
(`09:30`). A time such as `9:30` or `25:00` is refused with a message. The time is the local
time at the gathering.

The programme page then shows:

- **every day of the gathering** (its start date to its end date) as a chapter, labelled
  "Opening day", "Day 2" … "Closing day" ("The day" for a one-day gathering). A day with
  nothing on it says the programme for it is still being made. An experience dated outside
  the gathering's dates gets a chapter of its own. A gathering longer than three weeks —
  usually an end date typed wrong — shows only its first and last days and the days that
  have experiences, and when its days run across two months the month is shown too.
- what **the day holds** — the three tags (public select values) its experiences carry
  most — and, when at least three days have experiences, which is **the fullest day**. Both
  are worked out from the experiences, never typed in.
- the day's experiences as cards, **ordered by start time**, then the ones with no time,
  A–Z. A card shows its picture, its camp and a few lines; **the time is shown only when the
  card is opened**, with the full description and its people, grouped and titled by
  journey as on the experience's own page.
- six cards per day (four on a phone), then "See all … on Saturday", which opens that day
  alone (`…/programme/?day=2026-10-24`).
- experiences with no day yet, together at the end under **Day to be announced** — or,
  once the gathering is over (or when the day field is kept private), under **Other
  experiences**, since no day is coming.
- when the gathering has a **Tickets** link and has not ended, a ticket bar at the foot of
  the screen.

The experience's own page shows its day and time under its camp's name, or "Day to be
announced" while that can still happen.

## Deliberate non-features

By design, experiences have no:

- end time, length, or more than one session
- capacity or registration
- pricing or purchasing

If you find yourself wanting these on the programme, that's a product conversation, not a
configuration option.
