#!/usr/bin/env python3
"""Download The Gathering US programme from its shared Airtable interface page.

The page (https://airtable.com/app9ngdcZg3Rip0ID/shryVYkmxQwkfz2ky) loads every session,
description included, from one internal endpoint, `readForSharedPages`. This script calls
that endpoint, so no browser and no clicking through records is needed.

Usage:
  python3 airtable_schedule.py                   # fetch, write schedule.json + schedule.csv
  python3 airtable_schedule.py --out DIR         # write somewhere other than output/airtable-schedule
  python3 airtable_schedule.py --raw FILE        # parse a saved response instead of fetching

The endpoint needs the signed access policy the page itself sends; `share.json` holds it. It
expires (see `share.json`), and then the fetch fails with a message saying how to refresh it.
"""
import argparse
import csv
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
SHARE_FILE = HERE / "share.json"
ENDPOINT = "https://airtable.com/v0.3/application/{app}/readForSharedPages"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0 Safari/537.36"
)
TIMEZONE = "America/Los_Angeles"

# Airtable column name -> output key
KEYS = {
    "Session Name": "title",
    "Day": "day",
    "Start Time": "start",
    "End Time": "end",
    "Location/Area": "location",
    "Camp Name": "camps",
    "Category": "category",
    "Program Description (150-word max)": "description",
}
CSV_FIELDS = ["id", "day", "start", "end", "length", "title", "location", "camps", "category", "description"]

REFRESH_HELP = """\
The signed access policy in share.json has expired or been revoked. To refresh it:
  1. Open {url} in Chrome.
  2. In DevTools > Network, find the request to readForSharedPages.
  3. Copy its accessPolicy and stringifiedObjectParams query values (URL-decoded JSON)
     into share.json, and update "expires".
"""


def fetch(share):
    params = dict(share["params"], allowMsgpackOfResultIfEnabled=False)
    qs = urllib.parse.urlencode({
        "stringifiedObjectParams": json.dumps(params, separators=(",", ":")),
        "accessPolicy": json.dumps(share["accessPolicy"], separators=(",", ":")),
    })
    req = urllib.request.Request(ENDPOINT.format(app=share["applicationId"]) + "?" + qs, headers={
        "User-Agent": USER_AGENT,
        "x-airtable-application-id": share["applicationId"],
        "x-requested-with": "XMLHttpRequest",
        "x-time-zone": "UTC",
        "x-user-locale": "en",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code in (401, 403, 422):
            sys.exit(f"Airtable refused the request ({e.code}).\n" + REFRESH_HELP.format(url=share["url"]))
        raise


def wall_clock(value):
    """Airtable stores these times as UTC, but they are the gathering's local clock time:
    the 8:00 AM yoga is `...T08:00:00.000Z`. Keep the clock time and drop the fake Z."""
    return value[:16] if value else None


def minutes_between(start, end):
    if not (start and end):
        return None
    fmt = "%Y-%m-%dT%H:%M"
    return int((datetime.strptime(end, fmt) - datetime.strptime(start, fmt)).total_seconds() // 60)


def parse(response):
    """Return the sessions in `response`, in the page's order, with select ids resolved."""
    data = response["data"]
    preload = data["preloadPageQueryResults"]
    query = preload["querySlices"][0]
    table_id = query["tableId"]
    schema = next(s for s in data["tableSchemas"] if s["id"] == table_id)
    columns = {c["id"]: c for c in schema["columns"]}
    rows = preload["tableDataById"][table_id]["partialRowById"]

    sessions = []
    for row_id in query["rowIds"]:
        cells = rows[row_id]["cellValuesByColumnId"]
        session = {"id": row_id}
        for col_id, col in columns.items():
            value = cells.get(col_id)
            if value is not None:
                if col["type"] == "select":
                    value = col["typeOptions"]["choices"][value]["name"]
                elif col["type"] == "foreignKey":
                    value = [link["foreignRowDisplayName"].strip() for link in value]
                elif col["type"] == "date":
                    value = wall_clock(value)
            if isinstance(value, str):
                value = value.strip()
            session[KEYS.get(col["name"], col["name"])] = value
        session["camps"] = session.get("camps") or []
        session["length"] = minutes_between(session.get("start"), session.get("end"))
        sessions.append(session)
    sessions.sort(key=lambda s: (s.get("start") or "", s.get("title") or ""))
    return sessions


def warnings(sessions):
    """Things worth a look before the data goes anywhere public."""
    out = []
    seen = {}
    for s in sessions:
        for key in ("title", "day", "start", "end", "location", "description"):
            if not s.get(key):
                out.append(f"{s['id']} {s.get('title')!r}: no {key}")
        if s["length"] is not None and s["length"] < 0:
            out.append(f"{s['id']} {s['title']!r}: ends before it starts")
        elif s["length"] == 0:
            out.append(f"{s['id']} {s['title']!r}: starts and ends at the same time")
        k = (s.get("title"), s.get("start"), s.get("location"))
        if k in seen:
            out.append(f"{s['id']} {s['title']!r}: same title, start and place as {seen[k]}")
        seen.setdefault(k, s["id"])
    return out


def write(sessions, out_dir, source):
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {"source": source, "timezone": TIMEZONE, "count": len(sessions)}
    (out_dir / "schedule.json").write_text(
        json.dumps({"meta": meta, "sessions": sessions}, ensure_ascii=False, indent=2) + "\n")
    with open(out_dir / "schedule.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader()
        for s in sessions:
            w.writerow({**{k: s.get(k) for k in CSV_FIELDS}, "camps": "; ".join(s["camps"])})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=REPO_ROOT / "output" / "airtable-schedule")
    ap.add_argument("--raw", type=Path, help="parse this saved readForSharedPages response instead of fetching")
    args = ap.parse_args()

    share = json.loads(SHARE_FILE.read_text())
    if args.raw:
        response = json.loads(args.raw.read_text())
    else:
        response = fetch(share)
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / "raw.json").write_text(json.dumps(response, ensure_ascii=False))

    sessions = parse(response)
    write(sessions, args.out, share["url"])
    for line in warnings(sessions):
        print("warning:", line)
    days = sorted({s["day"] for s in sessions if s.get("day")}, key=lambda d: d.split()[-1])
    print(f"{len(sessions)} sessions over {len(days)} days ({', '.join(days)}) -> {args.out}")


if __name__ == "__main__":
    main()
