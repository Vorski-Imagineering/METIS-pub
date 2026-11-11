---
name: metis-admin
description: >
  Use when administering METIS configuration rather than its data — managing classes
  (holon/person/journey/space/step classes): renaming a class or its plural label, changing
  its icon or description, offering or removing journeys on a class, creating a new class or
  subclass, editing a class's config (info_field_groups / additional fields, detail_sections,
  views, link_fields, allowed child classes), or "why does every <class> show/lack X".
  Trigger on: "manage classes", "add a field to the camp class", "offer journey X on class Y",
  "create a subclass for ...", "change the class icon", "edit class config".
---

# METIS admin

Admin work changes **configuration that every record of a type inherits**. One save to a class
touches every holon of that class and every subclass that hasn't overridden the setting. That
is why this skill is separate from `metis` (which reads and writes individual records through
`/api/v1/`).

Admin is done **in the browser**, on the user's logged-in Chrome session, using the
`mcp__claude-in-chrome__*` tools (invoke the `claude-in-chrome` skill first). The `/api/v1/` API
can *read* classes (`GET /api/v1/classes`) but cannot change them.

## Routing

| Task | Read |
|---|---|
| Anything about classes: labels, icon, description, journeys on a class, new class/subclass, class config (info fields, sections, link fields, child classes) | `references/classes.md` |

Add a row and a new `references/<area>.md` as further admin areas are covered.

## Rules for every admin change

1. **Read before you write.** Capture the current value (label, selected journeys, or the full
   `config` JSON) and show it to the user before changing it, so the change can be reverted.
2. **Confirm the exact change with the user before saving**, naming the class and how many
   holons it affects (the class panel lists its members). Approval for one class does not
   carry over to another.
3. **Verify after saving** by reloading the class panel, or with `GET /api/v1/classes` (see the
   `metis` skill for auth), and report what changed.
4. Never use a Delete control on a class. Deactivating or deleting is out of scope: ask the
   user to do it themselves.
5. METIS is not LinkedIn, but still act like a person: no tight loops of page loads, and batch
   your reads into one script per page.
