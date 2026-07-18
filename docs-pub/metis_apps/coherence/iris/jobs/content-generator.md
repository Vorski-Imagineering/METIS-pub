# Content Generator

| | |
|---|---|
| **Label** | Content Generator |
| **Slug** | `content_generator` |
| **File** | `metis_apps/coherence/iris_content.py` |
| **Class** | `ContentGenerator` |
| **Depends on** | *(none declared, but needs `TranscriptSegment` rows to exist)* |

## Purpose

Calls Google Gemini **once** to generate all text-based publishing assets — title, subtitle,
YouTube description, LinkedIn posts (host + guest), Instagram quotes — from the conversation
transcript in a single structured call. Quality-gates on segment count and speaker
resolution before calling the model.

## Pipeline position

- **Upstream (`depends_on`):** none declared, but it needs `TranscriptSegment` rows, so it
  must run after a transcription step ([transcript-importer](transcript-importer.md) or
  [google-transcribe](google-transcribe.md)).
- **Feeds into:** `cover_image_generator` and `youtube_uploader` (both declare
  `content_generator`).
- **Alternative to:** none.

## Data flow

**Reads**
- `TranscriptSegment` rows (ordered by `offset_ms`).
- `JourneyStep.config` (`model`, `max_tokens`, `min_segments`, `min_distinct_speakers`,
  `prompts.*`).

**Writes**
- `infos["publishing"]["qa"]` (segment_count, distinct_speakers, warnings).
- `infos["publishing"]` (title, subtitle, language, youtube.description,
  linkedin.posts.host/guest, instagram.quotes, meta.model, meta.generated_at).

## Requirements

- **Agent.config:** `gemini.api_key`.
- **System:** none.
- **External credentials:** Gemini API key.

## Behavior details

- **Quality gates:** segment count and distinct-speaker resolution are checked before the
  model call; too few segments or unresolved speakers stop with a clear remediation note
  rather than generating weak content.
- **Retry policy:** transient errors (429/500/503/network) get 3× exponential backoff
  (1s/5s/25s) before `RetryLater`; permanent errors (400/403/404, validation, missing
  config) fail immediately.
- **Prompt tuning:** the `prompts.*` sections are configurable per journey step through the
  web UI — see the [prompt authoring guide](content-generator-prompts.md) for the available
  sections and context-injection tokens.
- **Done vs error:** "done" once `infos["publishing"]` is populated; permanent error on a
  quality-gate failure or a permanent Gemini error.

## Step slug convention

`"content-generator"` (matches `config["iris_job"] = "content_generator"`).

## Testing this step

No automated test today; the manual script
*test-scripts/test-content-generation.md* (internal engineering doc, not published here) is the
worked reference — 8 scenarios including the public-browse-endpoint regression check. Run it
on **staging only** with a staging Agent that has a valid `gemini.api_key`.

Verify: `infos["publishing"]` fields populated, `infos["publishing"]["qa"]` present,
`config["iris.content-generator"]` status `done`, a FLOW Note, `current_step` advanced. See
the *testing guide* (internal engineering doc, not published here).

## Related runbooks

- *manual-retrigger* (internal engineering doc, not published here) — the conversation detail page's
  **Regenerate** clears content-generator state and `infos["publishing"]` and re-runs.
