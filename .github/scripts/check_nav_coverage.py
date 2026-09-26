#!/usr/bin/env python3
"""
Fail the build if an assembled page is missing from the nav, or the nav points at
a page that does not exist.

Why this exists: docs-pub/ is copied wholesale into the site, so a new file added
upstream in METIS publishes at a URL immediately but appears in no sidebar and is
linked from nothing. That already happened twice (api/outreach-PLAYBOOK.md,
metis_apps/gathering/experience-images-howto.md were live and unreachable). A page
nobody can navigate to is worse than a build failure, so this makes it a failure.

The nav is now more than one file. A nav entry whose link ends in "/" is
mkdocs-literate-nav's cross-link to that directory's own SUMMARY.md, and the docs
section uses one: docs-pub/SUMMARY.md arrives from METIS, where it sits beside the
pages it lists. This walks those cross-links, so the two indexes are checked as one
nav — and every SUMMARY.md is exempt, because a nav file is not a page (METIS-pub#434).

Usage: check_nav_coverage.py [--out site_src] [--nav site_src/SUMMARY.md]
"""
import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

#: A nav file is not a page, wherever it sits: the root one and every nested one that
#: a cross-link pulls in.
NAV_FILENAME = "SUMMARY.md"

LINK_RE = re.compile(r"\]\(([^)\s]+\.md)(?:#[^)\s]*)?\)")

#: mkdocs-literate-nav reads <dir>/SUMMARY.md when a nav link ends in "/".
CROSSLINK_RE = re.compile(r"\]\(([^)\s]*/)\)")

#: A nav file's leading HTML comment explains the format, example links included. Those
#: are documentation, not nav entries, and counting them sent this script recursing into
#: a path it had assembled out of prose.
COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def collect_linked(nav_file: Path, missing: list, seen: set = None) -> set:
    """Every page the nav reaches, following cross-links into nested nav files.

    Nested nav files are picked up only through a link ending in "/" — never
    implicitly — so this mirrors what the plugin itself does.
    """
    seen = set() if seen is None else seen
    nav_file = nav_file.resolve()
    if nav_file in seen:
        return set()
    seen.add(nav_file)

    if not nav_file.is_file():
        missing.append(nav_file)
        return set()

    text = COMMENT_RE.sub("", nav_file.read_text())
    linked = set()
    for target in LINK_RE.findall(text):
        if target.startswith(("http://", "https://")):
            continue
        linked.add((nav_file.parent / target).resolve())
    for target in CROSSLINK_RE.findall(text):
        if target.startswith(("http://", "https://")):
            continue
        nested = (nav_file.parent / target / NAV_FILENAME).resolve()
        linked |= collect_linked(nested, missing, seen)
    return linked


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="site_src")
    parser.add_argument("--nav", default=None)
    args = parser.parse_args()

    out = (REPO / args.out).resolve()
    nav_file = Path(args.nav).resolve() if args.nav else out / "SUMMARY.md"
    if not nav_file.is_file():
        sys.exit(f"check_nav_coverage: no nav file at {nav_file}")

    missing_navs: list = []
    linked = collect_linked(nav_file, missing_navs)
    for path in missing_navs:
        print(
            f"nav cross-link points at a missing nav file: {path}",
            file=sys.stderr,
        )

    on_disk = {p.resolve() for p in out.rglob("*.md")}
    exempt = {p.resolve() for p in out.rglob(NAV_FILENAME)}

    orphans = sorted(on_disk - linked - exempt)
    dangling = sorted(linked - on_disk)

    for path in dangling:
        print(f"nav points at a missing page: {path.relative_to(out)}", file=sys.stderr)
    for path in orphans:
        rel = path.relative_to(out)
        # Point at the file that actually has to change. A docs-pub/ page's nav entry
        # lives in METIS; editing it here would be overwritten by the next sync.
        where = (
            "add it to docs/pub/SUMMARY.md in METIS"
            if rel.as_posix().startswith("docs-pub/")
            else "add it to site-overlay/SUMMARY.md"
        )
        print(f"page is in no nav entry: {rel} — {where}", file=sys.stderr)

    if orphans or dangling or missing_navs:
        print(
            f"\n{len(orphans)} orphan(s), {len(dangling)} dangling entry(ies), "
            f"{len(missing_navs)} missing nav file(s). See DOCS-CONVENTIONS.md.",
            file=sys.stderr,
        )
        return 1

    print(f"nav coverage OK: {len(on_disk) - len(exempt)} page(s), all reachable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
