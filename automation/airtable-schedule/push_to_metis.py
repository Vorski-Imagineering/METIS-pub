#!/usr/bin/env python3
"""Load the downloaded Airtable programme into METIS as published experiences.

Reads schedule.json (from airtable_schedule.py) and keeps one experience per Airtable session
under the 2026 USA California gathering (226). Airtable is the source of truth for the fields
this script owns; every run overwrites them.

Usage:
  python3 push_to_metis.py                 # dry run: print the plan, write nothing
  python3 push_to_metis.py --apply         # carry the plan out
  python3 push_to_metis.py --schedule FILE # read a schedule.json other than output/airtable-schedule/

Each session is matched to its experience by `links.source` (`<share url>#<record id>`), so
re-runs update rather than duplicate. A session's owner is its first camp in `owners.json`;
a session with no camp, or only camps mapped to the gathering, is owned by the gathering.
A session that leaves Airtable is moved back to the programme's non-public first step.
"""
import argparse
import html
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / "regenworld-sync"))
from regenworld_sync import Metis, plain  # noqa: E402

PROGRAMME_JOURNEY_NAME = "Experience Programme"
LIVE_STEP, LIVE_STEP_TITLE = "published", "Published"
HIDDEN_STEP = "idea"
TAG_FIELD = "tags"
WHERE_FIELD = "where"  # value is the place's id from owners.json "places"
NOTE = "airtable schedule sync"
WRITE_GAP_S = 0.3


def source_url(share_url, record_id):
    return f"{share_url}#{record_id}"


def owner_of(session, owners):
    """(holon id, camps named alongside it) for a session, or (None, unknown camp names)."""
    camps = session["camps"]
    unknown = [c for c in camps if c not in owners["camps"]]
    mapped = [c for c in camps if owners["camps"].get(c)]
    if unknown:
        return None, unknown
    owner = next((owners["camps"][c] for c in mapped if owners["camps"][c] != owners["gathering"]),
                 owners["gathering"])
    return owner, [c for c in camps if owners["camps"].get(c) != owner]


def description_html(session, also):
    """The Airtable text as paragraphs, with the other camps named first."""
    paras = []
    if also:
        paras.append("With " + " and ".join(also) + ".")
    paras += [p for p in session["description"].split("\n\n") if p.strip()]
    return "".join("<p>" + html.escape(p.strip()).replace("\n", "<br>") + "</p>" for p in paras)


def info_fields(session, class_fields, places=None):
    out = {}
    place = (places or {}).get(session.get("location"))
    if WHERE_FIELD in class_fields and place:
        out[WHERE_FIELD] = place
    if session.get("start"):
        out["start_date"], out["start_time"] = session["start"][:10], session["start"][11:16]
    if session.get("length"):  # METIS refuses a length of 0
        out["length"] = session["length"]
    if TAG_FIELD in class_fields and session.get("category"):
        out[TAG_FIELD] = [session["category"]]
    return out


def plan(sessions, existing, owners, share_url, class_fields):
    """Actions taking METIS from `existing` ({source: experience}) to `sessions`."""
    actions, warnings, seen = [], [], set()
    for s in sessions:
        if s["id"] in owners.get("skip", {}):
            continue  # left out on purpose; if it was published, it's unpublished below
        src = source_url(share_url, s["id"])
        seen.add(src)
        owner, also = owner_of(s, owners)
        if owner is None:
            warnings.append(f"{s['id']} {s['title']!r}: camp {also} not in owners.json — skipped")
            continue
        if s.get("location") and s["location"] not in owners.get("places", {}):
            warnings.append(f"{s['id']} {s['title']!r}: place {s['location']!r} not in owners.json — "
                            f"add it on the gathering's Places and to owners.json")
        want = {"name": s["title"], "description": description_html(s, also),
                "info_fields": info_fields(s, class_fields, owners.get("places"))}
        exp = existing.get(src)
        if exp is None:
            actions.append({"op": "create", "parent_id": owner, "source": src, **want})
            continue
        if exp["parent_id"] != owner:
            warnings.append(f"{s['id']} {s['title']!r}: owner is now {owner} but experience {exp['id']} "
                            f"is under {exp['parent_id']} — move it in the web app")
        changes = {}
        if exp["name"] != want["name"]:
            changes["name"] = want["name"]
        if plain(exp["description"] or "") != plain(want["description"]):
            changes["description"] = want["description"]
        stale = {k: v for k, v in want["info_fields"].items() if exp["info_fields"].get(k) != v}
        if stale:
            changes["info_fields"] = stale
        if changes:
            actions.append({"op": "update", "id": exp["id"], "title": s["title"], **changes})
        if exp.get("step") != LIVE_STEP_TITLE:
            actions.append({"op": "publish", "id": exp["id"], "title": s["title"]})
    for src, exp in existing.items():
        if src not in seen and exp.get("step") == LIVE_STEP_TITLE:
            actions.append({"op": "unpublish", "id": exp["id"], "title": exp["name"]})
    return actions, warnings


def load_existing(metis, owners, share_url):
    """Experiences under the gathering and its mapped camps that came from this share."""
    out = {}
    for parent in sorted({owners["gathering"], *(v for v in owners["camps"].values() if v)}):
        for exp in experiences_under(metis, parent):
            src = (exp.get("links") or {}).get("source", "")
            if isinstance(src, str) and src.startswith(share_url + "#"):
                exp["relationship_id"], exp["step"] = programme_step(metis, exp["id"], parent)
                out[src] = exp
    return out


def experiences_under(metis, parent):
    offset = 0
    while True:
        page = metis.get("/holons", **{"class": "experience", "parent": parent, "limit": 100, "offset": offset})
        yield from page["items"]
        if not page.get("has_more"):
            return
        offset += len(page["items"])


def programme_step(metis, exp_id, parent):
    rels = metis.get(f"/holons/{exp_id}/relationships")["items"]
    for r in rels:
        if r.get("journey_name") == PROGRAMME_JOURNEY_NAME and r["to_holon"]["id"] == parent:
            return r["relationship_id"], r.get("step_title")
    return None, None


def describe(a):
    if a["op"] == "create":
        f = a["info_fields"]
        when = f"{f.get('start_date')} {f.get('start_time')} +{f.get('length', '?')}m"
        return f"CREATE under {a['parent_id']}: {a['name']!r} ({when})"
    if a["op"] == "update":
        return f"UPDATE {a['id']} {a['title']!r}: {', '.join(k for k in a if k not in ('op', 'id', 'title'))}"
    return f"{a['op'].upper()} {a['id']} {a['title']!r}"


def apply(metis, actions, owners):
    for a in actions:
        if a["op"] == "create":
            exp = metis.post("/experiences", {
                "parent_id": a["parent_id"], "name": a["name"], "description": a["description"],
                "info_fields": a["info_fields"], "links": {"source": a["source"]}})["experience"]
            rel_id, _ = programme_step(metis, exp["id"], a["parent_id"])
            metis.post(f"/relationships/{rel_id}/update", {"step_slug": LIVE_STEP, "note": f"{NOTE}: published"})
        elif a["op"] == "update":
            metis.post(f"/holons/{a['id']}/update",
                       {k: v for k, v in a.items() if k in ("name", "description", "info_fields")})
        else:
            exp = metis.get(f"/holons/{a['id']}")
            rel_id, _ = programme_step(metis, a["id"], exp["parent_id"])
            step = LIVE_STEP if a["op"] == "publish" else HIDDEN_STEP
            metis.post(f"/relationships/{rel_id}/update", {"step_slug": step, "note": f"{NOTE}: {a['op']}"})
        print("done:", describe(a))
        time.sleep(WRITE_GAP_S)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write to METIS (default: dry run)")
    ap.add_argument("--schedule", type=Path, default=REPO_ROOT / "output" / "airtable-schedule" / "schedule.json")
    args = ap.parse_args()

    schedule = json.loads(args.schedule.read_text())
    owners = json.loads((HERE / "owners.json").read_text())
    share_url = schedule["meta"]["source"]
    metis = Metis(REPO_ROOT / ".env")
    exp_class = metis.get("/classes/holon/experience")
    class_fields = {f["key"] for g in exp_class["config"]["info_field_groups"] for f in g["fields"]}
    if TAG_FIELD not in class_fields:
        print(f"note: the experience class has no '{TAG_FIELD}' field yet, so categories aren't sent")

    existing = load_existing(metis, owners, share_url)
    actions, warnings = plan(schedule["sessions"], existing, owners, share_url, class_fields)
    for w in warnings:
        print("warning:", w)
    if not actions:
        print("in sync — nothing to do")
        return
    for a in actions:
        print(describe(a))
    counts = {op: sum(a["op"] == op for a in actions) for op in ("create", "update", "publish", "unpublish")}
    print(", ".join(f"{n} {op}" for op, n in counts.items() if n))
    if args.apply:
        apply(metis, actions, owners)
    else:
        print("dry run — nothing written. Re-run with --apply.")


if __name__ == "__main__":
    main()
