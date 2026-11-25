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
  `from_holon`, `to_holon`, `journey_name`/`journey_slug`, `step_title`/`step_slug` (not `source`/`target`).
  Org↔camp links are relationships between the two holons, not memberships.
  It pages (`offset` until `has_more` is false) and filters by `journey`, `step_slug` and
  `direction` (`from`/`to`/`either`). Items carry `journey_slug` and `step_slug` too, so group
  by the slug: journey names aren't unique.
- **Unknown query parameters are a `400`**, and the error names the parameters the endpoint
  takes. Read that list instead of guessing.
- **A class filter includes subclasses:** `GET /holons?class=local_gathering` also returns
  holons of classes built on it, such as 2026 México (`the-gathering-mexico-2026`). Add
  `class_exact=true` to match that class only. Class reads give `parent_slug` and `ancestors`
  (nearest first).
- **Step flags are objects, not strings:** each step's `config_flags` (from `GET /journeys/{slug}`)
  is a list of `{key, value, kind, label, …}`. To test whether a step is public, check
  `any(f['key']=='public-visible' and f['value'] for f in step['config_flags'])`.
  `'public-visible' in flags` is always False, which makes every step look private.
- **Where a journey is offered:** `used_by` on `GET /journeys/{slug}`. Each entry has a `way`:
  `offered` means a class offers it (`class_slug`), and `offered_here` means one holon has it
  directly (`holon_id`).
- **"People for outreach" means the `To Contact` step only, not the whole Outreach journey.**
  When the user asks how many people are "for outreach" / "awaiting outreach" on a holon
  without naming a step, filter `GET /holons/{holon_id}/memberships` results (or count) down
  to `step_slug=to_contact` on the `person-outreach` journey. Other steps on that journey
  (`Personal Message`, `Invited`, `In Conversation`, etc.) are people already in progress, not
  waiting to be contacted — including them inflates the count and the "first N" list with
  people who shouldn't be messaged again.

- **Editing a Person's contact details (email, phone, etc.):** `POST /people/{id}/update`
  with `contact` (a partial merge: `null` removes a key) and an optional `note`. A person with
  a login can't have their email changed here (`403`). An email or LinkedIn already held by
  another Person is a `409`. Afterwards, check `contact` with `GET /people/{id}`.
