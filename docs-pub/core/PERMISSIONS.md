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

## The rule

**You can read anything that is not private. You can change a holon's things if you can
edit that holon.**

Everything below is that rule applied to a particular screen. If a page shows you
something, the question of whether you may change it has one answer: can you edit the
holon it belongs to? A membership belongs to its holon, a relationship to either of its
two ends, a journey to the single holon that carries it. There is no separate "but only
if the holon is private" branch anywhere — that was a rule of its own for a while, and it
meant a scoped team could see a thing on their own screen and be refused when they moved
it.

Two things are deliberately **not** covered by the rule:

- **Notes.** A holon's notes and activity are its internal record, so reading them asks
  for *edit* access, not view access — whether or not the holon's class is private.
- **CSV import.** Bulk import has its own group, `csv_importers`, because it writes far
  more than the screen it is launched from — and being able to edit one holon is not a
  reason to be able to load rows into many.

---

## Groups

Three groups control access. A global editor assigns users to them.

| Group | Grants |
|---|---|
| `trusted_editors` | Broad non-admin edit access across the application (global edit access). |
| `coherence_users` | Access to the Coherence module (conversations, transcripts, journeys). |
| `csv_importers` | Permission to run CSV imports. |

---

## Config flags

Some permissions are configured by setting flags in the `config` of a `JourneyStep`,
rather than by group membership.

### The capabilities

A membership resting at a step is granted whatever capabilities that step carries. There
are five, and they are independent — you can give someone any one without the others:

| Capability | What it grants |
|---|---|
| **Edit content** | Edit the holon's fields, info fields, logo and media; create child holons; appear on its team roster |
| **Manage team** | Add, change and remove memberships on the holon — who is on the team and where they sit on their journey |
| **Manage people** | Edit the Person records of people who belong to the holon, or to any holon beneath it |
| **View private** | See holons whose class marks its composition private |
| **Manage logins** | Create and reset the login of a person who belongs to the holon, or to any holon beneath it |

**All five reach holons underneath.** A capability granted on a gathering applies to its
camps, and to the experiences under those. It never works the other way: standing on a camp
gives you nothing on the gathering above it.

Four of these five replaced a single flag, `team-active`, which granted all four at once —
a camp leader who should manage their camp's schedule necessarily also got edit rights on
every person in the camp. Existing team steps were migrated to carry those four, and only
those four: **manage logins** was never part of `team-active`, and no step carries it until
someone ticks it. So nobody's access changed, except in one approved way: **manage
people** now reaches people who belong only to holons *beneath* the one it was granted
on, where before it stopped at the exact holon.

**Setting it:** capabilities are granted in the Django admin and nowhere else. Open the
journey step (journey page → pencil icon → **Journey steps**, or the step's own admin page)
and tick the capabilities. Each checkbox is labelled with what it grants and whether it
reaches holons underneath. Saving leaves everything else on the step — its colours in
particular — untouched.

**Who holds what:** a holon's admin page links to a read-only list of every person with a
capability on it, the membership granting it, and whether it came from the holon itself or
from an ancestor.

### `private_memberships` (on a holon class)

Set in a **holon class's** `config`, not a journey step's. It marks that class's
composition private: who belongs to a holon of this class, and the workflow they are in,
are readable only by someone who holds **view private** on that holon (or a global
editor). Everyone else gets a 403 on the holon's page and on its Team panel, and the
holon does not appear in search results or listings.

```json
{"private_memberships": true}
```

**Turning it off** takes the JSON boolean `false`, and only that. Unlike a
capability — where anything but boolean `true` reads as unset — this flag
fails *closed*: `null`, `0`, `""` and the string `"true"` all leave the class
private. A privacy flag that misreads as "public" is the expensive direction to
be wrong in. Remove the key entirely to go back to inheriting.

Two things follow that are easy to get wrong:

- **It is inherited.** A subclass of a private class is private too, whether or not it
  repeats the flag. Both the per-object check and the queryset filter resolve it through
  the class tree, so they cannot disagree about a subclass.
- **It hides the holon, and grants nothing.** Named for what it protects — who
  belongs to the holon — but enforcement covers the record too: the detail page
  and every partial under it return 403, and the name is withheld from search,
  mentions, listings and the CSV/email exports. What it never does is grant
  rights: it is a visibility flag, not a role.

The Outreach network and list classes use it: a network holds the operator's entire
LinkedIn graph, and a list holds who they are approaching.

### Display flags are not permission flags

Not every config flag grants access. `public-visible` (below) controls only what is
*shown* on the public site and grants no edit rights. Keep the two ideas apart: don't
reach for a capability to make something public. Asking a display flag as if it were a
permission is refused outright, so the two cannot quietly merge again.

---

## Public visibility (`public-visible`)

**This is not a permission.** It decides what the public `/view` site publishes, and
grants no access to anything.

| Where set | Effect |
|---|---|
| On a `JourneyStep` | A flow resting on this step is publishable. Use for one public stage of an otherwise internal journey. |
| On a `Journey` | **Every** step of the journey is publishable. Use when the whole pipeline is public. |

The two are ORed: a flow publishes if either its current step or its journey carries the
flag. The value must be the boolean `true` (same rule as a capability).

Publishing used to happen as a side effect of `team-active`: granting someone edit access
also put every membership on that step onto the public site. It is now an explicit setting,
independent of every capability.

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
or `trusted_editors`. "Scoped team member" = a person whose membership grants the relevant
capability on the holon **or on any of its ancestors**.

### Holons

One canonical rule — **"can edit this holon's content"** — governs a holon's fields, its
memberships, and its relationships. It passes for global editors and for scoped team
members of the holon **or any of its ancestors**.

| Action | Who can do it |
|---|---|
| View a holon's notes / activity | Anyone who can edit that holon |
| View a holon's change history | Anyone who can edit that holon |
| Edit a holon's fields, logo, and configuration | Anyone who can edit the holon's content |
| Manage a holon's team (add/remove members, edit or move a membership's journey step) | Anyone with **manage team** on the holon or an ancestor |
| Add / edit / delete holon relationships, and move a relationship's journey step | Anyone who can edit the content of **either endpoint** of the relationship |
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
| Add a person to the CRM | Global editors, or anyone with **manage people** on **any** holon |
| Edit a person | Global editors; the person themselves; anyone with **manage people** on a holon that person belongs to, or on a holon above it |
| View a person's change history | Anyone who can edit that person |
| Delete a person | Superusers and staff only |

Adding a person asks only that you run *something* — a camp lead enrolling a
participant, a conversation host adding a guest. It used to ask for standing on
a **domain**-type holon, which refused camp leads: a camp is a different class,
and the check was an exact class match. Handing that person a **login** is a
separate, narrower question — see below.

### Journeys and users

| Action | Who can do it |
|---|---|
| Manage journeys (journey editor, Journeys settings, creating and duplicating a journey in the shared catalog) | Global editors only |
| Edit a journey and its steps | Global editors, or anyone who can edit content on the **single holon that carries it** — provided no class offers it |
| Create or reset a person's **login** | Global editors, or anyone with **manage logins** on a holon that person belongs to, or on a holon above it — except when the person is themselves a global editor |
| Run CSV imports | Superusers and members of `csv_importers` |

**A journey belongs to one holon, or to nobody.** A scoped editor may rewrite a journey
only when exactly one holon carries it and no class offers it to others — that journey is
that holon's own working sequence. The moment a second holon runs it, or a class offers it
to every holon of that class, it is shared: shared journeys belong to global editors,
because a step renamed in one place would change what everyone else is looking at.

A brand-new journey has no holon at all, which is why *creating* one — and *duplicating*
one into the shared catalog — stays with global editors. A Coherence event team duplicates
through their own route instead, which attaches the copy to their event.

**Manage logins, in plain terms.** Ticking **Manage logins** on a journey step lets
everyone sitting at that step create a login for, and reset the password of, anyone who
belongs to their holon — and to every holon underneath it. A gathering-level grant covers
its camps; a camp-level grant covers only that camp, never the gathering above it.

It never applies to a full administrator. If the person whose password you are trying to
reset is a superuser, staff, or a trusted editor, you are told *"Only a full administrator
can manage the login of another administrator"*, however much standing you have. That is
deliberate: without it, a camp-level right could be turned into administrator access by
resetting an administrator's password and signing in as them.

It also never applies to someone in no holon at all — there is no holon for the grant to
reach, so only a global editor can give that person a login.

**Nobody holds it until it is ticked.** No step carries **Manage logins** out of the box.
Until an administrator ticks it on a step, creating and resetting logins stays exactly
where it was: global editors only.

### Coherence

| Action | Who can do it |
|---|---|
| Access Coherence (conversations, transcripts, journeys) | Superusers and members of `coherence_users` only |

Coherence access is a deliberate opt-in: it does **not** follow from `is_staff` or
`trusted_editors`. The Coherence navigation item and all Coherence-related sections
(profile, person detail, holon detail, note links) appear only for users with Coherence
access.

Coherence access is a **door, not a permission**. Being in `coherence_users` lets you
reach the Coherence screens; what you may change once you are there is the same question
as everywhere else — can you edit the event holon the conversation belongs to. Group
membership on its own grants no editing.

---

## What different users see

**Global editors** land on the Activity / dashboard page and see the operational
navigation (Activity, Calendar, Kanban), the Journeys settings card, the Chrome extension
download card, and the option to clear focus (view "All").

**Scoped users** (team members without global edit access) are taken to the detail page of
the first holon they hold **edit content** on. Their focus is scoped to their team holons
and those holons' ancestors. If they hold it nowhere, they remain on the landing page.
