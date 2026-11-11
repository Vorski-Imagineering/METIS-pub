# METIS — journeys and memberships

Read with the main `metis` skill. Notes for creating journeys, offering them on holons, and placing or moving people.

- **Creating a journey: the API can't, the browser can.** `/api/v1/journeys` is read-only, so
  use the web journey editor via the Chrome connector. The agent's tab is normally
  `document.hidden`: typed text doesn't land, and htmx forms (Add Step) send nothing ("Transition
  was aborted") yet clear the input, so it looks like it worked. Instead, drive it with
  `javascript_tool`:
  1. `/journey/new/`: set `select` (class; Person = `5`), `input[name=name]`,
     `input[name=slug]` (it isn't auto-filled from script), then `form.requestSubmit()`. This
     is a plain POST and redirects to `/app/metis/journey/{pk}/`. **Note the pk**.
  2. Steps: `await fetch('/journey/{pk}/step/create/', {method:'POST', body: FormData{csrfmiddlewaretoken, title}, headers:{'X-CSRFToken':csrf,'HX-Request':'true'}})`,
     one at a time in order. The slug comes from the title (`Bought Ticket` → `bought-ticket`).
     New steps always go **last**.
  3. Reorder: POST `/journey/{pk}/step/reorder/` with FormData `step_ids[]` (the step PKs from
     `.step-row[data-step-id]`, in the new order) and an `X-CSRFToken` header. It returns 204.
  4. Verify with `GET /journeys/{slug}`. The editor page stays stale until reloaded.
- **Offering a new person journey on one holon:** `POST /holons/{id}/update` with
  `journey_ids: [pk, …]` + `note` (global edit access). This is a **full replace of the
  directly assigned journeys**, so first list
  `GET /holons/{id}/journeys?object_kind=person` and `?object_kind=holon`, then keep every
  item with `offered_by: "holon"` (`"class"` items come from the class catalog and are
  unaffected). Afterwards the journey shows `offered_by: "holon"`. Confirm with the
  bogus-person bulk-add probe below. Its body is `{"journey": slug, "items": [{"person_id": …}]}`
  (the journey goes at the top level, not per item).
- **`relationships:bulk-add` → `journey_not_offered`:** holon journeys are offered by *class*
  (`GET /holons/{id}/journeys?object_kind=holon` shows `offered_by`). Holons of the same
  gathering can carry different classes (e.g. 2022 Portugal camps are split between
  `camp_pt_legacy` and `camp`), so a journey used on sibling links may be refused. The API
  can't change a holon's class — that's a web-app fix. Don't substitute another journey, and
  don't use `journey_ids` on `/holons/{id}/update` as a workaround: it's a full replace, and
  journey PKs aren't exposed.
- **Checking whether a journey is valid on a given holon, without side effects:** call
  `memberships:bulk-add` with a bogus `person_id` (e.g. `999999999`). The response
  distinguishes cleanly: `"Journey is not allowed on this Holon"` (journey invalid there) vs
  `"Person not found"` (journey is fine, your real person_id will work). Much faster than
  guessing and creating throwaway records.
- **Moving a person to a different Journey on the same Holon** (e.g. "move everyone on
  Journey A to Journey B"): `memberships:bulk-add` only *creates* new memberships — it is
  not a move and leaves the old membership in place. The actual move is
  `POST /memberships/{membership_id}/update` with `journey_slug` + `step_slug` set (mutually
  exclusive with `advance_step`). This reassigns the existing membership in place — no
  duplicate row, no separate delete step needed. `step_slug` must be an active step on the
  *target* journey (fetch via `GET /journeys/{slug}` to pick one); the call 400s if the person
  already has another membership on that target journey for the same holon.
- **Adding a Person to two holons at once:** `POST /people`'s `membership` field only accepts
  one holon. Create the Person with the primary membership + note, then call
  `POST /holons/{other_holon_id}/memberships:bulk-add` for the same `person_id` to add the second.
- **Web class list:** `https://app.the-gathering.earth/classes/` (root path —
  `/app/metis/classes/` is a 404). Per-class pages are under `/classes/{object_kind}/{slug}`.
