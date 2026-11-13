# METIS — lookups and reads

Read with the main `metis` skill. Notes for finding and listing records.

- **Holon class for a "gathering":** there is no `gathering` class — `GET /holons?class=...`
  rejects it with a `validation_error` listing valid slugs. A top-level gathering event (e.g.
  "2026 USA California") is class `local_gathering`. Use `GET /holons?class=local_gathering`
  (optionally with `q=...`) to find one; `GET /classes?object_kind=holon` lists all valid slugs
  if a class guess like this one gets rejected again in the future.
- **Listing a holon's children:** `GET /holons?parent=<id>` alone 400s ("At least one of q or
  class must be provided") — add a class, e.g. `class=camp&parent=2` or `class=holon&parent=2`
  for every child. `limit` max is 100 (422 above that).
- **Relationship list shape:** `GET /holons/{id}/relationships` items use `relationship_id`,
  `from_holon`, `to_holon`, `journey_name`, `step_title` (not `source`/`target`/`journey_slug`).
  Org↔camp links are relationships between the two holons, not memberships.
- **"People for outreach" means the `To Contact` step only, not the whole Outreach journey.**
  When the user asks how many people are "for outreach" / "awaiting outreach" on a holon
  without naming a step, filter `GET /holons/{holon_id}/memberships` results (or count) down
  to `step_slug=to_contact` on the `person-outreach` journey. Other steps on that journey
  (`Personal Message`, `Invited`, `In Conversation`, etc.) are people already in progress, not
  waiting to be contacted — including them inflates the count and the "first N" list with
  people who shouldn't be messaged again.

- **Editing a Person's contact details (email, phone, etc.):** the API can't do it, since
  `/people/{id}` is GET-only (checked against the live schema on 2026-10-13). Use the web app
  in Chrome instead. The person page is `/core/person/{id}/`, not `/people/{id}/` or
  `/core/people/{id}/`, which both 404. Clicking the CONTACT field runs
  `hx-get=/person/{id}/field/contact/edit/`, which swaps a form into `#field-contact`
  (inputs `email`, `phone`, `whatsapp`, `linkedin`, …, and a `Save` button). There is
  only one email field, so record extra addresses as a note
  (`POST /memberships/{id}/update` with just `note`). Afterwards, check with
  `GET /people/{id}` that `contact` changed.
