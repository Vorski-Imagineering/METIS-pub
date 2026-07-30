# Telegram Distributor

Writes the "here it is" announcement as a note on the conversation. Something else delivers it
to Telegram.

## At a glance

| | |
|---|---|
| **Needs** | The title and the video URL |
| **Produces** | A formatted note on the conversation |
| **Waits when** | The title or the video URL isn't ready |
| **Re-running** | Safe — skips once the note exists |

## What it does

Composes a note containing the title, the video link, and — when the journey published them —
the LinkedIn post links, each labelled with who published it.

**It does not talk to Telegram.** Delivery is handled by the existing scheduled Telegram
update job, which picks up notes and sends them to whichever channel the target is linked to.
Keeping the two apart means IRIS has one job (say the right thing) and the delivery mechanism
has another (get it to the right place), and neither needs to know how the other works.

So this step succeeding means **the note exists** — not that anything arrived in Telegram. If
the message never shows up, the note is the place to check first: if it's there, the problem is
delivery, not IRIS.

This is distinct from the participant messages sent by
[Publish Live Notifier](publish-live-notifier.md), which go to individual people. This one is a
single broadcast-style note.

### Seeing where it will go

Because the destinations come from the note's references rather than from this step's settings,
the step's panel on a conversation lists them: the sending agent's own channel, each
participant's linked account, the conversation's owning Event holon, and every connected holon
that has a channel — each with its chat ID and forum topic. An empty list is called out
explicitly: the note would be created and delivered to nobody.

A holon links to **one** channel (plus an optional forum topic), not a list. To reach a second
channel, link it on another holon connected to the conversation.

## How it behaves

- **Missing title or video URL means waiting**, not failing — it's simply ahead of the steps
  that produce them.
- **LinkedIn links are optional.** Each is included only if that publisher ran and succeeded;
  their absence never blocks the note. URLs come from the stored post record, never
  reconstructed.
- **It won't post twice** — once the note is recorded on the conversation, re-running does
  nothing.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| Waiting with no error | The title or video URL isn't available yet | Normal. Check the generator and upload steps. |
| Step says done but nothing arrived in Telegram | The note was created; delivery is a separate job | Check the target has a linked Telegram channel, and that the Telegram update job is running |
| Note is missing the LinkedIn links | Those publishers didn't run, or didn't reach a published state | Expected. Check the LinkedIn steps if you wanted the links included |
| Duplicate messages in Telegram | The note was created more than once (for example after a reset) | Check the conversation's notes; delete the extra one |
| Wrong channel | The destination comes from the target's linked Telegram channel, not this step | Fix the link on the target record |

## Technical reference

| | |
|---|---|
| **Step type** | `telegram_distributor` |
| **Runs after** | `youtube_video_upload`, and whichever LinkedIn publishers the journey runs |
| **Feeds** | nothing — terminal step |
| **Waits on (gates, not errors)** | `fields.title`, `records.youtube.video_url` |
| **Optional inputs** | `records.linkedin.organization_post`, `records.linkedin.member_post` — included only when published |
| **Writes** | `records.telegram` — the note id and when it was created |
| **Delivery** | Handled by the separate `metis_telegram_update` job, which reads the destination from the target's linked Telegram channel |
