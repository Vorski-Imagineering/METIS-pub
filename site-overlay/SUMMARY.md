<!--
  This file IS the site navigation (mkdocs-literate-nav reads it in place of a `nav:`
  block in mkdocs.yml). It covers THIS repo's own pages only — the site home,
  Automation, Tags and Project.

  The docs section's nav is METIS's docs/pub/SUMMARY.md, which arrives here as
  docs-pub/SUMMARY.md on every sync and is reached by the `- [METIS Docs](docs-pub/)`
  cross-link below: a nav link ending in "/" makes mkdocs-literate-nav read that
  directory's own SUMMARY.md. Edit it in METIS, never here — docs-pub/ is overwritten
  wholesale on every sync, and the menu has to agree with pages that live there
  (METIS-pub#434).

  Every page of this repo's own must appear here exactly once —
  .github/scripts/check_nav_coverage.py fails the build otherwise, following the
  cross-link so both navs are checked as one. Order is meaningful: it sets the sidebar
  order and the prev/next footer links. Order IRIS job pages by pipeline position, not
  alphabetically.
-->

- [Home](index.md)
- [METIS Docs](docs-pub/)
- [Automation](automation/index.md)
    - [LinkedIn automation](automation/linkedin-automation/index.md)
    - [METIS API](automation/metis/index.md)
    - [Google Sheets](automation/google-sheets/index.md)
- [Tags](tags.md)
- Project
    - [Contributing](CONTRIBUTING.md)
    - [Docs conventions](DOCS-CONVENTIONS.md)
