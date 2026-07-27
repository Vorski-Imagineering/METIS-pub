# Publish Notifier

| | |
|---|---|
| **Label** | Publish Notifier |
| **Slug** | `publish_notifier` |
| **File** | `metis_apps/coherence/iris_notify.py` |
| **Class** | `PublishNotifier` |
| **Depends on** | `youtube_video_upload` |
| **See also** | [Publish Live Notifier](publish-live-notifier.md) — the sibling "it's live" announcement |

## Purpose

Announces the upcoming publish to every conversation participant: the unlisted YouTube
video, a signed personal review/opt-out link, and the publish-by date. Delivery is
attempted on every enabled channel per person (email and/or Telegram — see
[Channels](#channels-independent-not-a-fallback) below), and once every participant has
been delivered-or-recorded-unreachable, this step starts the single clock that
`publish_waiter` waits on.

## Pipeline position

- **Upstream (`depends_on`):** `youtube_video_upload` (needs the unlisted video URL).
- **Feeds into:** `publish_waiter`, which reads `records.publish_notify.notified_at` and
  will not proceed until this step sets it.
- **Alternative to:** none.

## Data flow

**Reads** (`_required_reads` — hard **wait-gates**, via `RetryLater`, not errors):
- `fields.title`
- `records.youtube.video_url`

`fields.linkedin_post` is also declared in the registry `reads` for ordering, but it is
an optional enrichment (the "finished" LinkedIn share post, with the video URL already
inserted) — a missing/empty value never blocks the announcement.

**Writes**
- `records.publish_notify.people.<person_id>` — per participant, once delivered on at
  least one channel: `{"notified_at": "<ISO 8601>", "channels": ["email", "telegram"]}`.
  Only channels that actually delivered are listed; a participant reached only by email
  gets `["email"]`, not both.
- `records.publish_notify.notified_at` — the single shared clock. Set once, only after
  **every** participant has a per-person record (delivered — never for "unreachable";
  see [Blocking behavior](#blocking-behavior-not-a-silent-skip)). `publish_waiter` reads
  this to start its grace period.

## Requirements

- **Agent.config `email`** (**required**) — the mailbox notifications are sent from,
  shared by every notifier step (this step and `publish_live_notifier`):

  | Key | Required | Notes |
  |---|---|---|
  | `host`, `port` | yes | The SMTP server to send through. |
  | `from_email` | yes | The From line, e.g. `IRIS <iris@example.org>`. A display name is kept. |
  | `username`, `password` | no | SMTP credentials, where the server needs them. |
  | `use_tls` / `use_ssl` | no | Mutually exclusive; set at most one. |
  | `timeout` | no | Connection timeout in seconds. |
  | `bcc` | no | A system-wide debug/monitoring bcc applied to every notifier step's participant emails. |

  There is **no fallback to the platform mail server**. An agent with no `email` block,
  or a partial or malformed one, fails the step with an error naming what is missing and
  sends nothing. This is deliberate: the alternative is real participant notifications
  going out — successfully, to real people — from whatever the platform's default sender
  happens to be, with no symptom until someone reads a delivered header. A blank
  `from_email` is rejected for the same reason: it is the one invalid value that would
  still send, because an empty sender is substituted with the platform default.

  The block is only required for a step that actually sends email. With
  `channels: ["telegram"]` the mailbox is never resolved and no connection is opened.

  `bcc` was previously a top-level `email_bcc` key. That spelling is still read, so a
  leftover one keeps working; `email.bcc` wins if both are set. A legacy value that is
  not exactly one usable address is ignored with a warning in the log rather than
  failing the block — a stale debug setting can never stop participant notifications.
  An agent carrying *only* `email_bcc` has no mailbox and cannot send.
- **Step config `bcc`** (optional) — a step-local bcc, combined with (not replacing) the
  Agent-level one; either or both may be set. Each is a single address — a list is
  rejected when the step config is saved.
- **System:** outbound email (`core/email.py`) and, if Telegram is an enabled channel, a
  configured Telegram bot token (see `docs/dev/agents/telegram-linking.md`).
- **External credentials:** none directly in this job — Telegram delivery goes through
  `send_personal_telegram` in `metis_apps/coherence/participant_telegram.py`.

## Channels: independent, not a fallback

`channels` (step config, default `["email", "telegram"]`) controls which delivery
methods this step is *allowed* to use at all. For each enabled channel, each participant
is sent that channel's message **if they have the matching contact info**:

- **Email** — sent if `"email" in channels` and the participant's `Person.email` is set.
- **Telegram** — sent if `"telegram" in channels` and the participant's
  `Person.config["telegram-channel"]` is set (a linked Telegram account).

There is **no cross-channel fallback or suppression**. A participant with both an email
and a linked Telegram account gets **both** messages — the step does not prefer one
channel or skip a channel because the other succeeded. `channels` is a step-wide
operator toggle, not a per-person priority order. If an operator wants Telegram-only
notifications, they must uncheck Email in the step config, not rely on Telegram "winning"
when both are present.

## Blocking behavior (not a silent skip)

Each channel send is wrapped in its own `try`/`except` (logged via `logger.exception`,
not raised) so a failure on one channel or for one participant never aborts the
already-successful sends earlier in the same run — those are persisted first, before any
error is raised, so a retry never re-notifies someone already delivered.

Per participant, after both channels are attempted, there are three outcomes:

1. **Delivered** on at least one enabled channel → recorded in
   `records.publish_notify.people.<id>`, participant is done.
2. **No channel available** — no email on file *and* no linked Telegram, for whichever
   channels are enabled → reason `no-channel`.
3. **Channel(s) attempted but all failed** (exception during render or send) → reason
   `send-failed`.

If **any** participant falls into (2) or (3), the step raises `RetryLater` — it does
**not** silently skip them and move on. The retry message names the two failure classes
separately: `"no email or linked Telegram: <names>"` vs `"delivery failed (will retry):
<names>"`. Practically, this means **one unreachable or failing participant blocks the
entire publishing pipeline** — `publish_waiter` can never start its grace-period clock
until every participant is either delivered or an operator fixes their contact info (adds
an email, links Telegram) so a later retry can reach them.

`send_personal_telegram` itself never raises for "no linked account" or "no bot token
configured" — it returns `False` (with a `logger.warning` if the bot token is entirely
unconfigured). A `False` return is treated identically to "channel not available": no
entry added to that participant's `channels` list, no exception.

- **Idempotency:** a participant with an existing `records.publish_notify.people.<id>`
  record is skipped entirely on rerun — never re-notified.
- **Done vs error:** "done" (starts the clock) only once every participant is recorded;
  permanent (non-retry) error only on an invalid step config or zero participants on the
  conversation.

## Step slug convention

`"publish_notifier"` (matches `config["iris_job"] = "publish_notifier"`).

## Step config fields

Set via the journey editor's step-config panel
(`templates/coherence/partials/iris_config_publish_notifier.html`):

| Field | Default | Notes |
|---|---|---|
| `channels` | `["email", "telegram"]` | Checkboxes; unchecking both is allowed by the form but leaves every participant unreachable — see [Blocking behavior](#blocking-behavior-not-a-silent-skip). |
| *(grace period)* | — | Not a field on this step. The publish-by date announced here is read from the sibling `publish_waiter` step's `grace_days`, because the waiter is what enforces it. The editor shows the resolved value read-only. A journey with this step and no waiter is a misconfiguration: the editor shows an error and the step refuses to run rather than promising a date nothing will honour. |
| `token_expiry_days` | `30` | How long each participant's signed review/opt-out link stays valid. Only has an effect if your templates use `review_url` — the default copy deliberately does not. |
| `reply_to` | *(blank)* | Optional staff inbox for a "reply to this email" fallback in the copy. |
| `bcc` | *(blank)* | Optional debug/monitoring address — a single address; combined with `Agent.config["email"]["bcc"]`. |
| `email_subject_template`, `email_text_template`, `telegram_text_template` | see `iris_notify_templates.py` | Django template strings. Available context: `person`, `conversation`, `title`, `subtitle`, `video_url`, `review_url`, `deadline_date`, `linkedin_post`, `podcast_url`, `reply_to`. Emails are plain text only (no HTML alternative) — nothing is escaped, so the templates render apostrophes/ampersands raw rather than as HTML entities. |

## Testing this step

**Automated:** `metis_apps/coherence/tests/test_iris_notify.py` covers: successful
dual-channel delivery, email-only and Telegram-only delivery, a participant with no
channel blocking and not starting the clock
(`test_participant_with_no_channel_blocks_and_does_not_start_clock`), a failed send
blocking without recording or starting the clock
(`test_failed_send_blocks_and_does_not_record_or_start_clock`), and idempotency across
retries.

**Manual (staging):** use the journey editor's "send test" on this step — it renders the
real copy against the real conversation for a chosen participant, and on either channel
offers two sends: **Send to me** delivers it to the operator, re-rendered with their own
review link so a participant's live opt-out link never lands in someone else's inbox, and
**Send to &lt;participant&gt;** delivers that participant their own real copy, including
their real live opt-out link — an irreversible message to a real person, so it asks for
confirmation first and is offered only on channels this step actually has enabled.
Neither send writes to the publishing store, so no test can make the step think it has
already notified someone (see
`metis_apps/coherence/templates/coherence/partials/iris_notify_test_modal.html` and
`views/notify_test.py`). It shows per-channel "no email on file" / "no linked Telegram"
text for the previewed participant, and a warning banner if that participant is
unreachable on every enabled channel, explicitly noting that a real run does **not** skip
them. See the *testing guide* (internal engineering doc, not published here) for the
full manual pipeline walkthrough.

## Related runbooks

- *manual-retrigger* (internal engineering doc, not published here)
- *consent-withdrawal* (internal engineering doc, not published here)
