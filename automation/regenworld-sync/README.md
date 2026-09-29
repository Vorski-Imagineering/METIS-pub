# regenworld.net → METIS camp sync

[regenworld.net](https://regenworld.net/) hosts The Gathering US (Camp Navarro, California,
October 2026), which METIS holds as the Local Gathering **2026 USA California** (id 226).
`regenworld_sync.py` reads the site and keeps that gathering and its camps in METIS up to date.

```
regenworld.net /gather/ + /camps/ → plan (site vs METIS) → dry run or --apply
```

The site is the source of truth for the fields the script owns. Every run overwrites them.

## What it syncs

- **Gathering (226):** `start_date` and `end_date` from the `/gather/` hero ("OCT 15 – 18,
  2026"), and `tickets` (the `/gather/` page itself). Place, tagline and description are left
  to people in METIS: the site's versions are less detailed than METIS's.
- **Camps:** each camp block on `/camps/` (an Elementor tabs widget: About, Schedule,
  Partners) becomes a `camp` holon under 226:
  - **New camps** are created with `POST /camps` on the `pt-2026-camps` journey, step
    **Selling**. They get the About text as their description, the logo uploaded at full
    size, a `source` link and, where the site embeds one, a `youtube` link.
  - **Existing camps** get their name and description overwritten from the site. The logo is
    re-uploaded only when the site's image URL changes (it's kept in the `logo_source` link).
    Links someone added by hand in METIS are kept.
  - **Camps that leave the site** are moved to the **Cancelled** step, which isn't public, so
    they drop off the public site and keep their history. If one comes back, it moves back to
    Selling.
- **Experiences:** not yet. Every camp's schedule tab still says "Coming Soon". When one has
  real content the script warns, and the parser gets written against the real format.

### How camps are matched

Each camp is found in METIS by its `source` link (`https://regenworld.net/camps/#<key>`,
looked up with `GET /holons?link=…&link_key=source`), so re-runs update rather than duplicate.

Camp names appear only inside the logo images on the site, and the text headings beside them
are copy-pasted (three say "CAMP AUDAX SCHEDULE"). So `camps.json` names each camp by the
`data-id` of its Elementor tabs widget:

```json
"443adb4": {"name": "Camp Kaizen", "key": "camp-kaizen"}
```

A camp block the file doesn't know is reported as **UNMAPPED**, with its logo and text, and
nothing is written for it. While any camp is unmapped, the script also refuses to cancel
anything: an unmapped block may be a known camp whose widget was rebuilt.

### Hidden camps

A camp block whose container carries `elementor-hidden-desktop`, `-tablet` and `-mobile` is
on the page but shown to nobody. It's treated as absent. On 29 Sep 2026 that was AUREA and
NERA Alliance Camp, which Golden Era Camp's text says it brings together.

### Exceptions: camps METIS owns

`camps.json` has an `exceptions` list of camp keys, each with a reason. The script never
creates, updates, re-logos, cancels or restores an excepted camp. **Camp Audax** (1708) is
on it: its description, logo and links are written in METIS from
[audax.earth](https://audax.earth/#camp), not taken from regenworld.

## Running it

Needs Python 3.9+ (standard library only) and the repo-root `.env` that
[`/metis-setup`](../metis/README.md) creates.

```bash
python3 automation/regenworld-sync/regenworld_sync.py            # dry run: print the plan, write nothing
python3 automation/regenworld-sync/regenworld_sync.py --apply    # carry the plan out
python3 automation/regenworld-sync/regenworld_sync.py --html-dir DIR   # parse saved gather.html/camps.html
```

A dry run prints the excepted camps, warnings (hidden, unmapped, schedules with content) and
each planned change. A run with nothing to do prints `in sync — nothing to do`. Always read the
dry run before `--apply`.

It fetches two pages from regenworld.net, 4 seconds apart.

## Gotchas it handles

- **METIS autolinks `word.Word`.** The site's CircleUp text has "world.In a world" (its
  paragraph is repeated with no space), and METIS turned it into a link to `http://world.In`.
  The parser puts a space after a sentence that runs straight into the next.
- **Descriptions are compared as text,** so markup METIS adds on save isn't seen as a change.
- **`links` is a full replace on update,** so the script merges its keys into the existing
  links instead of sending its own alone.
- **A logo's `logo_source` is recorded only after the upload succeeds,** so a failed upload is
  retried on the next run.

## Tests

```bash
cd automation/regenworld-sync && python3 -m unittest discover -s tests
```
