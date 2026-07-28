# Docs conventions

How the published documentation site is put together, and how to write a page that fits it.

The site is built from two sources that behave very differently:

| Tree | Origin | Edit it here? |
|---|---|---|
| `docs-pub/` | Synced automatically from the METIS source repo | **No** — changes are overwritten on the next sync. Edit upstream in METIS. |
| `automation/`, `README.md`, `CONTRIBUTING.md` | Written and maintained in this repo | Yes |
| `site-overlay/` | Written and maintained in this repo | Yes — this is how you change the *site's* view of `docs-pub/` durably |

## How the build works

`.github/workflows/docs.yml` runs three steps:

1. **`.github/scripts/assemble_docs.py`** builds `site_src/` (the mkdocs `docs_dir`):
   copies the published trees in, renames every `README.md` to `index.md` and rewrites
   links to match, lays `site-overlay/` on top, normalizes Markdown for Python-Markdown,
   and injects `tags:` front matter from `site-overlay/tags.yml`.
2. **`.github/scripts/check_nav_coverage.py`** fails the build if any assembled page is
   missing from the nav, or the nav points at a page that doesn't exist.
3. **`mkdocs build --strict`**.

Nothing needs a workflow edit when a page is added — but step 2 means a new page **does**
need a `site-overlay/SUMMARY.md` entry.

### The nav lives in `site-overlay/SUMMARY.md`

There is no `nav:` block in `mkdocs.yml`. `mkdocs-literate-nav` reads `SUMMARY.md` — a
nested Markdown list — instead. Two rules:

- **The list must be tight** (no blank lines between items). A blank line makes
  Python-Markdown wrap each item in `<p>`, and literate-nav rejects that.
- **Order is meaningful.** It sets both the sidebar order and the prev/next footer links.
  Order by the reader's path through the material, not alphabetically — the IRIS job
  pages are ordered by pipeline position, which is the order an operator meets them.

A section whose title line carries a link uses that page as the section's landing page
(Material's `navigation.indexes`), so "Job reference" opens the IRIS job index rather than
merely expanding.

### Adding a page

- **Upstream in METIS, under `docs-pub/`:** add the file there, then add one line to
  `site-overlay/SUMMARY.md` here, and a row to the relevant table in
  `site-overlay/docs-pub/index.md`. Until you do, CI fails — deliberately: an unreachable
  published page is worse than a red build. Two pages
  (`api/outreach-PLAYBOOK.md`, `metis_apps/gathering/experience-images-howto.md`) sat live
  and unlinked before this check existed.
- **In this repo, under `automation/`:** any `README.md` under `automation/` is picked up
  automatically; still add the `SUMMARY.md` line.

### Tags

`site-overlay/tags.yml` maps page paths to tags. Tags live there rather than in the pages
because front matter added to `docs-pub/` would be lost on the next sync. The vocabulary
is deliberately small (`linkedin`, `publishing`, `permissions`, `api`, `configuration`) and
enforced by `tags_allowed` in `mkdocs.yml` — a typo fails the build instead of quietly
creating a one-page tag. A tag that lands on half the site sorts nothing; if a new tag
wouldn't group at least three pages that are *far apart in the nav*, it isn't earning its
place.

## Writing a page

The IRIS job pages are the model to copy. Every one of them opens with the same key-value
table and then follows the same heading spine — so a reader who has read one can navigate
all nineteen without re-orienting. Aim for that property per document type.

### Every page

1. **An H1 that names the thing**, not the section it sits in.
2. **A lede of one or two sentences** that says what the page covers *and who it is for*.
   A page must stand on its own: most readers arrive from search, not from the index, so
   "who should read this" belongs on the page rather than only in the index table.
3. **No hand-numbered headings.** Don't write `## 2.2.4 Job Steps`. The sidebar numbers
   itself, and hand numbering has to be rewritten every time a page is inserted.
4. **Links to sibling pages by relative `.md` path** (`youtube-uploader.md`,
   `../using-iris.md`), so they work both on GitHub and on the site.

### Reference pages (one page per unit of a repeating thing)

Follow the IRIS job pattern exactly:

- A key-value table at the top: what identifies this thing (label, slug, source file,
  class, dependencies).
- Then the fixed spine: **Purpose → Pipeline position → Data flow → Requirements →
  Behavior details → Testing this step → Related runbooks.**
- The set of them gets an index page that is a **table**, not prose: one row per page,
  with the columns a reader scans by. `docs-pub/metis_apps/coherence/iris/jobs/README.md`
  uses *# / Job / Slug / Depends on / Purpose*, and fits nineteen pages on one screen.
- The index says what has **no page of its own** and what is **legacy**. Navigation
  honesty: a reader who can't find a page should learn why from the index.
- Where the structure isn't linear, draw it — the ASCII branch diagram in the IRIS job
  index conveys the two-branch shape faster than any amount of prose.

### Guides and how-tos

- Lead with the outcome, then the click-path in order.
- Prerequisites go in an `!!! note` admonition before step 1, not scattered inline.
- If the guide is for a specific audience (participants, administrators), say so in the
  lede — see `iris/participant-approval.md`.

### Placeholder pages

A page whose guide isn't written yet must say so in its own body, in an admonition:

```markdown
!!! warning "Placeholder"

    The usage guide for this app has not been written yet. This page exists so the
    section has a home; it will be filled in.
```

Don't leave the fact that a page is a stub visible only from the index — readers arriving
from search deserve to know within one screen. `metis_apps/audax/quests-and-missions.md`,
`metis_apps/outreach/linkedin-outreach.md` and `web/invite/signup.md` are the current
stubs; they still need this treatment upstream in METIS.

## Building locally

```bash
python3 -m venv .venv
.venv/bin/pip install mkdocs-material mkdocs-literate-nav
python3 .github/scripts/assemble_docs.py
python3 .github/scripts/check_nav_coverage.py
.venv/bin/mkdocs serve
```

`site_src/` and `site/` are both generated and both git-ignored — never edit them.
