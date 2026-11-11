# METIS — creating and editing holons

Read with the main `metis` skill. Notes for writing Organisations, Camps and Experiences.

- **Creating holons: Organisations, Camps and Experiences.** A Local Gathering or any other
  class still needs a human in the METIS web app. Before telling the user a type can't be
  created, re-check the `POST` paths in the live `/api/v1/openapi.json` — this has changed twice.
  - `POST /holons` creates a top-level **Organisation** (`name` required). A name or link that
    already exists returns `409` naming the existing ids and writes nothing (#240).
  - `POST /camps` creates a **Camp** under `parent_id`. **`journey` is required at runtime even
    though the schema doesn't mark it** — for a 2026 gathering it's `pt-2026-camps` (step
    `selling` for a published camp; `GET /holons/{parent}/journeys?object_kind=holon` lists what's
    offered). Same name or same link under the same parent → `409` (#488).
  - `POST /experiences` creates an **Experience** under an existing Camp/Gathering. It takes
    `links` but does **not** refuse duplicates: look up first.
- **Finding a holon by an external source:** `GET /holons?class=…&parent=…&link=<url>&link_key=source`
  matches a link value exactly (the `#fragment` counts). Store the source URL in `links.source`
  when creating. `links` on `/holons/{id}/update` is a **full replace** — merge into the existing
  links, or you delete ones a human added.
- **Logos:** `POST /holons/{id}/logo`, multipart file field `logo` (jpeg/png/gif/webp, ≤5 MB).
  No URL form: download the image first.
- **Removing a camp or experience from the public site:** move its relationship to the
  `cancelled` step (`POST /relationships/{id}/update` with `step_slug` + `note`). Both the
  `pt-2026-camps` (Camp) and `experience-programme` journeys have one, not public. Moving back to
  a public step restores it. There is no delete.
- **Host orgs of a camp:** relationship camp → org on `26-camp-lead`, step `active`, via
  `POST /holons/{camp_id}/relationships:bulk-add` (safe to re-run: an existing pair returns
  `already_present`).
- **METIS autolinks `word.Word` in descriptions** (e.g. "world.In" became a link to
  `http://world.In`). Put a space after sentence ends in text you send, and compare
  descriptions as text, not HTML, since METIS adds markup on save.
