# Content Generator

Writes the publishing draft from the transcript: title, subtitle, YouTube description,
LinkedIn post, and pull quotes — all in a single pass.

## At a glance

| | |
|---|---|
| **Needs** | A transcript with speakers matched to real people |
| **Produces** | The Publishing draft on the conversation |
| **Waits when** | Rarely — it fails rather than waits if the transcript isn't good enough |
| **Re-running** | Safe. **Regenerate** replaces the draft, including manual edits |

## What it does

Sends the transcript to the AI model once, with your instructions, and gets every text asset
back in one structured response. One call rather than six keeps the outputs consistent with
each other — the LinkedIn post and the description are describing the same conversation in the
same voice, because they were written together.

The instructions are settings on the step, editable in the web UI: a shared base instruction
plus one per output. See [Writing prompts](../writing-prompts.md) for the sections available
and how to inject live conversation context (participant bios, connected organisations) into
them.

## Quality gates — why it sometimes refuses

Before spending a model call, the step checks the transcript is worth writing from:

- **enough content** — a transcript below the minimum segment count is rejected;
- **speakers resolved** — a transcript whose speakers aren't matched to real people is
  rejected.

Both thresholds are step settings. When a gate trips, the step **fails with a note saying what
to fix** rather than producing weak, misattributed copy from a thin transcript. Confident
nonsense is worse than an obvious blocker: nobody proofreads a draft that looks finished.

## How it behaves

- **Transient model errors are retried in place** — a few times, with increasing gaps, before
  the step gives up and waits for its next scheduled run.
- **Permanent errors fail immediately** — a bad API key, a rejected request, or a
  quality-gate failure won't fix itself by retrying.
- **Regenerating is a clean slate.** The Regenerate action on the Publishing panel clears the
  existing draft and re-runs. Manual edits are lost — copy anything you want to keep first.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| Error: transcript too short | The transcript has fewer segments than the step's minimum | Check the transcript imported correctly; if the conversation genuinely was that short, lower the minimum on the step |
| Error: speakers not resolved | Some speakers aren't matched to real people | Assign speakers in the assign-speakers UI, then regenerate |
| Error mentioning the API key | The model credentials are missing or rejected | An administrator fixes the agent configuration, then re-run |
| Draft generated but the voice is wrong | The prompts need tuning | Edit the step's prompt sections, then regenerate — see [Writing prompts](../writing-prompts.md) |
| LinkedIn post contains a placeholder like `[Link to Video]` | The prompt asks for a link, but no video exists yet at generation time | Fix the prompt — the real URL is appended automatically later. See [Writing prompts](../writing-prompts.md#the-linkedin-post-must-not-contain-the-video-link) |
| Regenerated and lost my edits | Regenerate replaces the whole draft | Expected. Edit after regenerating, not before |
| Draft is fine but the video shows the old title | The title is pushed to YouTube by a separate step | Re-run the metadata sync step — see [YouTube publishing](youtube-uploader.md) |

## Technical reference

| | |
|---|---|
| **Step type** | `content_generator` |
| **Runs after** | A transcription step — not a declared dependency, but it needs transcript rows to exist |
| **Feeds** | `cover_image_generator`, `youtube_video_upload` |
| **Reads** | `TranscriptSegment` rows; step settings `model`, `max_tokens`, `min_segments`, `min_distinct_speakers`, `prompts.*` |
| **Writes** | `fields.title`, `fields.subtitle`, `fields.language`, `fields.youtube_description`, `fields.linkedin_post`, `fields.instagram_quotes`, and `fields.qa` (segment count, distinct speakers, warnings) |
| **Provenance** | Every field is stamped with the job, model, prompt version and timestamp that produced it, so staleness is knowable per field rather than per run |
| **Needs on the agent** | `gemini.api_key` |
| **Model** | Google Gemini, one structured call per generation |
