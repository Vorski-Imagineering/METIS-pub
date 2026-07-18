# Working with People & Orgs

The core CRM workflow: finding, adding, and tracking people and organisations. This pairs
with the concept references [Journeys](../../core/JOURNEY.md) and
[Holons and classes](holons-and-classes.md) — it's the "how do I actually do it" side.

Everything here is scoped by your current **Focus** — see
[Focus](../../web/app/focus-and-scoping.md) if a list looks emptier or fuller than you
expect.

---

## Finding a person or org

- **People** and **Orgs** in the sidenav open the list views for your current Focus.
- Lists have **filters** (including a "mine vs. all" style toggle and journey/step filters)
  and column controls; the filters you apply are reflected in the URL, so a filtered list is
  bookmarkable and shareable.
- **Search** (top of the sidenav) jumps straight to a specific person or holon by name.

## Adding a person or org

Use the add control on the relevant list to create a new person or organisation. When you're
**focused** on a holon, a new organisation you create is parented to that Focus (see
[Focus → Creating things while focused](../../web/app/focus-and-scoping.md#creating-things-while-focused)).

## The detail page

A person's or org's detail page shows its fields and sections. Which sections appear is
driven by the holon's **class** (see [Holons and classes](holons-and-classes.md)) — e.g.
Description, Links, People/Team, Additional fields, Events, Conversations, Children.

- **Inline editing** — most fields edit in place: click a field, change it, save. Changes
  apply immediately without a full page reload.
- **Additional fields** — custom structured fields configured on the class (including video
  embeds and photo slideshows). See [Additional fields](info-fields.md).

## Journeys & Memberships in practice

A **Journey** is a progression track; a person's or org's position on one is shown on their
profile as the current **step**.

- Moving someone through steps updates their Membership (for people ↔ holon) or the
  holon relationship (for org ↔ org).
- Some steps carry meaning beyond display — for example, a "team-active" step marks someone
  as an active team member, which affects sidebar Focus and edit rights. See
  [Access and permissions](../../core/access-and-permissions.md).

For the model behind this (journeys, steps, memberships, relationships), see
[Journeys](../../core/JOURNEY.md).

## Kanban board view

Where a list offers a **kanban** view, each column is a journey step and each card is a
person or org at that step. Drag a card to another column to move it to that step — the same
as changing the step on the profile.

## Comments and @mentions

You can leave **notes/comments** on a person or org. Typing `@` in a note opens a search of
People and Holons; picking one inserts a mention that renders as a styled pill and links to
that record. Mentions are a first-class reference, not just text — they connect the note to
the person or holon mentioned.

## Relationships between holons

Organisations can be related to other holons (org-to-org, org-to-event, …). These
relationships appear in the **Related Orgs** section of the detail page and, like
memberships, carry their own journey/step so you can track where a relationship stands.
Adding, editing, and removing relationships is a broad-editor action (see
[Access and permissions](../../core/access-and-permissions.md)).
