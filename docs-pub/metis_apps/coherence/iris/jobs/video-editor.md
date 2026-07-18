# Video Editor

| | |
|---|---|
| **Label** | Video Editor |
| **Slug** | `video_editor` |
| **File** | `metis_apps/coherence/iris_video.py` |
| **Class** | `VideoEditor` |
| **Depends on** | `realtimekit_downloader` |

## Purpose

Produces the **cleaned canonical long-form** (internally "v1a") from the raw recording: a
fixed head trim (the RealtimeKit connection artifact at the very start) plus leading and
trailing dead-air removal. Internal pacing is deliberately **preserved** — aggressive
filler removal is reserved for clips ([clip-generator](clip-generator.md)), not the
long-form.

It exists as its own step, rather than being folded into the downloader or uploader,
because it also emits an **edit map** (an EDL) recording the time-shift between the raw and
cleaned timelines. That map is the single source of truth so moments, captions, and deep
links still resolve on the cleaned timeline. The raw recording is **never edited in place**
— the cut is a new derived file and the raw is retained (`MemoryModel.md`, "evidence is
immutable").

> **⚠️ TO BE REVIEWED:** this note claims `youtube_uploader` still publishes the raw
> `recording`, not `edited_recording` — but the code has since changed to **prefer**
> `edited_recording` (see [youtube-uploader.md](youtube-uploader.md) → *Recording selection*,
> `_select_recording_rel`, `iris_youtube.py:287`). This paragraph is stale and needs
> reconciling with that behavior.
>
> **Deliberate non-change (stale — see above):** `youtube_uploader` still publishes the raw
> `recording`, not `edited_recording`. Switching it would change an existing job's published
> output, which is a hard-stop change (see CLAUDE.md) and is intentionally *not* done here.
> Soft captions (`longform_vtt`) need word timestamps (WhisperX) and are a separate follow-up.

## Pipeline position

- **Upstream (`depends_on`):** `realtimekit_downloader` — needs the raw recording on disk.
- **Feeds into:** `clip_generator` (cuts clips from the cleaned recording, mapped through
  the edit map). This is the **video/clips branch**, parallel to the transcript branch.
- **Alternative to:** none.

## Data flow

**Reads**
- `config["iris.downloads"]["recording"]` — the raw recording (MEDIA_ROOT-relative).
- `JourneyStep.config` (`VideoEditorConfig`): `head_trim_ms`, `silence_noise_db`,
  `min_silence_ms`, `trim_leading_silence`, `trim_trailing_silence`, `edge_tolerance_ms`.

**Writes** (owned output paths)
- `config["iris.downloads"]["edited_recording"]` — MEDIA_ROOT-relative path to the cleaned
  cut, kept beside the raw file with an `edited_` prefix (so cloud migration and cleanup
  treat it like any other downloaded artifact).
- `config["iris.downloads"]["edit_map"]` — the EDL dict (`EditMap.to_dict()`).

## Requirements

- **Agent.config:** none.
- **System:** `ffmpeg`/`ffprobe` on PATH (duration probe, `silencedetect`, render/remux via
  `video_ops`).
- **External credentials:** none.

## Behavior details

- **Idempotency:** skips if `edited_recording` is set **and** its file still exists on disk.
- **`RetryLater` conditions:** the recording path isn't set yet, or is set but the file
  isn't present yet (waiting on the downloader).
- **Config validation:** an invalid `JourneyStep.config` raises `ValueError` (permanent
  error), not `RetryLater`.
- **Empty-cut guard:** if the trim plan would remove the *entire* recording (whole-file
  silence, or `head_trim_ms >= duration`), it logs a warning and falls back to an
  **identity edit map** — the raw recording is published unchanged rather than producing an
  empty video.
- **No-op cut:** if nothing is removed, it **stream-copies** (remux) rather than
  re-encoding.
- **Path safety:** both the read (raw) and write (edited) paths are checked to resolve
  inside `MEDIA_ROOT` — a malformed `..`/absolute upstream path is rejected, because this
  job both writes the derived cut and deletes it on step reset.
- **Done vs error:** "done" once the cleaned cut and edit map are written; a permanent error
  is a bad config or a path escaping `MEDIA_ROOT`.

## Step slug convention

`"video-editor"` (matches `config["iris_job"] = "video_editor"`).

## Testing this step

Unusually well-covered by automated tests — the manual pass should focus on
visually / `ffprobe`-verifying an actual rendered cut, not re-checking logic the unit tests
already cover.

- `test_iris_video.py` — the `process()` behavior: writes edited recording + edit map,
  stream-copies when there's no silence, whole-file-silence falls back to remux (not an
  empty cut), path-traversal rejection, missing-recording `RetryLater`, idempotency,
  invalid-config `ValueError`.
- `test_edit_map.py` — the `EditMap` model (identity, removed regions, offset mapping in
  both directions, serialization round-trip, validation).
- `test_video_trim.py` — silence parsing and `plan_removed_regions` (edge trims, head trim,
  internal-silence preservation, trim-plan → edit-map integration).

Run: `python3 manage.py test --keepdb --parallel auto metis_apps.coherence`. See the
*testing guide* (internal engineering doc, not published here) for the shared "did it actually work"
verification pattern and how to force each error category.

## Related runbooks

- *manual-retrigger* (internal engineering doc, not published here) — re-run after a failed edit.
- *cleanup-image-files* (internal engineering doc, not published here) — for orphaned derived files
  when re-running produces a new cut.
