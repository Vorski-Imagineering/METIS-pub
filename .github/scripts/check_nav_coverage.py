#!/usr/bin/env python3
"""
Fail the build if an assembled page is missing from the nav, or the nav points at
a page that does not exist.

Why this exists: docs-pub/ is copied wholesale into the site, so a new file added
upstream in METIS publishes at a URL immediately but appears in no sidebar and is
linked from nothing. That already happened twice (api/outreach-PLAYBOOK.md,
metis_apps/gathering/experience-images-howto.md were live and unreachable). A page
nobody can navigate to is worse than a build failure, so this makes it a failure.

Usage: check_nav_coverage.py [--out site_src] [--nav site_src/SUMMARY.md]
"""
import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# Pages that are legitimately not nav entries.
EXEMPT = {"SUMMARY.md"}

LINK_RE = re.compile(r"\]\(([^)\s]+\.md)(?:#[^)\s]*)?\)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="site_src")
    parser.add_argument("--nav", default=None)
    args = parser.parse_args()

    out = (REPO / args.out).resolve()
    nav_file = Path(args.nav).resolve() if args.nav else out / "SUMMARY.md"
    if not nav_file.is_file():
        sys.exit(f"check_nav_coverage: no nav file at {nav_file}")

    linked = set()
    for target in LINK_RE.findall(nav_file.read_text()):
        if target.startswith(("http://", "https://")):
            continue
        linked.add((nav_file.parent / target).resolve())

    on_disk = {p.resolve() for p in out.rglob("*.md")}
    exempt = {(out / name).resolve() for name in EXEMPT}

    orphans = sorted(on_disk - linked - exempt)
    dangling = sorted(linked - on_disk)

    for path in dangling:
        print(f"nav points at a missing page: {path.relative_to(out)}", file=sys.stderr)
    for path in orphans:
        print(f"page is in no nav entry: {path.relative_to(out)}", file=sys.stderr)

    if orphans or dangling:
        print(
            f"\n{len(orphans)} orphan(s), {len(dangling)} dangling entry(ies). "
            f"Add them to site-overlay/SUMMARY.md (see DOCS-CONVENTIONS.md).",
            file=sys.stderr,
        )
        return 1

    print(f"nav coverage OK: {len(on_disk) - len(exempt)} page(s), all reachable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
