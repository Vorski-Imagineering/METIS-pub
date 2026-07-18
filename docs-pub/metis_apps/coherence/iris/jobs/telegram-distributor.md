# Telegram Distributor

| | |
|---|---|
| **Label** | Telegram Distributor |
| **Slug** | `telegram_distributor` |
| **File** | `metis_apps/coherence/iris_telegram.py` |
| **Class** | `TelegramDistributor` |
| **Depends on** | `youtube_uploader`, `linkedin_publisher` |

## Purpose

Creates a formatted **Note** on the conversation; delivery is delegated entirely to the
existing `metis_telegram_update` scheduled job. This job does **not** call Telegram directly.

The other of the two multi-dependency jobs.

## Pipeline position

- **Upstream (`depends_on`):** `youtube_uploader` **and** `linkedin_publisher`.
- **Feeds into:** nothing (terminal stage).
- **Alternative to:** none.

## Data flow

**Reads**
- `infos["publishing"]["title"]` and `infos["publishing"]["youtube"]["video_url"]` — both
  **wait-gates** (see below).
- `infos["publishing"]["linkedin"]["posts"]` — **optional**; post URLs are included only if
  available.

**Writes**
- `infos["publishing"]["telegram"]["note_id"]`, `["note_created_at"]`.

## Requirements

- **Agent.config:** none.
- **System:** none.
- **External credentials:** none in this job — Telegram delivery is handled by the separate
  `metis_telegram_update` job, which reads the destination from the target's
  `config["telegram-channel"]`.

## Behavior details

- **Wait-gates (not hard errors):** a missing `title` or missing
  `youtube["video_url"]` raises **`RetryLater`** (waits for content generation / YouTube
  upload) — it does not error. (IRIS.md's older "required" wording described these as
  required; in the code they are `RetryLater` gates, verified in `iris_telegram.py`.)
- **Graceful degradation:** LinkedIn post URLs are included only when present; their absence
  is not a gate.
- **Idempotency:** skips if `telegram.note_id` is already set.
- **Delivery boundary:** this job's success means the **Note exists**. Whether/when it
  reaches Telegram is up to `metis_telegram_update` and the target having a
  `telegram-channel` configured (see `docs/dev/agents/telegram-linking.md`).
- **Done vs error:** "done" once the Note is created; permanent error only on a bad step
  config.

## Step slug convention

`"telegram_distributor"` (matches `config["iris_job"] = "telegram_distributor"`).

## Testing this step

No automated test today. Manual scenario (staging): with a title and a YouTube `video_url`
present, run → a Note is created and `infos["publishing"]["telegram"]["note_id"]` is set;
omit the video URL → `RetryLater` (no error). To verify end-to-end delivery, ensure the
target has `config["telegram-channel"]` set and let `metis_telegram_update` run. See the
*testing guide* (internal engineering doc, not published here).

## Related runbooks

- *manual-retrigger* (internal engineering doc, not published here)
- *consent-withdrawal* (internal engineering doc, not published here).
