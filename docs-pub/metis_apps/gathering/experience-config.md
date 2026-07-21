# Experience Configuration (Administrator Checklist)

Experiences ship as **generic behaviour plus configuration**: the code never
hard-codes your programme's vocabulary, fields, or workflow states. This
checklist takes a deployment from zero to a working, publishable camp
programme. The user-facing guide is [Experiences](experiences.md); the general
config mechanics are in [Holons and classes](../metis/holons-and-classes.md)
and [Additional fields](../metis/info-fields.md).

---

## 1. Verify or choose the Experience class per camp class

The base `camp` class ships allowing the generic `experience` class in its
`allowed_child_class_slugs`. A contextual camp class (for one event) may
override the list with its own experience subclass — or several, when that
distinction is genuinely needed:

- **one** allowed class → the create form shows no class picker
- **several** → the form shows a picker using their configured labels
- **none** → creation shows a configuration error and creates nothing

Create contextual experience subclasses (class-tree parent: `experience`) only
when an event's experiences need their own fields or journeys.

## 2. Define the Experience fields

On the experience class (or subclass), configure `info_field_groups` with the
descriptors your programme will actually display or filter by — topics, format,
venue, access, and so on. Keep keys consistent across contextual subclasses so
public filters merge cleanly. Select options may carry icons:

```json
{"value": "mind", "label": "Mind", "icon": "brain"}
```

Fields marked `public_visible: true` appear on public pages; public **select**
fields additionally become filters on the public Gathering programme page,
automatically.

## 3. Create the programme journey

Attach **exactly one** holon journey carrying the config flag

```json
{"experience-programme": true}
```

to each creatable experience class's journey catalogue. This flag only selects
which journey new experiences start on — its name, steps, and transitions are
yours to design. Creation fails with a visible error when zero or several
flagged journeys resolve, and the new experience starts on the journey's first
active step.

## 4. Configure publication

Mark the step (or the whole journey) that should publish an experience with

```json
{"public-visible": true}
```

This is the same rule used everywhere on the public site: an experience appears
on public programme pages exactly when its camp-programme relationship sits on
a public-visible step or journey. There is no separate publish button or
publisher role — moving the relationship through its journey is publishing.

## 5. Configure people and related-holon journeys

Person journeys in the experience class's catalogue label the People groups on
the experience page (their journey names are the displayed group titles — no
hard-coded roles). Holon journeys do the same for related organisations, camps,
and other holons.

## 6. Configure artwork libraries

Add a `slideshow` info field with the key `experience_backgrounds` (marked
`public_visible: true` — its image URLs intentionally feed public artwork) to
the Gathering, Camp, and Experience classes:

- Gathering editors upload the default background library
- Camp editors may upload a camp override (a **non-empty** library replaces the
  Gathering's; an empty one inherits)
- Experience editors may upload an experience-specific pool instead of setting
  the single image

Resolution order, checked fresh on every render:

1. the experience's own uploaded image — always wins, if set
2. otherwise, one background assigned once from the nearest non-empty
   library (own → camp → Gathering), persisted so it stays stable across
   page loads
3. otherwise, a branded colour treatment — never a broken tile

The background assignment itself happens at two points only, never at
render time:

- **on creation**, drawing at random from whichever library (own/camp/
  Gathering) is nearest and non-empty
- **when the experience's own library is edited** — the current pick is
  kept if it's still in the (new) nearest pool, redrawn if it fell out, and
  cleared/refilled from the Camp/Gathering pool if the experience's own
  library was emptied

Editing a **Camp's or Gathering's** library never touches existing
experiences — only new ones drawn against it afterwards. This is why an
experience's background can look "stuck" after a parent library changes:
that's by design, not a bug.

On experience editing surfaces, label the standard holon image **Image** (not
Logo) and the slideshow **Background image options**, with help text explaining
that leaving both empty inherits the Camp/Gathering library.

Once this field is switched on, non-technical organisers can fill the libraries
themselves by clicking through the pages — that walkthrough is
[Giving experiences nice images](experience-images-howto.md).

## 7. Configure links

Set `link_fields` on the experience class for the link inputs experiences
should offer, marking the public ones `public_visible`.

## 8. Verify end to end

1. As a camp team member, use **Add Experience** on a camp page: the camp is
   preselected and locked, the form shows your configured fields.
2. Confirm the new experience appears in the camp's Experiences block, the
   Experiences list, and its own detail page — but **not** on any public page.
3. Move its programme relationship to the public-visible step.
4. Confirm it now appears on the public camp page preview, the camp programme,
   the Gathering programme (with filters working from the URL), and its own
   shareable detail page — with artwork, people, and related holons rendering.
5. Confirm API discovery:
   `GET /api/v1/holons?class=experience&sort=latest`.

## Worked example

A minimal working configuration for one event:

- camp class `camp_pt2026`: `allowed_child_class_slugs: ["experience"]`
- experience class `experience` with one field group:
  `dimension` (select: mind/heart/body with icons, `public_visible: true`) and
  `venue` (text-line, `public_visible: true`)
- journey **“Programme”** on the `experience` catalogue with
  `{"experience-programme": true}` and steps
  *Idea → In preparation → Published*, where *Published* carries
  `{"public-visible": true}`
- person journey **“Hosts”** in the experience catalogue for the team section
- `experience_backgrounds` slideshow on the Gathering class with 6–10 images

With exactly this, camps enter experiences through a two-field form plus two
selects, and publishing is dragging the programme card to *Published*.
