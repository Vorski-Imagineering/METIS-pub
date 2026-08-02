# Telegram Distributor

Sends the "here it is" announcement straight to Telegram, through the bot you choose, to the
groups and people you choose. It also keeps a record of the announcement on the conversation, but
that record is a receipt, not the delivery mechanism.

## At a glance

| | |
|---|---|
| **Needs** | The title, the video URL, and a configured Telegram agent |
| **Produces** | Telegram messages to the configured destinations, plus a note on the conversation as a record |
| **Waits when** | The title or the video URL isn't ready, Telegram is rate-limiting, or a LinkedIn post's public link is still being resolved (up to 6 hours) |
| **Re-running** | Safe — only destinations not yet delivered are retried |

## What it does

Composes a message containing the title, the video link, and — when the journey published them —
the LinkedIn post links, each labelled with who published it. It sends that message directly,
through the bot named in **Telegram agent** below, to every destination the checked scopes
resolve to for this conversation.

It also records the same message as a note on the conversation, purely as an activity record —
that note does not itself cause any delivery.

This is distinct from the participant messages sent by
[Publish Live Notifier](publish-live-notifier.md), which go to individual people through their
own linked account. This one is a broadcast to groups (and, if **Participants** is checked, to
individuals too) through a single bot identity you choose.

### Which bot, and where

Two things decide the fan-out:

- **Telegram agent** — which agent's Telegram bot sends the message. Only bots that reach
  somewhere send anything: a group or person must have separately connected to that specific bot
  (via `/connect`) before this step can reach them. Nothing is ever sent to a destination that
  never invited that bot.
- The **scope checkboxes** — which sources of destinations to use, described in
  [Settings](#settings) below.

The step's panel on a conversation previews the resolved destinations for this bot: which
targets are reachable, and which are in scope but have never connected this particular bot (so
nothing will be sent to them). That second list is the thing to check first when a destination
that "should" get the message doesn't.

### What it says

The copy is yours to edit, in **Telegram message template** — the same editing as the notifier
steps' message templates, and the same variables in braces filled in from this conversation. The
built-in copy announces the episode, links the video, lists whichever LinkedIn posts were
published (each named by its author), and asks people to reshare.

One difference from the notifier steps: this message goes to shared channels, so there is no
person to address and no personal review or opt-out link to include. A signed link here would
hand one participant's opt-out to everyone in the room.

The step's panel on a conversation shows the message rendered against that conversation's real
data, so you can read exactly what would go out before running it. If a template edit breaks the
copy, the panel says so there, and the step refuses to run rather than broadcasting half a
message.

## Settings

| Setting | Default | Notes |
|---|---|---|
| Telegram agent | *(not configured)* | Which agent's Telegram bot delivers the message. Required — the step refuses to send, with a clear error, until this is set. Only agents with a configured Telegram bot token are offered. |
| Event holon | checked | The conversation's owning Event holon. |
| Ancestor holons | unchecked | The chain above the event, excluding the event itself. Combine with **Event holon** to reach the event plus everything above it. |
| Connected holons | unchecked | Holons explicitly linked to this conversation (`Conversation.connected`). |
| Participants | unchecked | Direct messages to each participant with a Telegram account linked to this step's agent. |
| Telegram message template | built-in | The announcement copy, edited the same way as the notifier steps' copy. Available context: the conversation, title, subtitle, video URL, LinkedIn post URLs and their authors, the suggested LinkedIn post, podcast URL. There is no *person* and no review link — this is one message to shared channels, not a personal one. |

Checking more than one scope unions the results — the same destination reached through two
scopes at once (for example a holon that's both connected and an ancestor) is still messaged
only once.

## How it behaves

- **Missing title or video URL means waiting**, not failing — it's simply ahead of the steps
  that produce them.
- **No Telegram agent configured means a hard stop**, not a guess. The step names no default
  bot; an unconfigured step reports an error rather than picking one.
- **LinkedIn links are optional.** Each is included only if that publisher ran and succeeded;
  their absence never blocks the send. URLs come from the stored post record, never
  reconstructed.
- **Delivery is tracked per destination, not per step.** If some groups receive the message and
  others don't (because Telegram is throttling), a rerun only retries the ones that didn't go
  through — nobody who already received it gets a duplicate.
- **A destination that stops accepting messages from the bot** (it removed the bot, or blocked
  it) is reported as a stale connection rather than retried forever.
- **It won't record the note twice** — once the activity note is recorded on the conversation,
  re-running does not create another.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| Waiting with no error | The title or video URL isn't available yet | Normal. Check the generator and upload steps. |
| Error: no Telegram agent configured | The **Telegram agent** setting is unset | Set it — the step will not guess |
| Error: message template failed to render | The edited copy uses something the template language doesn't accept | Read the message preview on the step's panel, which names the problem, and fix the template |
| A destination in scope never received anything | That target has never connected the configured Telegram agent's bot | Have someone with permission on that group/holon run `/connect` with that bot |
| Note is missing the LinkedIn links | Those publishers didn't run, or didn't reach a published state | Expected. Check the LinkedIn steps if you wanted the links included |
| Some destinations lag behind others | Telegram rate-limited a batch send | Expected under load — the step retries the remaining destinations on its own schedule |
| Duplicate messages in Telegram | Rare — would mean the per-destination delivery record was cleared (for example by a reset) | Check the step's inspector for the recorded destinations |

## Technical reference

| | |
|---|---|
| **Step type** | `telegram_distributor` |
| **Runs after** | `youtube_video_upload`, and whichever LinkedIn publishers the journey runs |
| **Feeds** | nothing — terminal step |
| **Waits on (gates, not errors)** | `fields.title`, `records.youtube.video_url` |
| **Optional inputs** | `records.linkedin.organization_post`, `records.linkedin.member_post` — included only when published |
| **Bounded wait** | Up to 6 hours for each published post's `public_url`, the link that opens for people not signed into LinkedIn. The same wait `publish_live_notifier` honours — this broadcast reaches community channels, so it must never carry a worse link than the participant email. See [LinkedIn Publisher](linkedin-publisher.md) |
| **Writes** | `records.telegram` — the activity note id, and per-destination delivery/failure records |
| **Delivery** | Sent directly by this step, through the agent named in **Telegram agent** (`telegram_agent`), to destinations resolved by the scope checkboxes (`telegram_scopes`) and filtered to ones connected to that bot |
| **Copy** | `telegram_text_template` — rendered once per run; the same text is sent to every destination and stored as the activity note |
