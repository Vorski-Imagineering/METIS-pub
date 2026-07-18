# Clip Generator

| | |
|---|---|
| **Label** | Clip Generator |
| **Slug** | `clip_generator` |
| **File** | `metis_apps/coherence/iris_clips.py` |
| **Class** | `ClipGenerator` |
| **Depends on** | `video_editor` |

## Purpose

Plans short vertical clips (internally "v1b") from the most quotable, consent-cleared
moments of the conversation, mapping each moment's raw-recording window onto the **cleaned
timeline** via the edit map.

It **plans clips, not pixels**: it does *not* render them. Rendering (active-speaker
face-track to 9:16, aggressive trim, burned captions, per-platform encode) is an explicit
build-vs-buy decision (`specs/VideoEditingAndClips.md`, self-host toolchain vs a managed
API). Whichever wins is handed these records' explicit edited-timeline in/out points — the
**selection is the moat** and stays in-house either way. Burned captions additionally need
word timestamps (WhisperX), also a follow-up.

## Pipeline position

- **Upstream (`depends_on`):** `video_editor` — clips are cut from the cleaned recording and
  mapped through its edit map.
- **Feeds into:** nothing yet. Clip *rendering* isn't built, so this is currently the end of
  the **video/clips branch** — a deliberate dead end.
- **Alternative to:** none.

## Data flow

**Reads**
- `config["iris.downloads"]["edit_map"]` and `["edited_recording"]` — both required
  (`RetryLater` until `video_editor` has produced them).
- Moments source, in order of preference:
  1. `infos["publishing"]["moments"]` — the Synthesis `moments[]` signature, when present.
  2. Otherwise an **interim Gemini selection** shaped to the same schema (the in-house moat).
     This path reads `TranscriptSegment` rows and `config["enter-coherence"]` (speaker names).
- `JourneyStep.config` (`ClipGeneratorConfig`): `model`, `max_clips`, `min_clip_ms`,
  `max_clip_ms`, `target_clip_ms`, `quotability_threshold`.

**Writes** (owned output — reset via `reset_owned_output`, not `owned_output_paths`)
- `infos["publishing"]["clips"]` — one record per clip: `moment_id`, `speaker`, `text`,
  `quotability`, `source` (raw + edited start/end ms), a `platforms` map (one pending
  variant per target: `youtube_shorts`, `linkedin`, `tiktok`, `instagram_reels`),
  `captions: null` (deferred), `approval_state: "pending"`, `render_status: "pending"`.

## Requirements

- **Agent.config:** `gemini.api_key` — **only** for the interim moment selection. Once
  Synthesis `moments[]` exists on the conversation, no Gemini call is made.
- **System:** none (no ffmpeg/Playwright — it plans, doesn't render).
- **External credentials:** Gemini API key only, and only on the interim path.

## Behavior details

- **Idempotency:** skips if `"clips"` is **present** in `infos["publishing"]` — a
  *presence* check, not truthiness, so a legitimately empty selection (zero clips planned)
  still counts as done and isn't re-run (and doesn't re-call Gemini).
- **`RetryLater` conditions:** no edit map yet, no cleaned recording yet, or (interim path)
  no `TranscriptSegment` rows yet.
- **Reuse note:** the interim Gemini path deliberately reuses `content_generator`'s Gemini
  call/schema/retry helpers (`_call_gemini_with_retry`, `_gemini_schema`,
  `_raise_if_gemini_blocked`, `_resolve_speaker_name`) rather than duplicating a second
  retry/backoff and schema path — a reuse-before-new-code example.
- **Selection:** `clip_selection.select_clips` filters non-`public` consent, drops moments
  below `quotability_threshold`, ranks by quotability, caps at `max_clips`, builds each
  clip window toward `target_clip_ms` (bounded by min/max), and maps the window onto the
  edited timeline. `ClipGeneratorConfig` validates `min_clip_ms <= target_clip_ms <=
  max_clip_ms`.
- **Config defaults:** `model="gemini-2.5-pro"`, `max_clips=6` (1–8), `min_clip_ms=15000`,
  `target_clip_ms=30000`, `max_clip_ms=90000`, `quotability_threshold=0.0`.
- **Prompt safety:** the interim prompt wraps the transcript in explicit
  untrusted-content markers and instructs the model to ignore any embedded instructions.
- **Done vs error:** "done" once `clips` is written (possibly empty); a permanent error is a
  bad config, a missing Gemini key on the interim path, or a Gemini response that fails
  schema validation.

## Step slug convention

`"clip-generator"` (matches `config["iris_job"] = "clip_generator"`).

## Testing this step

- `test_iris_clips.py` — `process()`: plans clips ranked/consent-filtered/mapped,
  `RetryLater` without edit map or without cleaned recording, idempotency (including the
  empty-selection case), `reset_owned_output` clears clips, invalid-config `ValueError`.
- `test_clip_selection.py` — the selection helper: window expansion to target length,
  start/end clamping, max-length cap, consent exclusion, quotability ranking + cap,
  threshold filtering, edited-timeline mapping.

Because the interim path calls Gemini, exercise it on staging with a real transcript and a
valid `gemini.api_key`; or provide `infos["publishing"]["moments"]` to test the
selection/mapping without any model call. Run:
`python3 manage.py test --keepdb --parallel auto metis_apps.coherence`. See the
*testing guide* (internal engineering doc, not published here) for the shared verification pattern.

## Related runbooks

- *manual-retrigger* (internal engineering doc, not published here) — re-run after clearing the step
  marker (the presence idempotency means you must clear `infos["publishing"]["clips"]` to
  re-plan; the step reset action does this via `reset_owned_output`).
