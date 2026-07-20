# Permissions

## Overview

Access control in METIS has five layers:

1. **Django built-ins** — `is_superuser` and `is_staff` grant global edit access. Some
   module-specific features, such as Coherence, still require their own group unless noted
   below.
2. **Trusted broad editors** — users in the `trusted_editors` group get broad non-admin
   editing access.
3. **Coherence users** — users in the `coherence_users` group may access the Coherence
   module. Superusers are also allowed; `is_staff` and `trusted_editors` are **not**
   automatically included.
4. **Config-flag roles** — semantic roles declared as flags on a `JourneyStep`'s
   configuration (see [Config flags](#config-flags) below).
5. **Object ownership** — a person can always edit their own record.

Throughout this document, **global edit access** means the user is a superuser, is staff,
or belongs to `trusted_editors`.

---

## Groups

Three Django groups control access. Assign users to them in Django admin.

| Group | Grants |
|---|---|
| `trusted_editors` | Broad non-admin edit access across the application (global edit access). |
| `coherence_users` | Access to the Coherence module (conversations, transcripts, journeys). |
| `csv_importers` | Permission to run CSV imports. |

---

## Config flags

Some permissions are configured by setting flags in the `config` of a `JourneyStep`,
rather than by group membership.

### `team-active`

Marks members resting at this step as **active team members** of the holon. This is the
key that powers scoped editing. It controls:

- display and sidebar focus,
- default journey placement when quick-adding a member, **and**
- permission to edit the holons they belong to (including ancestor holons).

**Setting it:** there is no toggle in the journey step editor — the flag lives in the
step's `config`, editable in Django admin (journey page → pencil icon → *Journey steps*
inline):

```json
{"team-active": true, "color_bg": "#109367"}
```

The value must be the JSON boolean `true`. **The string `"true"` does not work** — every
reader checks for boolean `true`, so a string reads as unset. The journey editor renders a
greyed-out chip when it finds a string, so a mistake here is visible rather than silent.

### Display flags are not permission flags

Not every config flag grants access. `public-visible` (below) controls only what is
*shown* on the public site and grants no edit rights. Keep the two ideas apart: don't
reach for a permission flag to make something public.

---

## Public visibility (`public-visible`)

**This is not a permission.** It decides what the public `/view` site publishes, and
grants no access to anything.

| Where set | Effect |
|---|---|
| On a `JourneyStep` | A flow resting on this step is publishable. Use for one public stage of an otherwise internal journey. |
| On a `Journey` | **Every** step of the journey is publishable. Use when the whole pipeline is public. |

The two are ORed: a flow publishes if either its current step or its journey carries the
flag. The value must be the boolean `true` (same rule as `team-active`).

**What reads it:** the public gathering page (`/view/<gathering>/`) and camp page
(`/view/<gathering>/<camp>/`) both list an organisation when it is related to a camp *and*
the relationship's step or journey is flagged. The two pages always agree.

⚠️ The flag belongs to the step or journey, not to a page. Setting it on a journey shared
across many holons (e.g. an outreach journey whose steps include *To Contact* and
*Inactive*) publishes **every** flow in that journey — including cold prospects. Prefer the
step-level flag on shared journeys; use the journey-level flag only when the whole pipeline
is genuinely public.

**Checking:** the journey editor shows every flag set on a journey and on each step as a
read-only chip, so you can see what is actually set without reading JSON.

---

## What each role can do

The table below summarises who can perform each action. "Global editor" = superuser, staff,
or `trusted_editors`. "Scoped team member" = a person with a `team-active` membership on the
holon **or any of its ancestors**.

### Holons

One canonical rule — **"can edit this holon's content"** — governs a holon's fields, its
memberships, and its relationships. It passes for global editors and for scoped team
members of the holon **or any of its ancestors**.

| Action | Who can do it |
|---|---|
| View a holon's notes / activity | Anyone who can edit that holon |
| Edit a holon's fields, logo, and configuration | Anyone who can edit the holon's content |
| Manage a holon's team (add/remove members, edit membership flow) | Anyone who can edit the holon's content |
| Add / edit / delete holon relationships | Anyone who can edit the content of **either endpoint** of the relationship |
| Create a child holon under a holon (of a class its config allows) | Anyone who can edit the parent holon's content |
| Create an unrestricted top-level holon | Global editors only |
| Delete a holon | Superusers and staff only (trusted editors cannot delete) |
| Assign journeys to a holon | Global editors only |

Because scoped rights walk **up** the ancestor chain, a team member of a parent holon can
edit all of its child holons — a Gathering team member can manage its camps' teams and
relationships, and a camp team member can do the same for the camp's experiences.

Managing a relationship from one endpoint never grants edit access to the *other*
endpoint: relating your camp to an organisation doesn't let you edit that organisation.

### People

| Action | Who can do it |
|---|---|
| Edit a person | Global editors; the person themselves; scoped team members who share a holon with that person |
| Delete a person | Superusers and staff only |

### Journeys and users

| Action | Who can do it |
|---|---|
| Manage journeys (journey editor, Journeys settings) | Global editors only |
| Create / manage user accounts | Global editors, or team-active members of a **domain**-type holon |
| Run CSV imports | Superusers or members of `csv_importers` |

### Coherence

| Action | Who can do it |
|---|---|
| Access Coherence (conversations, transcripts, journeys) | Superusers and members of `coherence_users` only |

Coherence access is a deliberate opt-in: it does **not** follow from `is_staff` or
`trusted_editors`. The Coherence navigation item and all Coherence-related sections
(profile, person detail, holon detail, note links) appear only for users with Coherence
access.

---

## What different users see

**Global editors** land on the Activity / dashboard page and see the operational
navigation (Activity, Calendar, Kanban), the Journeys settings card, the Chrome extension
download card, and the option to clear focus (view "All").

**Scoped users** (team members without global edit access) are taken to the detail page of
their first team-active holon. Their focus is scoped to their team holons and those holons'
ancestors. If they have no team-active holon, they remain on the landing page.
