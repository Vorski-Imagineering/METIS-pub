# Publish Live Notifier

Tells every participant it's live, with the public links — the YouTube video and, if the
journey published there, the LinkedIn post.

This is the sibling of [Publish Notifier](publish-notifier.md), which is the *pre*-publish
"here's what we're about to publish, here's your opt-out" message. This one carries no opt-out
link and no deadline: publishing has already happened, there's nothing left to decide.

## At a glance

| | |
|---|---|
| **Needs** | The video actually public, plus any LinkedIn posts the journey publishes |
| **Produces** | A personal "it's live" message per participant |
| **Waits when** | The video isn't public yet, or a LinkedIn post the journey runs hasn't been published |
| **Re-running** | Safe — anyone already told is never told twice |

## What it does

Everything [Publish Notifier](publish-notifier.md) does — the same per-participant fan-out,
the same independent email and Telegram channels, the same refusal to silently skip someone
unreachable, the same guarantee that a retry never re-notifies. Only the message differs.

It keeps its own separate delivery record, so re-running one notifier never affects the
other's history.

## What it waits for

- **The video must actually be public.** The step waits until the visibility flip has
  happened; an "it's live" message linking to an unlisted video would simply be false.
- **LinkedIn links, if the journey publishes them.** If the journey includes a Page publisher,
  this step waits for that post's URL; likewise for a member publisher. A journey with neither
  skips both waits and goes out YouTube-only. This is worked out by looking at what the
  journey actually runs, not by a fixed rule.

## Settings

The same shape as [Publish Notifier](publish-notifier.md), minus everything to do with
consent: channels, **Telegram agent**, an optional bcc, and the message templates (subject, email
body, Telegram body). There is no review-link expiry and no grace period, because nothing here
asks the participant to decide anything.

**Telegram agent** is its own setting on this step — it is not shared with Publish Notifier. A
journey can announce the pre-publish notice through one agent's bot and the "it's live" message
through another, though most journeys use the same one for both. See [Publish Notifier →
Settings](publish-notifier.md#settings) for what the setting means and how it's validated.

Template context omits the review URL and publish-by date, and adds the LinkedIn post URLs and
author names so the copy can label each link with who published it.

The sending mailbox is the agent-level one shared with the pre-publish notifier — see
[Publish Notifier → the sending mailbox](publish-notifier.md#the-sending-mailbox). Without it
this step fails rather than falling back to the platform mail server.

**Send test…** works exactly as it does on the pre-publish notifier.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| Waiting with no error, video still unlisted | The visibility promote step hasn't run | Check that step; this one is correctly refusing to announce something that isn't live |
| Waiting although the video is public | A LinkedIn step in the journey hasn't published yet | Check the LinkedIn publisher steps — this step waits for their post URLs |
| Waiting on a LinkedIn link the journey shouldn't publish | An unused LinkedIn step is still active on the journey | Remove or archive the step; the wait is derived from what the journey runs |
| Note names people with no email or linked Telegram | Those participants have no reachable channel | Add contact details; it retries and clears itself |
| Error: mailbox not configured | The agent has no usable email block | An administrator configures it — see [Publish Notifier](publish-notifier.md#the-sending-mailbox) |
| Error: Telegram enabled but no bot configured | This step's own **Telegram agent** setting is unset | Set it — it's independent of Publish Notifier's setting, even if the two usually match |
| Participants got the "it's live" message twice | The step's own delivery record was cleared by a reset | Delivery is recorded per person; a reset is the only way to repeat it |
| Message links to the wrong LinkedIn post | Both publishers ran and the copy labels them by author | Expected — each link is labelled with who published it |

## Technical reference

| | |
|---|---|
| **Step type** | `publish_live_notifier` |
| **Runs after** | `youtube_visibility_promote`, plus whichever LinkedIn publishers the journey runs |
| **Feeds** | `telegram_distributor` (a separate, unrelated notification — a note, not a per-participant fan-out) |
| **Waits on (hard gates)** | `records.youtube.promoted_at`, `fields.title`, `records.youtube.video_url` |
| **Journey-conditional waits** | `records.linkedin.organization_post.post_url` and `records.linkedin.member_post.post_url`, each only if the journey runs that publisher |
| **Writes** | `records.publish_live_notify.people.<person_id>` and `records.publish_live_notify.notified_at` — its own prefix, independent of the pre-publish notifier. Nothing downstream currently waits on this clock |
| **Needs on the agent** | The same `email` block as [Publish Notifier](publish-notifier.md) |
| **Telegram delivery** | Sent through the agent named in this step's own **Telegram agent** (`telegram_agent`) — a separate setting from Publish Notifier's, not inherited from it |
