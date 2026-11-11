# Managing classes

Concepts (class tree vs containment tree, inheritance, what config controls) are in
`docs-pub/metis_apps/metis/holons-and-classes.md`. Info-field schema reference (field types,
`select` options, key rules) is in `docs-pub/metis_apps/metis/info-fields.md`. Read those for
the "what"; this file is the "where and how".

## Two places, different powers

| Change | Where |
|---|---|
| Label, plural label, description | Classes browser, inline |
| Icon | Classes browser, inline (file upload) |
| Journeys offered on the class (person + holon) | Classes browser, inline |
| `config` JSON: `info_field_groups`, `detail_sections`, `views`, `link_fields`, `allowed_child_class_slugs`, `publication`, `css_class` | Django admin only |
| Create a new class / subclass | Django admin only (the Classes browser has no Add button) |
| Slug, object kind, app, parent of an existing class | Read-only everywhere (set at creation) |

### Classes browser: `https://app.the-gathering.earth/classes/`

- Staff only. Left column lists classes grouped by app (Coherence, Gathering, …), each with its
  kind pill (`holon`, `journey`, `space`, `step`, `agent`, `person`) and `↑ <parent class>`.
- **Deep link:** `/classes/?kind=<kind>&slug=<slug>` (e.g. `?kind=holon&slug=camp`) opens the
  panel directly. Panel content loads into `#browse-main` via htmx.
- The panel shows: details (label, plural, description, kind, slug, parent, status, app, CSS
  class), child classes, the resolved **View** and **Configuration** section lists (with the
  class that defines each), info-field groups, link fields, **Journeys**, **Members** (the
  holons of this class: use it to state the blast radius), and **Raw config**.
- **The class id** is in the panel's edit URLs: `/core/classes/<id>/field/...`. The pencil
  (top right) links to `/admin/core/metisclass/<id>/change/`.

Inline edit forms (htmx; open by clicking the value, then **Save**/**Cancel**):

| Field | Edit fragment | Posts to |
|---|---|---|
| label / plural_label / description | `GET /core/classes/<id>/field/<field>/edit/` | `/core/classes/<id>/field/<field>/update/` (input `value`) |
| journeys | `GET /core/classes/<id>/field/journeys/edit/` | `/core/classes/<id>/field/journeys/update/` |
| icon | `/core/classes/icon/<id>/edit/` | file upload |

**Journeys form = two multi-selects, both named `journeys`:** `#class-person-journeys-select`
(journeys for *memberships* of people on holons of this class) and
`#class-holon-journeys-select` (journeys for *relationships* between holons). Saving submits
**the full selection: anything not selected is removed from the class.** Read the current
selection first, add or remove only what the user asked for, and leave the rest selected.
To offer a journey on **one holon** rather than the whole class, use that holon's own
configuration page (Journeys section) instead. That is the less invasive option, so suggest it
when the user only names one holon.

The panel's sections and config are marked "Read-only here; placement changes go through a
migration or a reviewed data edit". That is the team's policy, so admin edits to `config` are
the "reviewed data edit" route: always do the full read → confirm → save → verify cycle.

### Django admin: `https://app.the-gathering.earth/admin/core/metisclass/`

- Change form: `/admin/core/metisclass/<id>/change/`. Editable: label, plural label, icon,
  sort order, description, journeys (dual-list widget), **`config`** (plain JSON textarea).
  Read-only: slug, object kind, app, parent, is system, is active.
- Save buttons: **Save**, **Save and continue editing**, **Save and add another**. Prefer
  *Save and continue editing* so you stay on the page and can see validation errors.
- **History** (top right) → `/admin/core/metisclass/<id>/history/` shows past changes.
- Add form: `/admin/core/metisclass/add/`. Required: label, slug, object kind
  (`holon, person, agent, journey, page, step, space`), metis app, sort order, config
  (default `{}`). Parent is optional but almost always wanted: a subclass inherits its
  parent's journeys and config, so it only needs the keys that differ. App and parent are
  search/autocomplete selects, so type to find the option rather than reading its `<option>`
  list (it starts empty). To fill them from `javascript_tool`, look the id up with
  `fetch('/admin/autocomplete/?' + new URLSearchParams({term, app_label:'core',
  model_name:'metisclass', field_name:'metis_app'|'parent'}))` → `results[{id,text}]`, add
  `new Option(text, id, true, true)` to the select and fire `django.jQuery(sel).trigger('change')`.
  Then read every field back and screenshot the form for the user before saving. The user
  may click **Save** themselves, so verify afterwards either way.
- **Copying a class** (e.g. "new Gathering 2027 like The Gathering Mexico 2026"): copy kind, app,
  parent and config, but don't copy blindly. Event-specific values in the source (its
  journeys, a per-event child class like `camp_mx2026` in `allowed_child_class_slugs`) usually
  belong to the old event: ask about each one. To let a key inherit from the parent, leave it
  out of the config, and check what the parent provides first.
- **After saving, compare the panel with what you filled in.** The user may adjust the form
  (e.g. add a journey) before clicking Save. A difference is usually theirs: report it and ask,
  but don't undo it.

## Editing `config` safely

1. Read the current JSON from `textarea[name=config]` (or the panel's Raw config) and show the
   relevant part to the user. Keep the full original so it can be restored.
2. Change **only the keys asked for**. Config is resolved per key up the class tree: a key
   present on this class *replaces* the inherited value for that key, it does not merge. So
   adding `info_field_groups` to a subclass with one new group hides every inherited group
   unless you copy them in too. Check where the current value comes from (the panel says
   "fields from this class" or names the ancestor) before deciding which class to edit.
3. Write the textarea value with `javascript_tool` (`JSON.stringify(obj, null, 2)`), not by
   typing: typing long JSON is slow and error-prone.
4. Confirm with the user (class, before/after diff, number of members affected), then
   **Save and continue editing**. Read any error banner: unknown info-field `type`s and bad
   JSON are refused on save.
5. Verify in the Classes browser panel (reload the deep link) and/or `GET /api/v1/classes`.

### Info-field gotchas (from `info-fields.md`)

- Field `key`s are permanent once holons have values. Renaming one orphans the saved data.
  Add a new field instead, and tell the user.
- Keys must be unique across all groups of the class.
- Removing a field or a `select` option hides values but doesn't delete them.
- Per-event variation is done with a **subclass** that has its own schema, not by editing a
  shared class back and forth.
