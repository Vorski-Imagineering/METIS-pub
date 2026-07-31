# Publish Notifier (and Publish Waiter)

The consent gate. The **Notifier** tells every participant what's about to be published, gives
them a personal review-and-opt-out link, and states the publish-by date. The **Waiter** then
holds the pipeline until that date passes, everyone confirms early, or someone opts out.

Two steps, one mechanism — a journey needs **both**. See also
[Publish Live Notifier](publish-live-notifier.md), the "it's live" announcement that goes out
afterwards.

## At a glance

| | |
|---|---|
| **Needs** | The title, the unlisted video URL, and a way to reach every participant |
| **Produces** | A personal notification per participant, and the clock the waiter counts down |
| **Waits when** | Any participant hasn't been reached yet — see *It blocks rather than skipping* |
| **Re-running** | Safe — anyone already notified is never notified twice |

## What it does

For each participant on the conversation, it sends a personal message containing the unlisted
video, the title and subtitle, and a signed link to their own review page — where they can
read the LinkedIn draft, edit it, confirm, or opt out.

Once **every** participant has been reached, it starts a single shared clock. The Publish
Waiter reads that clock and holds the pipeline until one of three things happens:

- **everyone confirms** → publishing proceeds immediately;
- **the publish-by date passes** → publishing proceeds;
- **anyone opts out** → publishing stops, and no deadline overrides it.

The publish-by date is not a field on this step: it comes from the Publish Waiter's grace
period, because the waiter is what actually enforces it. A journey with a notifier and no
waiter is a misconfiguration — the editor flags it and the step refuses to run rather than
promising a date nothing will honour.

## Channels are independent, not a fallback

Two delivery channels can be enabled on the step: **email** and **Telegram**. For each enabled
channel, a participant gets that channel's message if they have the matching contact detail —
an email address on their Person record, or a linked Telegram account.

**There is no cross-channel fallback and no suppression.** Someone with both an email address
and a linked Telegram gets **both** messages. The channel setting is a step-wide toggle for
what's allowed, not a per-person priority order. To send Telegram only, turn email off on the
step; don't expect Telegram to "win".

**Telegram here is a personal direct message**, sent to the participant's own linked account —
never a group or holon channel. That is deliberate: the message can carry a personal review and
opt-out link, which must not land somewhere other people can use it. Announcements to shared
channels are a different step, [Telegram Distributor](telegram-distributor.md).

The Telegram channel sends through the bot chosen in **Telegram agent** below (see
[Settings](#settings)). A participant is only reachable on Telegram if they've connected their
own account to that specific bot — connecting to a different agent's bot doesn't count. If
**Telegram agent** isn't set, the Telegram channel can't be used even if it's checked on above:
the step reports an error rather than guessing which bot to send through.

The step's panel on a conversation lists every participant with the address and linked account
it resolved for them, flags anyone missing one, and marks anyone already delivered on an earlier
run — so who the next run will message is visible before it runs.

## It blocks rather than skipping

After trying every enabled channel, each participant lands in one of three outcomes:

1. **Delivered** on at least one channel — recorded, done, never contacted again by this step.
2. **No channel available** — no email on file *and* no linked Telegram.
3. **Attempted but failed** — something went wrong sending.

If **anyone** is in (2) or (3), the step waits and retries instead of moving on, and the
retry message names who and why. Practically: **one unreachable participant blocks the whole
publishing pipeline** until someone adds their contact details.

That is the intended behaviour, not an oversight. Publishing goes ahead by default when the
deadline passes — so a participant who was never told cannot object, and would find out by
seeing themselves published. Blocking is the safe direction to fail in.

Sends that already succeeded are saved before any error is raised, so a retry never
re-notifies someone who was already reached.

## Previewing before it goes out

Use **Send test…** on the step. It renders the real copy against this conversation for a
chosen participant and offers two sends:

- **Send to me** — delivered to you, re-rendered with your own review link, so a participant's
  live opt-out link never lands in someone else's inbox.
- **Send to \<participant\>** — their real message with their real live link. It's an
  irreversible message to a real person, so it asks for confirmation, and it's only offered on
  channels this step actually has enabled.

Neither writes anything to the conversation, so no test can make the step think it has already
notified someone. The modal also shows "no email on file" / "no linked Telegram" for the
previewed participant, and warns if they're unreachable on every enabled channel — with a
reminder that a real run does not skip them.

The header block in the modal shows the **From** address and any **Bcc** actually in effect, so
a test uses the same mailbox and the same server a scheduled run would.

## Settings

| Setting | Default | Notes |
|---|---|---|
| Channels | email + Telegram | Which delivery methods this step may use. Unchecking both leaves every participant unreachable. |
| Telegram agent | *(not configured)* | Which agent's Telegram bot sends the Telegram channel's messages. Only relevant while Telegram is a checked channel; leaving it unset while Telegram is enabled is an error, not a fallback to some default bot. |
| *(publish-by date)* | — | Not set here. Read from the Publish Waiter's grace period and shown read-only. |
| Review link validity | 30 days | How long each participant's signed link stays usable. Only relevant if your templates include the review link — the default copy deliberately doesn't. |
| Reply-to | blank | Optional staff inbox for "reply to this email". |
| Bcc | blank | Optional single monitoring address; combined with the agent-wide one. |
| Message templates | built-in | Email subject, email body, and Telegram body. Available context: the person, the conversation, title, subtitle, video URL, review URL, publish-by date, LinkedIn post, podcast URL, reply-to. Emails are plain text. |

### The sending mailbox

Notifier steps send from a mailbox configured on the agent — host, port, and From address are
required; username, password, TLS/SSL and timeout are optional; an optional bcc copies every
participant message to a monitoring address.

**There is no fallback to the platform mail server.** An agent with no mailbox configured, or a
partial one, fails the step with an error naming what's missing and sends nothing. That is
deliberate: the alternative is real notifications going out successfully, to real people, from
whatever the platform default happens to be — with no symptom until someone reads a delivered
header. A blank From address is rejected for the same reason.

The mailbox is only needed by a step that actually sends email; a Telegram-only step never
opens a connection.

A bcc set on the step and one set on the agent add together, and the same address in both is
still only sent once. A malformed bcc can never block a real notification — bad addresses are
dropped before the message is built. The bcc is a header on each participant's own message, so
the monitoring inbox receives one copy per participant, not one per conversation.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| Step waits, note names people with "no email or linked Telegram" | Those participants have no reachable channel | Add an email address or link their Telegram, then let it retry — it clears itself |
| Step waits, note says "delivery failed (will retry)" | A send errored — a bad address, an SMTP problem | Check the address; check the mail server is reachable. It retries automatically |
| Error: mailbox not configured / missing From address | The agent has no usable email block | An administrator configures the sending mailbox on the agent |
| Error: Telegram enabled but no bot configured | **Telegram agent** is unset while Telegram is a checked channel | Set **Telegram agent**, or uncheck Telegram if it isn't meant to be used here |
| Participant has a linked Telegram but never receives a message | They connected a different bot than the one set in **Telegram agent** | Have them run `/connect` with the bot this step actually uses |
| Nobody received anything and there's no error | The step hasn't run yet, or the video/title it waits on isn't ready | Check the inspector's Reads row for ○ inputs |
| A participant got two messages | They have both an email address and a linked Telegram | Expected — channels are independent. Turn one off on the step if you don't want both |
| Someone was notified twice across runs | Shouldn't happen — delivery is recorded per person | If it did, the per-person record was cleared; check whether the step was reset |
| Waiter never releases | Someone opted out, or the clock never started because the notifier is still blocked | Check the notifier step first; an opt-out is a deliberate full stop and must be resolved with that person |
| Publishing went ahead without anyone confirming | The publish-by date passed and nobody objected | Working as designed — silence is consent, which is why the date is stated in every message |
| Monitoring inbox stays empty | The bcc value isn't a single usable address | Re-check it; a bad legacy value is dropped with a log warning rather than failing the step |

## Technical reference

| | |
|---|---|
| **Step types** | `publish_notifier`, `publish_waiter` |
| **Runs after** | `youtube_video_upload` (needs the unlisted video URL) |
| **Feeds** | `publish_waiter`, and through it every publishing step |
| **Waits on (hard gates)** | `fields.title`, `records.youtube.video_url` |
| **Optional input** | `fields.linkedin_post` — enrichment only; its absence never blocks the announcement |
| **Writes** | `records.publish_notify.people.<person_id>` = `{notified_at, channels}` per delivered participant; `records.publish_notify.notified_at`, the single shared clock, set only once **every** participant is recorded. The waiter writes `publishing_status` |
| **Needs on the agent** | An `email` block: `host`, `port`, `from_email` required; `username`, `password`, `use_tls`/`use_ssl`, `timeout`, `bcc` optional |
| **Telegram delivery** | Sent through the agent named in **Telegram agent** (`telegram_agent` in the step config); a participant with no linked account *to that agent* is treated as "channel not available", not an error. Unset while Telegram is enabled is a permanent config error, not a runtime guess |

The bcc was previously a top-level `email_bcc` key. That spelling is still read so existing
setups keep working, and `email.bcc` wins if both are set — but an agent carrying *only*
`email_bcc` has no mailbox and cannot send.
