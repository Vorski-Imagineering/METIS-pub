#!/usr/bin/env python3
"""Sync regenworld.net (The Gathering US) into METIS: the gathering's dates and its camps.

The site is the source of truth for the fields this script owns; every run overwrites them.
Each camp is matched to its METIS holon by `links.source`, so any run can be repeated safely.

Usage:
  python3 regenworld_sync.py                 # dry run: print the plan, write nothing
  python3 regenworld_sync.py --apply         # carry the plan out
  python3 regenworld_sync.py --html-dir DIR  # parse saved gather.html/camps.html instead of fetching

Camp names only appear inside the logo images, so `camps.json` names each camp by the id of
its Elementor tabs widget. A camp the file doesn't know is reported and left alone. Its
`exceptions` list names camps (by key) that METIS owns: never created, updated or moved.
"""
import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

SITE = "https://regenworld.net"
METIS_URL = "https://app.the-gathering.earth/api/v1"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0 Safari/537.36"
)
GATHERING_ID = 226
CAMP_JOURNEY = "pt-2026-camps"
CAMP_JOURNEY_NAME = "Camp"
LIVE_STEP = "selling"
CANCELLED_STEP = "cancelled"
CAMP_CLASS = "camp"
NOTE = "regenworld.net sync"
FETCH_GAP_S = 4
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]

HIDDEN_EVERYWHERE = {"elementor-hidden-desktop", "elementor-hidden-tablet", "elementor-hidden-mobile"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
BLOCK = {"p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li", "section", "br"}
SKIP = {"script", "style", "noscript", "svg", "iframe", "button", "img"}
MONTHS = {m: i for i, m in enumerate(
    ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"], 1)}


# ---------------------------------------------------------------- HTML → tree

class Node:
    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.parent, self.children = tag, attrs, parent, []

    @property
    def classes(self):
        return set((self.attrs.get("class") or "").split())

    def walk(self):
        yield self
        for c in self.children:
            if isinstance(c, Node):
                yield from c.walk()

    def ancestors(self):
        n = self
        while n is not None:
            yield n
            n = n.parent


class _TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = self.cur = Node("#root", {}, None)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, {k: v or "" for k, v in attrs}, self.cur)
        self.cur.children.append(node)
        if tag not in VOID:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(Node(tag, {k: v or "" for k, v in attrs}, self.cur))

    def handle_endtag(self, tag):
        # Close back to the nearest open element of this tag; ignore stray end tags.
        for n in self.cur.ancestors():
            if n.tag == tag:
                self.cur = n.parent or self.root
                return

    def handle_data(self, data):
        self.cur.children.append(data)


def parse_html(text):
    b = _TreeBuilder()
    b.feed(text)
    return b.root


def blocks(node):
    """Text of `node` split into paragraphs at block-element boundaries."""
    out, buf = [], []

    def flush():
        t = re.sub(r"\s+", " ", "".join(buf)).strip()
        if t:
            out.append(t)
        buf.clear()

    def rec(n):
        for c in n.children:
            if isinstance(c, str):
                buf.append(c)
            elif c.tag in SKIP:
                continue
            elif c.tag in BLOCK:
                flush()
                rec(c)
                flush()
            else:
                rec(c)

    rec(node)
    flush()
    return out


def unglue(text):
    """'world.In a world' → 'world. In a world'; METIS would otherwise autolink 'world.In'."""
    return re.sub(r"([a-z])\.([A-Z][a-z])", r"\1. \2", text)


def plain(markup):
    """Visible text of stored HTML, so markup METIS adds on save (autolinks) isn't a change."""
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", markup or ""))).strip()


def full_size(url):
    """WordPress thumbnail URL → original upload (drop the -1024x839 size suffix)."""
    return re.sub(r"-\d+x\d+(\.\w+)$", r"\1", url)


# ---------------------------------------------------------------- site parsing

def parse_camps(page):
    """Every camp block on /camps/: one Elementor nested-tabs widget (About/Schedule/Partners)."""
    root = parse_html(page)
    camps = []
    for w in root.walk():
        if w.attrs.get("data-widget_type") != "nested-tabs.default":
            continue
        panels = [n for n in w.walk() if n.attrs.get("role") == "tabpanel"]
        titles = [" ".join(blocks(n)).upper() for n in w.walk() if n.attrs.get("role") == "tab"]
        about = panels[titles.index("ABOUT")] if "ABOUT" in titles else (panels[0] if panels else w)
        logo = next((n.attrs["src"] for n in about.walk()
                     if n.tag == "img" and "/wp-content/uploads/" in n.attrs.get("src", "")), None)
        video = next((n.attrs["src"] for n in about.walk()
                      if n.tag == "iframe" and "youtube.com/embed/" in n.attrs.get("src", "")), None)
        paras = [unglue(p) for p in blocks(about) if p not in ("Read More ▼", "Read More")]
        schedule = panels[titles.index("SCHEDULE")] if "SCHEDULE" in titles else None
        camps.append({
            "widget_id": w.attrs.get("data-id"),
            "hidden": any(HIDDEN_EVERYWHERE <= a.classes for a in w.ancestors()),
            "logo": full_size(logo) if logo else None,
            "video": "https://www.youtube.com/watch?v=" + video.split("/embed/")[1].split("?")[0] if video else None,
            "description": "".join(f"<p>{html.escape(p, quote=False)}</p>" for p in paras),
            "schedule_text": blocks(schedule) if schedule is not None else [],
        })
    return camps


def parse_gathering(page):
    """Dates from the /gather/ hero, e.g. 'OCT 15 – 18, 2026' or 'OCT 30 – NOV 2, 2026'."""
    text = " ".join(blocks(parse_html(page)))
    m = re.search(r"\b([A-Z]{3})\s+(\d{1,2})\s*[–-]\s*(?:([A-Z]{3})\s+)?(\d{1,2}),\s*(\d{4})", text)
    if not m or m.group(1) not in MONTHS:
        raise ValueError("no event date range found on /gather/")
    mon1, d1, mon2, d2, year = m.groups()
    start = date(int(year), MONTHS[mon1], int(d1))
    end = date(int(year), MONTHS[mon2 or mon1], int(d2))
    return {"start_date": start.isoformat(), "end_date": end.isoformat(), "tickets": f"{SITE}/gather/"}


# ---------------------------------------------------------------- METIS client

class Metis:
    def __init__(self, env_path):
        env = dict(line.split("=", 1) for line in Path(env_path).read_text().splitlines()
                   if "=" in line and not line.startswith("#"))
        body = {"email": env["METIS_EMAIL"], "password": env["METIS_PASSWORD"]}
        self.token = self._call("POST", "/auth/login", json.dumps(body).encode(),
                                {"X-Metis-Api-Key": env["API_LOGIN_SECRET"],
                                 "Content-Type": "application/json"})["token"]

    def _call(self, method, path, data=None, headers=None):
        req = urllib.request.Request(METIS_URL + path, method=method, data=data,
                                     headers={"User-Agent": USER_AGENT, **(headers or {})})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8", "replace"), strict=False)
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"{method} {path} -> {e.code}: {e.read().decode('utf-8', 'replace')[:400]}")

    def _auth(self, extra=None):
        return {"Authorization": f"Bearer {self.token}", **(extra or {})}

    def get(self, path, **params):
        qs = "?" + urllib.parse.urlencode(params) if params else ""
        return self._call("GET", path + qs, headers=self._auth())

    def post(self, path, body):
        return self._call("POST", path, json.dumps(body).encode(),
                          self._auth({"Content-Type": "application/json"}))

    def upload(self, path, field, filename, content, content_type):
        boundary = uuid.uuid4().hex
        data = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{field}\"; "
                f"filename=\"{filename}\"\r\nContent-Type: {content_type}\r\n\r\n").encode() \
            + content + f"\r\n--{boundary}--\r\n".encode()
        return self._call("POST", path, data,
                          self._auth({"Content-Type": f"multipart/form-data; boundary={boundary}"}))


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read(), r.headers.get_content_type()


# ---------------------------------------------------------------- planning

def source_url(key):
    return f"{SITE}/camps/#{key}"


def plan(site_camps, gathering_site, gathering_metis, metis_camps, relationships, mapping, exceptions=None):
    """Pure: compare site vs METIS and return (actions, warnings). No I/O.

    metis_camps: {holon_id: holon}; relationships: {holon_id: step_title} for camps on the
    Camp journey under the gathering; mapping: {widget_id: {"name", "key", ["metis_id"]}};
    exceptions: {key: reason} — camps this script never creates, updates or moves.
    """
    actions, warnings = [], []
    exceptions = exceptions or {}

    fields = {k: v for k, v in gathering_site.items()
              if (gathering_metis.get("info_fields") or {}).get(k) != v}
    if fields:
        actions.append({"op": "update_gathering", "id": gathering_metis["id"], "info_fields": fields,
                        "was": {k: (gathering_metis.get("info_fields") or {}).get(k) for k in fields}})

    by_source = {(h.get("links") or {}).get("source"): h for h in metis_camps.values()
                 if (h.get("links") or {}).get("source")}
    seen, unknown = set(), False
    for c in site_camps:
        entry = mapping.get(c["widget_id"])
        if entry and entry["key"] in exceptions:
            continue
        if c["hidden"]:
            warnings.append(f"hidden on the site, treated as absent: widget {c['widget_id']}"
                            f" ({entry['name'] if entry else 'unmapped'})")
            continue
        if not entry:
            unknown = True
            warnings.append(f"UNMAPPED camp widget {c['widget_id']} — add it to camps.json to sync it. "
                            f"logo={c['logo']} text={re.sub('<[^>]+>', ' ', c['description'])[:160]!r}")
            continue
        src = source_url(entry["key"])
        seen.add(src)
        want_links = {"source": src, **({"youtube": c["video"]} if c["video"] else {})}
        h = by_source.get(src) or metis_camps.get(entry.get("metis_id"))
        if h is None:
            actions.append({"op": "create_camp", "name": entry["name"], "description": c["description"],
                            "links": want_links, "logo": c["logo"]})
            continue
        if c["logo"] and (h.get("links") or {}).get("logo_source") != c["logo"]:
            actions.append({"op": "set_logo", "id": h["id"], "name": entry["name"], "logo": c["logo"]})
        links = {**(h.get("links") or {}), **want_links}
        change = {}
        if h["name"] != entry["name"]:
            change["name"] = entry["name"]
        if plain(h.get("description")) != plain(c["description"]):
            change["description"] = c["description"]
        if links != (h.get("links") or {}):
            change["links"] = links
        if change:
            actions.append({"op": "update_camp", "id": h["id"], "name": h["name"], "set": change})
        step = relationships.get(h["id"])
        if step is None:
            warnings.append(f"{entry['name']} (#{h['id']}) has no '{CAMP_JOURNEY_NAME}' relationship"
                            f" to the gathering; not touching its step")
        elif step.casefold() == CANCELLED_STEP:
            actions.append({"op": "set_step", "id": h["id"], "name": entry["name"], "step": LIVE_STEP,
                            "why": "back on the site"})
        if c["schedule_text"] and not any("coming soon" in t.casefold() for t in c["schedule_text"]):
            warnings.append(f"{entry['name']}: schedule tab has content — experiences are not synced yet")

    excepted_sources = {source_url(k) for k in exceptions}
    for src, h in by_source.items():
        if src.startswith(f"{SITE}/camps/#") and src not in seen and src not in excepted_sources:
            step = relationships.get(h["id"])
            if unknown:
                warnings.append(f"{h['name']} (#{h['id']}) is missing from the site, but unmapped camps "
                                f"exist (maybe a rebuilt widget) — not cancelling until camps.json is fixed")
            elif step and step.casefold() != CANCELLED_STEP:
                actions.append({"op": "set_step", "id": h["id"], "name": h["name"],
                                "step": CANCELLED_STEP, "why": "no longer on the site"})
    return actions, warnings


def describe(a):
    op = a["op"]
    if op == "update_gathering":
        return f"gathering #{a['id']}: " + ", ".join(f"{k} {a['was'][k]!r} → {v!r}" for k, v in a["info_fields"].items())
    if op == "create_camp":
        return (f"CREATE camp {a['name']!r} under #{GATHERING_ID} on {CAMP_JOURNEY}/{LIVE_STEP}, "
                f"source={a['links']['source']}, {len(a['description'])} chars of description, "
                f"logo {'yes' if a['logo'] else 'none'}")
    if op == "update_camp":
        parts = []
        for k, v in a["set"].items():
            parts.append(f"name → {v!r}" if k == "name" else
                         f"description ({len(v)} chars)" if k == "description" else
                         f"links → {sorted(v)}")
        return f"update camp #{a['id']} {a['name']!r}: " + "; ".join(parts)
    if op == "set_logo":
        return f"set logo on #{a['id']} {a['name']!r} from {a['logo']}"
    if op == "set_step":
        return f"move #{a['id']} {a['name']!r} to {a['step']} ({a['why']})"
    return json.dumps(a)


# ---------------------------------------------------------------- execution

def load_metis_state(metis):
    gathering = metis.get(f"/holons/{GATHERING_ID}")
    children = metis.get("/holons", **{"class": "holon", "parent": GATHERING_ID, "limit": 100})["items"]
    camps = {h["id"]: metis.get(f"/holons/{h['id']}") for h in children if h["type"].startswith("camp")}
    rels = metis.get(f"/holons/{GATHERING_ID}/relationships", limit=100)
    rels = rels.get("items", rels) if isinstance(rels, dict) else rels
    steps, rel_ids = {}, {}
    for r in rels:
        if r.get("journey_name") == CAMP_JOURNEY_NAME and r["to_holon"]["id"] == GATHERING_ID:
            steps[r["from_holon"]["id"]] = (r.get("step_title") or "")
            rel_ids[r["from_holon"]["id"]] = r["relationship_id"]
    return gathering, camps, steps, rel_ids


def upload_logo(metis, holon_id, url):
    """Upload, then record the source URL — only after success, so a failed upload is retried."""
    content, ctype = fetch(url)
    metis.upload(f"/holons/{holon_id}/logo", "logo", url.rsplit("/", 1)[-1], content, ctype)
    links = metis.get(f"/holons/{holon_id}").get("links") or {}
    metis.post(f"/holons/{holon_id}/update", {"links": {**links, "logo_source": url}})


def apply(metis, actions, rel_ids):
    for a in actions:
        print("  ->", describe(a))
        op = a["op"]
        if op == "update_gathering":
            metis.post(f"/holons/{a['id']}/update", {"info_fields": a["info_fields"]})
        elif op == "create_camp":
            camp = metis.post("/camps", {"parent_id": GATHERING_ID, "name": a["name"],
                                         "description": a["description"], "journey": CAMP_JOURNEY,
                                         "step": LIVE_STEP, "metis_class": CAMP_CLASS,
                                         "links": a["links"]})["camp"]
            print(f"     created #{camp['id']}")
            if a["logo"]:
                time.sleep(1)
                upload_logo(metis, camp["id"], a["logo"])
        elif op == "update_camp":
            metis.post(f"/holons/{a['id']}/update", a["set"])
        elif op == "set_logo":
            upload_logo(metis, a["id"], a["logo"])
        elif op == "set_step":
            metis.post(f"/relationships/{rel_ids[a['id']]}/update",
                       {"step_slug": a["step"], "note": f"{NOTE}: {a['why']}"})
        time.sleep(1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write to METIS (default: dry run)")
    ap.add_argument("--html-dir", type=Path, help="read gather.html and camps.html from here instead of the site")
    ap.add_argument("--mapping", type=Path, default=HERE / "camps.json")
    args = ap.parse_args()

    if args.html_dir:
        gather_html = (args.html_dir / "gather.html").read_text(encoding="utf-8", errors="replace")
        camps_html = (args.html_dir / "camps.html").read_text(encoding="utf-8", errors="replace")
    else:
        gather_html = fetch(f"{SITE}/gather/")[0].decode("utf-8", "replace")
        time.sleep(FETCH_GAP_S)
        camps_html = fetch(f"{SITE}/camps/")[0].decode("utf-8", "replace")

    site_camps = parse_camps(camps_html)
    if not site_camps:
        sys.exit("no camp blocks found on /camps/ — page layout changed? refusing to plan")
    gathering_site = parse_gathering(gather_html)
    config = json.loads(args.mapping.read_text())
    mapping, exceptions = config["camps"], config.get("exceptions", {})

    metis = Metis(REPO_ROOT / ".env")
    gathering, camps, steps, rel_ids = load_metis_state(metis)
    actions, warnings = plan(site_camps, gathering_site, gathering, camps, steps, mapping, exceptions)

    print(f"site: {len(site_camps)} camp blocks ({sum(c['hidden'] for c in site_camps)} hidden); "
          f"METIS: {len(camps)} camps under #{GATHERING_ID}")
    for key, why in exceptions.items():
        print(f"  = excepted, not imported: {key} ({why})")
    for w in warnings:
        print("  !", w)
    if not actions:
        print("in sync — nothing to do")
        return
    if not args.apply:
        print(f"DRY RUN — {len(actions)} planned changes:")
        for a in actions:
            print("  -", describe(a))
        print("re-run with --apply to write them")
        return
    print(f"APPLYING {len(actions)} changes:")
    apply(metis, actions, rel_ids)
    print("done")


if __name__ == "__main__":
    main()
