# Publish Live Notifier

| | |
|---|---|
| **Label** | Publish Live Notifier |
| **Slug** | `publish_live_notifier` |
| **File** | `metis_apps/coherence/iris_notify.py` |
| **Class** | `PublishLiveNotifier` (thin subclass of `PublishNotifier`) |
| **Depends on** | `youtube_visibility_promote`, `linkedin_publisher`, `linkedin_member_publisher` |
| **See also** | [Publish Notifier](publish-notifier.md) — the pre-publish "announce + opt-out" step this subclasses |

## Purpose

Announces "it's live" to every conversation participant once the video is actually
public — the public YouTube link and (if the journey publishes there) the LinkedIn
reshare link. No opt-out link or deadline copy: by this point publishing has already
happened, there is nothing left to opt out of.

`PublishLiveNotifier` reuses essentially all of `PublishNotifier`'s fan-out, delivery,
error-handling, and blocking logic — only the records prefix, required reads, and default
templates differ. See [Publish Notifier](publish-notifier.md) for the full mechanics;
this page covers what's different.

## Pipeline position

- **Upstream (`depends_on`):** `youtube_visibility_promote` (video must actually be
  public), plus whichever LinkedIn publisher(s) the journey runs, if any.
- **Feeds into:** `telegram_distributor` (a separate, unrelated notification: a Note for
  `metis_telegram_update`, not this step's per-participant fan-out).
- **Alternative to:** none.

## Data flow

**Reads** (`_required_reads` — hard **wait-gates**, via `RetryLater`, not errors):
- `records.youtube.promoted_at` — gates on the video actually being flipped public; the
  "it's live" copy would be false before this is set.
- `fields.title`
- `records.youtube.video_url`

**Journey-conditional reads:** if the journey includes a `linkedin_publisher` step, this
step additionally waits for `records.linkedin.organization_post.post_url`; if it includes
`linkedin_member_publisher`, it additionally waits for
`records.linkedin.member_post.post_url`. A journey with neither LinkedIn step skips both
gates and stays YouTube-only — determined by inspecting the journey
(`journey_steps_with_job`), not declared as static reads, since the requirement depends
on what the journey actually runs.

**Writes**
- `records.publish_live_notify.people.<person_id>` — same shape as
  `records.publish_notify.people.<id>` (see [Publish Notifier](publish-notifier.md)), but
  under this step's own prefix — a separate per-participant record from the pre-publish
  notifier, so re-running one never affects the other's delivery history.
- `records.publish_live_notify.notified_at` — this step's own clock. Nothing downstream
  currently waits on it (unlike `publish_notify.notified_at`, which gates
  `publish_waiter`); it exists for symmetry and idempotency tracking.

## Channels and blocking behavior

Identical to [Publish Notifier](publish-notifier.md#channels-independent-not-a-fallback):
email and Telegram are independent, both-if-available, no cross-channel fallback, and a
participant unreachable on every enabled channel (or a channel that fails to send)
raises `RetryLater` rather than being silently skipped — see that page for the full
per-outcome breakdown (`no-channel` vs `send-failed`) and the idempotency guarantee that
already-delivered participants are never re-notified.

## Requirements

Same as [Publish Notifier](publish-notifier.md#requirements): `Agent.config["email_bcc"]`
(optional, shared across both notifier steps), a step-local `bcc` (optional, combined
with the Agent-level one), outbound email, and — if Telegram is enabled — a configured
Telegram bot token.

## Step slug convention

`"publish_live_notifier"` (matches `config["iris_job"] = "publish_live_notifier"`).

## Step config fields

Set via the journey editor's step-config panel
(`templates/coherence/partials/iris_config_publish_live_notifier.html`) — a subset of
`publish_notifier`'s fields, since there is no opt-out link or grace period to configure
here:

| Field | Default | Notes |
|---|---|---|
| `channels` | `["email", "telegram"]` | Same semantics as `publish_notifier` — see [Channels](publish-notifier.md#channels-independent-not-a-fallback). |
| `bcc` | *(blank)* | Optional debug/monitoring address — a single address; combined with `Agent.config["email_bcc"]`. |
| `email_subject_template`, `email_text_template`, `telegram_text_template` | see `iris_notify_templates.py` (`LIVE_*` constants) | Available context omits `review_url`/`deadline_date` (no opt-out here) but otherwise matches `publish_notifier`: `person`, `conversation`, `title`, `subtitle`, `video_url`, `linkedin_post`, `linkedin_org_post_url`, `linkedin_org_author`, `linkedin_member_post_url`, `linkedin_member_author`, `podcast_url`. |

Unlike `publish_notifier`, there is no `grace_days` or `token_expiry_days` field — this
step doesn't mint a review token, since there's no decision left for a participant to
make.

## Testing this step

**Automated:** covered alongside `publish_notifier` in
`metis_apps/coherence/tests/test_iris_notify.py` (shared fan-out/delivery/blocking logic,
tested once against the base behavior both classes share).

**Manual (staging):** same "send test" flow as `publish_notifier` — the journey editor's
send-test modal supports both notifier slugs identically (`NOTIFIER_JOB_SLUGS =
("publish_notifier", "publish_live_notifier")` in `notify_blockers.py`). See
[Publish Notifier § Testing this step](publish-notifier.md#testing-this-step).

## Related runbooks

- *manual-retrigger* (internal engineering doc, not published here)
- *consent-withdrawal* (internal engineering doc, not published here)
