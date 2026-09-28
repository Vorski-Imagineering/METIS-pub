# Sola → METIS experience scan

The 2024 Portugal Gathering's experiences were imported into METIS from
[Sola](https://sola.day) as `experience_pt2024` holons, with dates but no times and no people.
`sola_scan.py` re-reads each experience's Sola event page (its `source_url` field) and fills
in what the import left out.

```
METIS experience_pt2024 holons → source_url → sola.day event page → METIS updates
```

## What it writes

For each experience:

- **Times:** Sola stores start and end in UTC plus the event's timezone (`Europe/Lisbon`).
  The script converts to local gathering time and writes `start_date`, `start_time` and
  `length`: whole minutes from start to end, measured on the clock face, because that's how
  METIS works out the end (see [Experiences](../../docs-pub/metis_apps/gathering/experiences.md)).
  It only writes fields the holon's class declares, and METIS no longer accepts `end_date`, so
  the end date and time go only to the export.
- **People:** the event's `event_roles` (speaker, co-host, …) or, only when there are none,
  the account that posted the event (`owner`). Each name is looked up in METIS People. A match
  must be exactly one Person with that exact name, ignoring case. A matched Person gets an
  `experience-facilitator` membership on the experience, with a note naming the Sola event.
  No Persons are created. Sola names are often usernames or camp accounts, so expect most
  to come back unmatched.

The script sends each experience's other fields (`source_url`, `tags`) back unchanged with
the update, so they're kept.

Only events Sola marks `published` are written. Any other status (for example a cancelled
event) is skipped and listed under "Not written". Images and descriptions are not re-read,
because the original import already brought those in.

## Running it

Needs Python 3.9+ (standard library only) and the repo-root `.env` that
[`/metis-setup`](../metis/README.md) creates.

```bash
python3 automation/sola-import/sola_scan.py --dry-run --limit 10   # show planned writes only
python3 automation/sola-import/sola_scan.py --limit 10             # write the first 10 (by name)
python3 automation/sola-import/sola_scan.py                        # all experience_pt2024 holons
python3 automation/sola-import/sola_scan.py --ids 1411,1676        # specific experiences
```

It prints one line per experience, then a summary listing:

- the **unmatched people** (experience id, Sola role, Sola name), which are the input for
  the backfill pass
- experiences it **couldn't scan** (no `source_url`, or no event on the Sola page)
- any **errors** from METIS

Add `--export ~/Documents/sola-scan.csv` to also write one CSV row per experience: METIS id,
name and parent camp, Sola URL and status, local start/end date and time (including
`end_time`, even while METIS can't store it), the Sola **venue** as text, matched and
unmatched people, and what happened. The file must be outside this repo, because the repo
is public and the file holds people's names. The script refuses a path inside it. Rows are
written as the run goes, so an interrupted run still leaves a usable file.

Re-running is safe. Times already set are left alone, and a membership that already exists
is reported as `already_present`. The backfill pass is simply a re-run with `--ids` once the
missing people exist in METIS.

## Being polite to Sola

The script waits a random, human-like interval between Sola pages, averaging about 4
seconds, so a full run of ~366 experiences takes about 25 minutes. It stops after 3 failed
Sola pages in a row rather than pushing through a possible throttle or outage.

Sola answers `200` even for an event that doesn't exist, so the script judges a page by
whether it contains the event data, not by its status code.

## Tests

```bash
cd automation/sola-import && python3 -m unittest discover -s tests
```
