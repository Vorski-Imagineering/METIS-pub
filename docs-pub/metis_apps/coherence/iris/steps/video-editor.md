# Video Editor

Produces a clean version of the recording: trims the connection glitch at the very start, and
the dead air at the beginning and end. Optional, and on its own branch of the pipeline.

## At a glance

| | |
|---|---|
| **Needs** | The downloaded recording |
| **Produces** | A cleaned copy of the recording, plus a map of what was cut |
| **Waits when** | The recording hasn't been downloaded yet |
| **Re-running** | Safe — skips if the cleaned cut already exists |

## What it does

Makes a **new** file — the raw recording is never edited in place — with three trims: a fixed
head trim for the connection artefact every meeting recording starts with, plus leading and
trailing silence.

**Pacing inside the conversation is deliberately left alone.** Cutting pauses and filler out
of a long-form conversation makes it feel wrong; that kind of aggressive editing belongs to
short clips, which are a separate concern and not something IRIS does.

Alongside the cut it writes an **edit map**: a record of how time in the cleaned version
relates to time in the original. That's the reason this is its own step rather than something
folded into the downloader or the uploader — timestamps, chapter marks and deep links into the
conversation are all recorded against the original recording, and the edit map is what keeps
them pointing at the right moment after the trim.

[YouTube Video Upload](youtube-uploader.md) prefers the cleaned cut whenever it exists, and
falls back to the raw recording otherwise — so adding or removing this step from a journey
needs no other changes. It also shifts any chapter timestamps in the description onto the
cleaned timeline so they don't drift.

## How it behaves

- **It never publishes an empty video.** If the trim plan would remove the entire recording —
  whole-file silence, or a head trim longer than the recording — it logs a warning and falls
  back to publishing the recording unchanged.
- **Nothing to cut means no re-encode.** If the plan removes nothing, the file is copied
  through rather than re-rendered, so quality is untouched and it's fast.
- **It won't redo work.** If the cleaned cut is already there, the step skips.

## Settings

Set on the step: the head-trim length, the silence-detection threshold and minimum silence
length, whether to trim leading and trailing silence, and the tolerance at the edges. An
invalid combination fails the step immediately rather than waiting — the error names the
problem.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| Waiting with no error | The recording isn't downloaded yet | Normal. Check the [Recording Downloader](realtimekit-downloader.md) step. |
| Error about configuration | An invalid combination of trim settings | Correct the step settings, then re-run |
| The cut is much shorter than expected | Long silences at the edges, or an over-long head trim | Check the trim settings; the edit map on the step inspector shows what was removed |
| Whole recording is silent, output is the full original | The empty-cut guard fired deliberately | Expected behaviour — the raw recording is published rather than an empty file |
| Uploaded video is the raw recording, not the cut | The cleaned file was missing when the upload ran | Re-run this step, then reset the upload step so it picks up the cut |
| Old cut files left behind after a re-run | Re-running writes a new derived file | Harmless; an administrator can clean up orphaned derived files |

## Technical reference

| | |
|---|---|
| **Step type** | `video_editor` |
| **Runs after** | `realtimekit_downloader` |
| **Feeds** | `youtube_video_upload` (prefers the cleaned cut when its file exists) |
| **Reads** | `config["iris.downloads"]["recording"]`; step settings `head_trim_ms`, `silence_noise_db`, `min_silence_ms`, `trim_leading_silence`, `trim_trailing_silence`, `edge_tolerance_ms` |
| **Writes** | `config["iris.downloads"]["edited_recording"]`, `config["iris.downloads"]["edit_map"]` |
| **Needs on the server** | `ffmpeg`, `ffprobe` |

Derived files are written beside the raw recording with an `edited_` prefix, so archiving and
cleanup treat them like any other downloaded artefact. Both the read and write paths are
checked to stay inside the media root — this step both creates and deletes files.
