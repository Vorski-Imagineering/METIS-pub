#!/usr/bin/env python3
"""
Keep the old …/README/ URLs alive after the README.md -> index.md rename.

The site has been published for a while with pages at /docs-pub/README/,
/automation/metis/README/ and so on. Those pages are now /docs-pub/ and
/automation/metis/, so anything already linking to the old URL would 404. This writes a
meta-refresh stub at each old location pointing at the new one.

The mkdocs-redirects plugin cannot do this job: it treats a README.md source as a
directory index, so `docs-pub/README.md: docs-pub/index.md` collapses to
"/docs-pub/ -> /docs-pub/" and it overwrites the real page with a self-redirect.

Reads the rename manifest that assemble_docs.py writes.

Usage: write_legacy_redirects.py [--site site] [--manifest .readme-renames.json]
"""
import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

TEMPLATE = """<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<title>Redirecting</title>
<link rel="canonical" href="{target}">
<meta http-equiv="refresh" content="0; url={target}">
</head><body>
Redirecting to <a href="{target}">{target}</a>.
</body></html>
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default="site")
    parser.add_argument("--manifest", default=".readme-renames.json")
    args = parser.parse_args()

    site = (REPO / args.site).resolve()
    manifest = REPO / args.manifest
    if not manifest.is_file():
        print(f"write_legacy_redirects: no manifest at {manifest}; nothing to do")
        return 0

    written = 0
    for rel in json.loads(manifest.read_text()):
        # "docs-pub/README.md" -> old URL /docs-pub/README/, new page at /docs-pub/
        directory = Path(rel).parent
        old = site / directory / "README" / "index.html"
        if old.exists():
            print(f"write_legacy_redirects: refusing to overwrite real page {old}")
            return 1
        old.parent.mkdir(parents=True, exist_ok=True)
        old.write_text(TEMPLATE.format(target="../"))
        written += 1

    print(f"wrote {written} legacy redirect stub(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
