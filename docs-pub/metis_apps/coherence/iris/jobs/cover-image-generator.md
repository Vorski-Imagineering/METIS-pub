# Cover Image Generator

| | |
|---|---|
| **Label** | Cover Image Generator |
| **Slug** | `cover_image_generator` |
| **File** | `metis_apps/coherence/iris_cover_images.py` |
| **Class** | `CoverImageGenerator` |
| **Depends on** | `content_generator` |

## Purpose

Renders branded thumbnail / LinkedIn-header / quote-card images via Playwright + HTML/CSS
templates, using `infos["publishing"]["title"]` and participant photos.

## Pipeline position

- **Upstream (`depends_on`):** `content_generator` (needs the generated title/quotes).
- **Feeds into:** nothing declares it downstream; its images are consumed by publishing jobs
  (e.g. YouTube thumbnail sync) via `infos["publishing"]`.
- **Alternative to:** none.

## Data flow

**Reads**
- `infos["publishing"]["title"]` (prerequisite gate), participant `Person.photo`.
- `JourneyStep.config` (`template_pack`, `generate_thumbnail`, `generate_linkedin_header`,
  `generate_quote_cards`, `quote_card_limit`).

**Writes**
- `infos["publishing"]["thumbnail"]`, `infos["publishing"]["linkedin"]["header"]`,
  `infos["publishing"]["instagram"]["quote_cards"]`,
  `infos["publishing"]["meta"]["cover_images"]`.

## Requirements

- **Agent.config:** none.
- **System:** Playwright + Chromium installed
  (`pip install playwright && playwright install chromium --with-deps`). The job launches
  headless Chromium on the server.
- **External credentials:** none.

## Behavior details

- **Prerequisite gate:** requires `infos["publishing"]["title"]` (from
  `content_generator`); `RetryLater` until present.
- **Partial-success:** individual card render failures are logged and skipped; the job only
  fails outright if **no** cards render.
- **Templates:** renders `thumbnail.html`, `linkedin_header.html`, and
  `quote_square.html` from the subdirectory selected by `template_pack` under
  `iris/cards/`; the selected pack is also recorded for traceability. Each pack
  must provide all three templates, so changing `template_pack` on a journey
  step changes the design used by that journey's generated cover images.
- **Randomised imagery:** a pack may ship its own image library under
  `<pack>/assets/` and draw from it at render time, so its cards differ between
  runs and between sibling cards in one run. Draws come from a shuffled deck, so
  a render batch exhausts the library before repeating an image. The `audax-os`
  pack works this way; `default` and `the-coherence-company` do not. Because the
  choice is made during template rendering, it is not recorded in
  `records.cover_images` — the worker log notes each draw instead.
- **Done vs error:** "done" once at least one image is written; permanent error only if
  every card fails or Playwright/Chromium is unavailable.

## Step slug convention

`"cover-image-generator"` (matches `config["iris_job"] = "cover_image_generator"`).

## Testing this step

Automated coverage renders every discovered pack's thumbnail, LinkedIn header, and
quote-card templates, and exercises the per-pack asset deck; it cannot judge
whether a card *looks* right. For that, use the card preview route in a browser
(`?pack=<name>&conversation=<id>`).

Two further manual references:

- *test-scripts/test-cover-images.md* (internal engineering doc, not published here) — shell-driven
  functional scenarios (errors, retries, partial success).
- *cover-images-setup-and-ui-testing.md* (internal engineering doc, not published here) —
  Playwright/Chromium install, deploy automation, and browser-based UI testing.

Run infra checks (Chromium launches, templates render) before functional tests. See the
*testing guide* (internal engineering doc, not published here).

## Related runbooks

- *cleanup-image-files* (internal engineering doc, not published here) — remove orphaned image files
  after a re-run.
- *manual-retrigger* (internal engineering doc, not published here)
