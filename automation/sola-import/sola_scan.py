#!/usr/bin/env python3
"""Re-scan Sola event pages for METIS experiences: write local start/end times, attach matched people.

Usage:
  python3 sola_scan.py --dry-run --limit 10
  python3 sola_scan.py --ids 1411,1676
  python3 sola_scan.py                      # every experience_pt2024 holon
  python3 sola_scan.py --export ~/Documents/sola-scan.csv   # also write a CSV (venue, times, people)
"""
import argparse
import csv
import json
import math
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

METIS_URL = "https://app.the-gathering.earth/api/v1"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0 Safari/537.36"
)
DEFAULT_TZ = "Europe/Lisbon"
JOURNEY = "experience-facilitator"
MAX_CONSECUTIVE_SOLA_FAILURES = 3
REPO_ROOT = Path(__file__).resolve().parents[2]

_PUSH_RE = re.compile(r'\.rsc\.push\(("(?:[^"\\]|\\.)*")\)')


def human_delay(mean_ms, min_ms, max_ms):
    # Same shifted-exponential scheme as humanDelay in the linkedin-automation skill.
    scale = max(1, (mean_ms - min_ms) / 1.2)
    d = min_ms - scale * math.log(1 - random.random())
    if random.random() < 0.1:
        d += -scale * 2 * math.log(1 - random.random())
    return min(max_ms, round(d))


def normalize_url(url):
    return url.replace("://app.sola.day/", "://sola.day/", 1)


def parse_event(html):
    text = "".join(json.loads(lit) for lit in _PUSH_RE.findall(html))
    anchor = text.find('"event_roles":')
    if anchor < 0:
        return None
    decoder = json.JSONDecoder()
    pos = anchor
    while True:
        pos = text.rfind("{", 0, pos)
        if pos < 0:
            return None
        try:
            obj, _ = decoder.raw_decode(text, pos)
        except ValueError:
            continue
        if isinstance(obj, dict) and "event_roles" in obj and "start_time" in obj:
            return obj


def _local(iso, tz):
    return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(tz)


def local_fields(event):
    tz = ZoneInfo(event.get("timezone") or DEFAULT_TZ)
    fields, wall = {}, {}
    for prefix in ("start", "end"):
        iso = event.get(f"{prefix}_time")
        if iso:
            dt = _local(iso, tz)
            wall[prefix] = dt.replace(tzinfo=None)
            fields[f"{prefix}_date"] = dt.strftime("%Y-%m-%d")
            fields[f"{prefix}_time"] = dt.strftime("%H:%M")
    if len(wall) == 2:
        # METIS reads an end as start + length on the clock face, so length is wall-clock, not elapsed.
        minutes = int((wall["end"] - wall["start"]).total_seconds() // 60)
        if minutes >= 1:
            fields["length"] = minutes
    return fields


def is_outage(exc):
    if isinstance(exc, urllib.error.HTTPError):
        return exc.code >= 500
    return isinstance(exc, (urllib.error.URLError, TimeoutError, ConnectionError))


def people_candidates(event):
    out, seen = [], set()
    for r in event.get("event_roles") or []:
        name = (r.get("display_name") or "").strip()
        if name and name.casefold() not in seen:
            seen.add(name.casefold())
            out.append((r.get("role") or "role", name))
    if not out:
        owner = event.get("owner") or {}
        name = (owner.get("nickname") or owner.get("name") or "").strip()
        if name:
            out.append(("owner", name))
    return out


def pick_match(name, people):
    want = name.strip().casefold()
    hits = [p for p in people if (p.get("name") or "").strip().casefold() == want]
    return hits[0] if len(hits) == 1 else None


def is_writable(event):
    return event.get("status") == "published"


def venue_text(event):
    return ((event.get("venue") or {}).get("name") or (event.get("place") or {}).get("name") or "").strip()


EXPORT_COLUMNS = [
    "holon_id", "name", "parent_id", "sola_url", "sola_status", "start_date", "start_time", "end_date",
    "end_time", "length", "venue", "people_matched", "people_unmatched", "result",
]


def export_row(holon, url, event, result, matched, unmatched):
    times = local_fields(event) if event else {}
    return {
        "holon_id": holon["id"],
        "name": holon["name"],
        "parent_id": holon.get("parent_id"),
        "sola_url": url,
        "sola_status": (event or {}).get("status") or "",
        **{k: times.get(k, "") for k in ("start_date", "start_time", "end_date", "end_time", "length")},
        "venue": venue_text(event) if event else "",
        "people_matched": "; ".join(f"{role}: {name} (#{p['id']})" for role, name, p in matched),
        "people_unmatched": "; ".join(f"{role}: {name}" for role, name in unmatched),
        "result": result,
    }


def plan_info_fields(existing, new, declared):
    current = {k: v for k, v in existing.items() if k in declared}
    payload = dict(current)
    skipped = []
    for k, v in new.items():
        if k in declared:
            payload[k] = v
        else:
            skipped.append(k)
    return (None if payload == current else payload), skipped


class Metis:
    def __init__(self, env_path):
        env = dict(
            line.split("=", 1) for line in Path(env_path).read_text().splitlines() if "=" in line and not line.startswith("#")
        )
        body = {"email": env["METIS_EMAIL"], "password": env["METIS_PASSWORD"]}
        resp = self._call("POST", "/auth/login", body, {"X-Metis-Api-Key": env["API_LOGIN_SECRET"]})
        self.token = resp["token"]

    def _call(self, method, path, body=None, headers=None):
        req = urllib.request.Request(
            METIS_URL + path,
            method=method,
            data=None if body is None else json.dumps(body).encode(),
            headers={"User-Agent": USER_AGENT, "Content-Type": "application/json", **(headers or {})},
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8", "replace"), strict=False)

    def get(self, path, **params):
        qs = "?" + urllib.parse.urlencode(params) if params else ""
        return self._call("GET", path + qs, headers={"Authorization": f"Bearer {self.token}"})

    def post(self, path, body):
        return self._call("POST", path, body, {"Authorization": f"Bearer {self.token}"})


def fetch_sola(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "replace")


def declared_keys(metis):
    return {
        c["slug"]: {f["key"] for g in c["config"].get("info_field_groups", []) for f in g["fields"] if f["type"] != "slideshow"}
        for c in metis.get("/classes", object_kind="holon")
    }


def load_holons(metis, cls, ids):
    if ids:
        return [metis.get(f"/holons/{i}") for i in ids]
    byid, offset = {}, 0
    while True:
        page = metis.get("/holons", **{"class": cls, "limit": 100, "offset": offset})
        for h in page["items"]:
            if h["type"] == cls:
                byid.setdefault(h["id"], h)
        if not page.get("has_more") or not page["items"]:
            break
        offset += 100
    return sorted(byid.values(), key=lambda h: (h["name"].casefold(), h["id"]))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="read and print planned writes, change nothing")
    ap.add_argument("--limit", type=int, help="only the first N experiences (by name)")
    ap.add_argument("--ids", help="comma-separated METIS holon ids instead of the whole class")
    ap.add_argument("--class", dest="cls", default="experience_pt2024", help="holon class to scan")
    ap.add_argument("--export", help="CSV file to write one row per experience (must be outside this repo)")
    ap.add_argument("--env", default=str(REPO_ROOT / ".env"))
    args = ap.parse_args()

    if args.export and Path(args.export).expanduser().resolve().is_relative_to(REPO_ROOT):
        sys.exit("--export must point outside the repo: it holds people's names and this repo is public.")

    metis = Metis(args.env)
    declared = declared_keys(metis)
    holons = load_holons(metis, args.cls, [int(i) for i in args.ids.split(",")] if args.ids else None)
    if args.limit:
        holons = holons[: args.limit]
    mode = "DRY RUN — no writes" if args.dry_run else "LIVE — writing to METIS"
    print(f"{len(holons)} experiences, {mode}\n")

    export_file = open(Path(args.export).expanduser(), "w", newline="") if args.export else None
    writer = csv.DictWriter(export_file, fieldnames=EXPORT_COLUMNS) if export_file else None
    if writer:
        writer.writeheader()

    stats = {"times_updated": 0, "times_unchanged": 0, "memberships_created": 0, "already_present": 0}
    unmatched_all, missing, errors, skipped_fields = [], [], [], set()
    person_cache = {}
    sola_failures = 0

    def record(h, url, event, result, matched=(), unmatched=()):
        if writer:
            writer.writerow(export_row(h, url, event, result, list(matched), list(unmatched)))
            export_file.flush()

    for n, h in enumerate(holons, 1):
        label = f"[{n}/{len(holons)}] {h['id']} {h['name'][:50]}"
        src = (h.get("info_fields") or {}).get("source_url")
        if not src:
            missing.append((h["id"], h["name"], "no source_url"))
            record(h, "", None, "no source_url")
            print(f"{label}: no source_url")
            continue
        if n > 1:
            time.sleep(human_delay(4000, 1500, 30000) / 1000)
        url = normalize_url(src)
        try:
            event = parse_event(fetch_sola(url))
        except (urllib.error.URLError, TimeoutError) as e:
            event, reason = None, f"fetch failed: {e}"
        else:
            reason = "no event on page"
        if not event:
            sola_failures += 1
            missing.append((h["id"], h["name"], f"{reason} ({url})"))
            record(h, url, None, reason)
            print(f"{label}: SOLA {reason}")
            if sola_failures >= MAX_CONSECUTIVE_SOLA_FAILURES:
                print(f"\nStopping: {sola_failures} Sola failures in a row — possible throttling or outage.")
                break
            continue
        sola_failures = 0

        if not is_writable(event):
            why = f"Sola status {event.get('status')!r}, not written"
            missing.append((h["id"], h["name"], why))
            record(h, url, event, why)
            print(f"{label}: {why}")
            continue

        try:
            parts = []
            new = local_fields(event)
            payload, skipped = plan_info_fields(h.get("info_fields") or {}, new, declared.get(h["type"], set()))
            skipped_fields.update(skipped)
            when = f"{new.get('start_date')} {new.get('start_time')}–{new.get('end_time')}"
            if payload is None:
                stats["times_unchanged"] += 1
                result = "unchanged"
                parts.append(f"times {when} unchanged")
            else:
                diff = ", ".join(f"{k}={v}" for k, v in payload.items() if (h.get("info_fields") or {}).get(k) != v)
            if payload is not None and args.dry_run:
                stats["times_updated"] += 1
                result = "would update"
                parts.append(f"times {when}, would set {diff}")
            elif payload is not None:
                try:
                    metis.post(f"/holons/{h['id']}/update", {"info_fields": payload})
                    stats["times_updated"] += 1
                    result = "updated"
                    parts.append(f"times {when}, set {diff}")
                except urllib.error.HTTPError as e:
                    if is_outage(e):
                        raise
                    errors.append((h["id"], f"update {e.code}: {e.read()[:200]!r}"))
                    result = f"update failed {e.code}"
                    parts.append(f"UPDATE FAILED {e.code}")

            matched, unmatched = [], []
            for role, name in people_candidates(event):
                if name not in person_cache:
                    person_cache[name] = metis.get("/people", q=name, limit=100)["items"] if len(name) >= 2 else []
                person = pick_match(name, person_cache[name])
                if person:
                    matched.append((role, name, person))
                else:
                    unmatched.append((role, name))
                    unmatched_all.append((h["id"], h["name"], role, name))
            if matched and not args.dry_run:
                items = [{"person_id": p["id"], "note": f"Matched from Sola event {url} (role: {role}, name: {name})"}
                         for role, name, p in matched]
                try:
                    resp = metis.post(f"/holons/{h['id']}/memberships:bulk-add", {"journey": JOURNEY, "items": items})
                    stats["memberships_created"] += resp.get("created", 0)
                    stats["already_present"] += resp.get("already_present", 0)
                    for it in resp.get("items", []):
                        if it.get("outcome") == "error":
                            errors.append((h["id"], f"membership person {it.get('person_id')}: {json.dumps(it)[:200]}"))
                except urllib.error.HTTPError as e:
                    if is_outage(e):
                        raise
                    errors.append((h["id"], f"bulk-add {e.code}: {e.read()[:200]!r}"))
            verb = "would add" if args.dry_run else "added"
            parts.append(f"people {len(matched)}/{len(matched) + len(unmatched)} matched"
                         + (f" ({verb} {', '.join(p['name'] for _, _, p in matched)})" if matched else ""))
            record(h, url, event, result, matched, unmatched)
            print(f"{label}: " + " | ".join(parts))
        except Exception as e:
            if not is_outage(e):
                raise
            outage = f"METIS unavailable ({e}) at {h['id']}"
            missing.append((h["id"], h["name"], outage))
            record(h, url, event, outage)
            print(f"{label}: {outage}\n\nStopping: METIS is not responding. Re-run to continue; finished items are skipped as unchanged.")
            break

    if export_file:
        export_file.close()

    print("\n=== Summary ===")
    for k, v in stats.items():
        print(f"{k}: {v}")
    if skipped_fields:
        print(f"fields not on the class, skipped: {sorted(skipped_fields)}")
    print(f"\nUnmatched people ({len(unmatched_all)}) — for the backfill pass:")
    for hid, hname, role, name in unmatched_all:
        print(f"  {hid} | {hname[:50]} | {role} | {name}")
    if missing:
        print(f"\nNot written ({len(missing)}):")
        for hid, hname, why in missing:
            print(f"  {hid} | {hname[:50]} | {why}")
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for hid, msg in errors:
            print(f"  {hid} | {msg}")
    if args.export:
        print(f"\nExport: {args.export}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
