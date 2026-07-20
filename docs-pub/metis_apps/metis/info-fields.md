# Additional Fields (Info Field Configuration)

Info fields — shown in the UI as a holon's **Additional fields** — let you define
structured, custom data for a holon class: things like format, capacity, theme, links to
videos, photo slideshows, or any other detail you want to collect and display. They work
for **any holon class** — organisations, camps, events, and so on — not just camps.

This is one piece of a holon class's configuration. For the bigger picture of holons and
their classes, see [Holons and classes](holons-and-classes.md).

Two parts, set in two places:

- The **schema** (which fields exist, their types, whether they show publicly) is defined
  once on the holon **class** — see [Holons and classes](holons-and-classes.md) for
  how class configuration and inheritance work.
- The **values** are filled in per holon, on that holon's page in the CRM.

Configuring the schema is admin-only. Because the schema lives on the *class*, it applies
to every holon of that class. Where different contexts need different fields (for example,
each event's camps needing their own fields), that's done by giving each context its own
subclass with its own schema — you don't edit fields on individual holons.

---

## How it works

- **The schema lives on the holon class.** You define which fields exist, their types, and
  whether they appear publicly, in the class's `info_field_groups` configuration. Like all
  class configuration, it's resolved up the class's ancestor chain, so a subclass inherits
  its parent's fields unless it defines its own.
- **Values live on each holon.** Each holon fills in its own values for those fields.
- **The public view page** shows only fields marked `public_visible: true` that have a
  non-empty value.
- **The CRM holon page** shows all configured fields and lets you edit their values.

---

## Step 1 — Define fields on the holon class

The field schema is part of the class's configuration, which is changed through the team's
reviewed process (see [Holons and classes → Viewing and changing a class's
configuration](holons-and-classes.md#viewing-and-changing-a-classs-configuration)). The
schema is an `info_field_groups` list of ordered groups, each with a title and a list of
fields:

```json
{
  "info_field_groups": [
    {
      "title": "Basics",
      "help_text": "Public-facing details shown when visible and filled.",
      "fields": [
        {
          "key": "format",
          "label": "Format",
          "type": "select",
          "options": ["Workshop", "Talk", "Unconference", "Social"],
          "public_visible": true,
          "help_text": "What format will this take?"
        },
        {
          "key": "capacity",
          "label": "Capacity",
          "type": "text-line",
          "public_visible": true,
          "help_text": "Approximate number of participants."
        }
      ]
    }
  ]
}
```

Fields are displayed in group order, then field order. Field keys must be unique across
all groups for a given class.

---

## Field definition reference

| Property | Required | Description |
|---|---|---|
| `key` | yes | Unique identifier for this field within the class. Use lowercase with underscores (e.g. `session_format`). Changing the key after holons have saved values will orphan those values. |
| `label` | yes | Human-readable label shown in the CRM and on the public page. |
| `type` | yes | One of `text-line`, `text-area`, `select`, `video`, `slideshow`, or `button`. |
| `options` | only for `select` | Ordered list of choices. Each is either a plain string, or an object `{"value": ..., "label": ..., "icon": ...}` — see the `select` notes below. |
| `button_text` | only for `button` | Label displayed on the button. Defaults to `label` if omitted. |
| `public_visible` | yes | `true` to show this field on the public page; `false` to keep it CRM-only. |
| `help_text` | no | Guidance shown above the field in the CRM edit form. Not shown publicly. |
| `help_link` | no | URL to detailed help documentation. When present, a Help button is shown alongside the help text in the CRM edit form. Not shown publicly. |

### Field types

| Type | Renders as | Stored value |
|---|---|---|
| `text-line` | Single-line text input | String |
| `text-area` | Multi-line text input | String |
| `select` | Multi-select dropdown with chips, fixed option list | List of strings |
| `video` | YouTube URL input → embedded iframe (16:9) on display | Normalized `https://www.youtube-nocookie.com/embed/<id>` URL string |
| `slideshow` | Per-photo upload UI with remove buttons → fade-transition Splide carousel on display | List of media URL strings |
| `button` | URL input in the CRM → labelled link button on display | URL string |

#### `select` notes

Options come in two interchangeable shapes:

- **Plain string** — `"Workshop"` acts as both the stored value and the display label.
- **Object** — `{"value": "mind", "label": "Mind", "icon": "brain"}` separates the stable
  stored value from the display label, and may add an optional icon shown next to the
  label on chips, cards, and detail pages.

Rules:

- `value` and `label` are required on object options; the stored value is always the
  `value` string, so labels can be reworded later without touching saved data.
- `icon` is optional and must be a key from the shared icon set; an unknown key falls back
  to showing the label alone. Icons accompany the label — they never replace it.
- The two shapes can be mixed in one `options` list, and existing string-option fields
  keep working unchanged.
- Saved values are validated against the configured options: a value not in the list is
  not stored.

#### `video` notes

- Accepts any common YouTube URL form: `youtube.com/watch?v=…`, `youtu.be/…`, `youtube.com/shorts/…`, `youtube.com/embed/…`. Invalid or non-YouTube URLs are stored as an empty string.
- The embed is rendered in a responsive 16:9 wrapper on both the CRM and public pages.

#### `button` notes

- The `button_text` is set once on the class's schema and shared by all holons of that class. Each holon provides its own URL as the field value.
- If the URL value is empty, the button is not shown on either the CRM display or the public page.
- If `button_text` is omitted from the schema, the field's `label` is used as the button text.

#### `slideshow` notes

- Photos are uploaded one at a time via the CRM edit UI. Each upload immediately posts and re-renders the photo grid; there is no separate save step for slideshow fields.
- Accepted formats: JPEG, PNG, GIF, WebP. Maximum 5 MB per photo.
- On display (CRM and public), the photos render as a Splide carousel: fade transition, autoplay every 4 s, photos shown with `object-fit: contain` so they are fully visible. On the public page the navigation arrows and pagination dots are hidden.

---

## Step 2 — Fill in values per holon

Open a holon in the CRM. The **Additional fields** section shows all configured fields.

Click **Edit** to open the form. Each field renders as the appropriate input type. Save
when done. Values are stored on the holon under `infos["info_fields"]`, for example:

```json
{
  "info_fields": {
    "format": ["Workshop"],
    "capacity": "40",
    "internal_notes": "Needs AV support",
    "intro_video": "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ",
    "photos": [
      "/media/pages/media/my-holon/photos/abc123.jpg"
    ]
  }
}
```

Value shapes by field type:

- `text-line`, `text-area` — string
- `select` — list of strings (multi-select)
- `video` — string (normalized embed URL, or empty string if invalid/cleared)
- `slideshow` — list of strings (media URLs)
- `button` — string (URL; leave empty to hide the button)

---

## Public display

On the holon's public view page (organisation and camp pages both render info fields),
fields are shown when both conditions are met:

1. `public_visible` is `true` on the field definition.
2. The holon has a non-empty value for that field.

---

## Gotchas

**Renaming a key breaks existing values.** If you change a field's `key` on the class
after holons have already saved data, the old values remain in storage but are no longer
linked to the field — they become invisible. Treat keys as permanent once holons have
data.

**Removing a field from the schema hides its values** from the CRM form and public page,
but the data stays in the holon's `infos` JSON. It is not deleted.

**Select values are stored as plain strings inside a list.** If you change or remove an
option from a `select` field's `options` list, holons that previously saved that option
will still display the raw string (it just won't match any current option in the
dropdown).

**Slideshow photos are not garbage-collected when removed from the field.** Clicking the
remove button unlinks a photo from the holon's value list, but the underlying file
remains in storage. Hard-deletes of orphaned media must be done out of band.
