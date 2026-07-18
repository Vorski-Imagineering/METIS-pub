#!/usr/bin/env python3
"""
Insert a blank line before any Markdown list that starts immediately after a
paragraph line, with no blank line in between.

GitHub's renderer (GFM/CommonMark) allows a list to interrupt a paragraph
without a blank line first; Python-Markdown (what mkdocs/mkdocs-material
builds with) does not — it silently folds the list into the preceding
paragraph as plain text. Content synced from the METIS repo renders fine on
GitHub but breaks on the docs site unless normalized first.

Usage: normalize_markdown_lists.py <dir> [<dir> ...]
Rewrites every *.md file under the given directories in place.
"""
import re
import sys
from pathlib import Path

LIST_RE = re.compile(r'^(\s*)([-*+]\s+|\d+[.)]\s+)')
FENCE_RE = re.compile(r'^\s*(```|~~~)')


def normalize(text):
    lines = text.split('\n')
    out = []
    in_fence = False
    in_list = False
    for line in lines:
        if FENCE_RE.match(line):
            in_fence = not in_fence
            in_list = False
            out.append(line)
            continue
        if not in_fence and LIST_RE.match(line):
            if not in_list and out and out[-1].strip() != '':
                out.append('')
            in_list = True
        elif line.strip() == '':
            in_list = False
        elif not line.startswith((' ', '\t')):
            in_list = False
        out.append(line)
    return '\n'.join(out)


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    changed = 0
    for root in argv:
        for path in Path(root).rglob('*.md'):
            original = path.read_text()
            fixed = normalize(original)
            if fixed != original:
                path.write_text(fixed)
                changed += 1
                print(f"normalized: {path}")
    print(f"{changed} file(s) changed")
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
