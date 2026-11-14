# The Gathering US programme ← Airtable

The programme for The Gathering US (Camp Navarro, California, 15–18 October 2026) is kept in
an Airtable base and published as a shared interface page:
<https://airtable.com/app9ngdcZg3Rip0ID/shryVYkmxQwkfz2ky>.
Two scripts keep the METIS programme in step with it:

```
Airtable readForSharedPages → airtable_schedule.py → schedule.json + schedule.csv
                                                  → push_to_metis.py → published experiences
                                                                        under gathering 226
```

1. `airtable_schedule.py` downloads every session on that page, full description included.
2. `push_to_metis.py` makes each session a published experience on the
   [2026 USA California programme](https://app.the-gathering.earth/view/2026-usa-california/programme/).

Airtable is the source of truth: re-run both, in that order, whenever the organisers change
the schedule.

```bash
python3 automation/airtable-schedule/airtable_schedule.py
python3 automation/airtable-schedule/push_to_metis.py            # dry run: read the plan
python3 automation/airtable-schedule/push_to_metis.py --apply
```

## Downloading: `airtable_schedule.py`

Python 3.9+, standard library only. No browser or login is needed.

```bash
python3 automation/airtable-schedule/airtable_schedule.py              # fetch → output/airtable-schedule/
python3 automation/airtable-schedule/airtable_schedule.py --out DIR    # write somewhere else
python3 automation/airtable-schedule/airtable_schedule.py --raw FILE   # re-parse a saved raw.json
```

It prints a warning for each thing worth checking before the data goes public (a missing
field, two sessions with the same title, start and place, a session with no length), then a
one-line summary. Re-run it whenever the organisers change the schedule. Each run overwrites
the output.

### What it writes

`schedule.json` has `meta` (source, timezone, count) and `sessions`. Each session:

| Key | From Airtable | Notes |
|---|---|---|
| `id` | record id | Stable: use it to match sessions across runs. |
| `title` | Session Name | |
| `day` | Day | As Airtable labels it: `Friday 10/16`. |
| `start`, `end` | Start Time, End Time | Local clock time, `2026-10-16T08:00`. See below. |
| `length` | | Minutes from start to end. |
| `location` | Location/Area | |
| `camps` | Camp Name | A list: one session has three camps, about a third have none. |
| `category` | Category | |
| `description` | Program Description | Full text, newlines kept. |

`schedule.csv` has the same columns, with `camps` joined by `; `. `raw.json` is the untouched
Airtable response.

### How it works

The interface page loads all its records, with every field, in one call to Airtable's
internal endpoint `readForSharedPages`. Opening a record in the page shows nothing that
response doesn't already have. The script makes the same call.

That call needs the **signed access policy** the page sends, which is kept in `share.json`.
Airtable gives a new one only to a real browser: plain HTTP gets a generic page with no share
data in it. The policy expires on the date in `share.json` (`expires`). After that, the
script stops with refresh steps. In short: open the share link in Chrome, find the
`readForSharedPages` request in DevTools, and copy its `accessPolicy` and
`stringifiedObjectParams` into `share.json`.

### Gotchas it handles

- **The times aren't UTC.** Airtable stores them as UTC and shows them as UTC, but they're
  the gathering's local time: the "8:00–9:00 AM" morning yoga is stored as `08:00Z`. The
  script keeps the clock time and drops the `Z`. The gathering's timezone is
  America/Los_Angeles.
- **Select values come as ids** (`selJFqfDWtYqycsi1`). The script swaps them for their labels
  from the table schema.
- **Text has stray spaces and newlines** (`"Camp Kaizen Conference\n"`). Each value is trimmed.

## Uploading: `push_to_metis.py`

Needs the repo-root `.env` that [`/metis-setup`](../metis/README.md) creates. A dry run
prints the plan and writes nothing; `--apply` carries it out. A run with nothing to do prints
`in sync — nothing to do`.

### What it writes

For each session, one experience with:

- **name** and **description** from the session. The description is split into paragraphs.
  A session with more than one camp names the others first ("With Camp Synthesis and NERA
  Camp.").
- **Day**, **Starts** and **Length** (`start_date`, `start_time`, `length`) from its start
  and end. A zero length is left out, because METIS refuses it.
- **Where** (`where`) from its location. The API stores a place as its id (`502944f0b862`),
  not its name, so `owners.json` maps each Airtable location to its place id.
- **Tags** (`tags`) set to its category, but only once the experience class has a `tags`
  field. Until then the run prints a note and leaves the category out.
- `links.source` = `<share url>#<record id>`. This is how a later run finds it.

Then it moves the experience's **Experience Programme** relationship to **Published**, so it
shows on the public programme straight away.

Later runs update the name, description and When fields of sessions that changed, and
publish any that someone unpublished. A session that leaves Airtable, or is added to `skip`,
is moved back to **Idea**, which isn't public. It keeps its history and comes back if the
session returns.

### `owners.json`: owners and places

`camps` maps each Airtable camp name to a METIS holon id. A session goes under its first camp
that maps to a real camp. With no camp, or only **RegenWorld** (the organiser, not a camp),
it goes under the gathering itself (226). `null` means the camp isn't in METIS (NERA Camp),
so it's only named in the text.

A camp name the file doesn't know is a **warning**, and that session is skipped. Add the camp
to `owners.json` and re-run. If a session's camp changes after it was uploaded, the run warns
and leaves it. The API can't move an experience to another parent, so move it in the web app.

`places` maps each Airtable location to a place id on the gathering. The API can't list or
create places, so they were added on the gathering's **Places** section in the web app
(15 Oct 2026, one per Airtable location, names as in Airtable). The id is in each place's
edit link: `/app/gathering/holon/226/places/<id>/edit/`. A location that isn't in the map
is a warning, and that session is uploaded without a place. Add the place in the web app,
add its id here, and re-run.

`skip` lists record ids to leave off, with a reason. On 14 Oct 2026 that was the two "Camp
Kaizen Conference" sessions copied under RegenWorld, which repeat Camp Kaizen's own entries.

## Not done yet

- **Category as tags.** An admin adds a multi-select field with key `tags` to the
  experience class, with the Airtable categories as options (Speaker, Community Building,
  Entrepreneurship, Personal Transformation, Music, Ceremonies, Meal, AI, Governance, Food
  Systems). The next `push_to_metis.py --apply` fills it in. Airtable spells one category
  "Food Sytems", and a value that isn't an option is dropped silently, so fix the spelling
  in Airtable or use the misspelling as the option.
