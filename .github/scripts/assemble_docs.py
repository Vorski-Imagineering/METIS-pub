#!/usr/bin/env python3
"""
Assemble site_src/ — the mkdocs docs_dir — from the repo.

This replaces the inline `cp` block that used to live in .github/workflows/docs.yml.
It does four things the shell version could not:

1. **Copies** the published trees into site_src/ (repo README, CONTRIBUTING, the
   automation module READMEs, and the whole synced docs-pub/ tree).
2. **Renames every README.md to index.md** and rewrites intra-doc links to match, so
   the page becomes its directory's landing page: /docs-pub/ instead of
   /docs-pub/README/. This is also what Material's `navigation.indexes` needs to turn
   a section header into a clickable page.
3. **Applies the overlay** in site-overlay/ on top of the result. docs-pub/ is synced
   from the METIS source repo and is overwritten wholesale on every sync, so anything
   we want to change about it durably has to live outside it — the overlay is that
   place. It also carries SUMMARY.md, which drives the nav (mkdocs-literate-nav).
4. **Normalizes** the synced Markdown for Python-Markdown (see normalize_markdown_lists),
   then **injects `tags:` front matter** from site-overlay/tags.yml so cross-cutting
   topics can be browsed from the tags index without editing synced files. Order
   matters: normalizing after injection would insert a blank line into the YAML.

Usage: assemble_docs.py [--out site_src]
Run from the repo root.
"""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from normalize_markdown_lists import normalize  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
OVERLAY = REPO / "site-overlay"

# (source, destination-relative-to-out). Directories are copied whole.
COPIES = [
    (REPO / "README.md", "index.md"),
    (REPO / "CONTRIBUTING.md", "CONTRIBUTING.md"),
    (REPO / "DOCS-CONVENTIONS.md", "DOCS-CONVENTIONS.md"),
    (REPO / "docs-pub", "docs-pub"),
]

# Every README.md under automation/ publishes; new modules need no workflow edit.
AUTOMATION = REPO / "automation"

# Matches a Markdown link target ending in README.md, with optional #anchor.
README_LINK_RE = re.compile(r"(?<=\]\()([^)\s]*?)README\.md(#[^)\s]*)?(?=[)\s])")


def copy_sources(out: Path) -> None:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    for src, dest in COPIES:
        if not src.exists():
            sys.exit(f"assemble_docs: missing source {src.relative_to(REPO)}")
        target = out / dest
        target.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, target)
        else:
            shutil.copy2(src, target)

    for readme in sorted(AUTOMATION.rglob("README.md")):
        target = out / readme.relative_to(REPO)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(readme, target)


def readmes_to_indexes(out: Path, manifest: Path) -> int:
    """Rename README.md -> index.md everywhere, then repoint links to match.

    Records what was renamed so write_legacy_redirects.py can keep the old
    …/README/ URLs alive — the site is already published under them.
    """
    renamed = []
    for readme in sorted(out.rglob("README.md")):
        index = readme.with_name("index.md")
        if index.exists():
            sys.exit(f"assemble_docs: both README.md and index.md in {readme.parent}")
        readme.rename(index)
        renamed.append(readme.relative_to(out).as_posix())
    manifest.write_text(json.dumps(renamed, indent=2) + "\n")

    for page in sorted(out.rglob("*.md")):
        original = page.read_text()
        # "…/README.md" -> "…/index.md"; a bare "README.md" -> "index.md".
        fixed = README_LINK_RE.sub(lambda m: f"{m.group(1)}index.md{m.group(2) or ''}", original)
        if fixed != original:
            page.write_text(fixed)
    return len(renamed)


def apply_overlay(out: Path) -> int:
    """Copy site-overlay/ over the assembled tree. Overlay files win."""
    if not OVERLAY.is_dir():
        return 0
    applied = 0
    for src in sorted(OVERLAY.rglob("*")):
        if src.is_dir() or src.name == "tags.yml":
            continue
        target = out / src.relative_to(OVERLAY)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
        applied += 1
    return applied


def normalize_markdown(out: Path) -> int:
    """Python-Markdown needs a blank line before a list; GitHub's renderer does not."""
    changed = 0
    for page in sorted(out.rglob("*.md")):
        original = page.read_text()
        fixed = normalize(original)
        if fixed != original:
            page.write_text(fixed)
            changed += 1
    return changed


def inject_tags(out: Path) -> int:
    """Prepend `tags:` front matter to pages listed in site-overlay/tags.yml."""
    mapping_file = OVERLAY / "tags.yml"
    if not mapping_file.is_file():
        return 0
    import yaml  # provided by mkdocs

    mapping = yaml.safe_load(mapping_file.read_text()) or {}
    tagged = 0
    for rel, tags in mapping.items():
        page = out / rel
        if not page.is_file():
            sys.exit(f"assemble_docs: tags.yml points at missing page {rel}")
        text = page.read_text()
        if text.startswith("---\n"):
            sys.exit(f"assemble_docs: {rel} already has front matter; merge by hand")
        block = "---\ntags:\n" + "".join(f"  - {t}\n" for t in tags) + "---\n\n"
        page.write_text(block + text)
        tagged += 1
    return tagged


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="site_src")
    parser.add_argument("--manifest", default=".readme-renames.json")
    args = parser.parse_args()
    out = (REPO / args.out).resolve()

    copy_sources(out)
    renamed = readmes_to_indexes(out, REPO / args.manifest)
    applied = apply_overlay(out)
    normalized = normalize_markdown(out)
    tagged = inject_tags(out)

    pages = sum(1 for _ in out.rglob("*.md"))
    print(
        f"assembled {pages} page(s) into {out.relative_to(REPO)}: "
        f"{renamed} README->index, {applied} overlay file(s), "
        f"{normalized} normalized, {tagged} tagged"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
