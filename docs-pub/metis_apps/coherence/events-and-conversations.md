# Coherence: Events & Conversations

The METIS-UI side of Coherence — where recorded conversations live before IRIS ever touches
them. For the publishing pipeline itself (drafts, cover images, approval, IRIS), see
the [IRIS documentation](iris/README.md) — starting with
[What IRIS does](iris/what-iris-does.md) and [How IRIS works](iris/how-iris-works.md).
For the RAG chatbot that answers questions from your
conversation content, see [CoCo Agent](coco-agent.md).

> This page assumes you can already find your way around the app (see
> [Getting started](../../web/app/getting-started.md) and
> [Focus](../../web/app/focus-and-scoping.md)) and have Coherence access.

---

## 1. Events

A Coherence **Event** is a holon — the same kind of thing as a person or an organisation, just
of the Coherence Conversation class — that acts as the container a Conversation belongs to.
It isn't a special model with its own fields for dates or locations; it's a Focus-able holon
you create like any other, with its own Journey for tracking the event itself (planning,
follow-up, etc.) separate from the conversations that happen under it.

**Creating an Event:**

1. From the Coherence Events list, use **Create Event**.
2. Choose a **parent holon** — defaults to your current Focus if you have one selected.
3. Give it a **name** and optional **description**.
4. Choose a **Journey** — the holon-relationship journey that tracks the event's own
   progression (not the conversation publishing journey; that's chosen per-conversation, see
   below).
5. Optionally set a **responsible** user, a **follow-up date**, and an initial **comment**.

If no journeys are configured for holon-relationship tracking in Coherence yet, the create
form tells you so instead of a blank journey picker — ask an admin to add one.

## 2. Conversations

A **Conversation** is the recorded-meeting record: participants, start/finish times, the
recording once captured, and everything IRIS generates from it. Every conversation belongs to
exactly one Event.

**There is no manual "create conversation" button.** Conversations are created automatically
when a scheduled meeting comes in through the cal.com booking webhook (below). If you need a
conversation, book it — you won't find a blank form to fill one in by hand.

Once a conversation exists, you manage it from:

- **List / Table / Kanban / Calendar views** — the usual ways to browse conversations, filter
  by journey/step, and see what's scheduled or in progress.
- **The conversation detail page** — participants, connected holons (the organisations/people
  it's associated with beyond participants), the transcript once available, and the whole IRIS
  publishing pipeline. This is where you'll spend most of your time once a conversation exists
  — see [Using IRIS](iris/using-iris.md) for the pipeline side of that page.

### Participants

The chips under the conversation title are its participants. **+ Add** opens a small form with
two ways to fill it:

- **Person** — search for someone METIS already knows.
- **…or create a new person** — type a full name for someone it doesn't. They are created and
  added to the conversation in one step; everything else about them (contact details,
  memberships) can be filled in later on their own page. If you'd rather record all of that up
  front, the **Full create form** link opens the normal Create Person page in a new tab.

If the transcript has speakers nobody has been matched to yet, the same form offers **Assign to
speaker**, so the person you just added is attributed in the transcript straight away.

Type a name METIS already has and the form stops to say so, with a link to who already holds it.
That is a warning, not a refusal: if it's the same person, find them in the search instead — a
second record splits their history. If it's genuinely someone else with the same name, **Create
anyway** proceeds. METIS never treats a name as proof of identity, because attributing a
recording to the wrong human is much harder to undo than a duplicate record.

Creating people is permission-gated: if you can't create people in METIS, the form offers only
the search.

### Materials and Resources

A conversation has two link fields for supporting material, and **which one you use decides
who can see it**:

| Field | Visibility | For |
|---|---|---|
| **Materials** | Private — CRM only | Agendas, working docs, drafts, internal recordings |
| **Resources** | Public — shows on the conversation's public page | Anything meant for readers |

Both work the same way. Open the Links editor, use **Add link** for each one, reorder with the
arrows, remove with ×. Each holds as many links as you need.

Give each link a **label**. It becomes the visible text, which matters here more than
anywhere: a Google Doc address is an opaque hash, so five unlabelled rows are five rows
nobody can tell apart. Leave a label blank and the address shows instead.

There is deliberately **no per-link privacy toggle** — visibility belongs to the field, not the
row. That is why there are two fields rather than one: a switch on every row would make "what
is public about this conversation" impossible to answer at a glance. If you are unsure where a
link belongs, put it in Materials; moving it to Resources later is a copy and a delete.

Limits: 20 links per field, labels up to 120 characters, addresses must start with `http://`
or `https://`, and the same address twice in one field is rejected.

## 3. The cal.com webhook

Each person in METIS has a personal cal.com webhook URL. Wiring it up is a one-time step per
person who takes bookings:

1. Open your **profile**, find the **Your Webhooks** section, and copy the **Coherence
   Conversation cal.com** URL shown there.
2. In your cal.com account, add that URL as a webhook destination (cal.com will send a test
   request to confirm it's reachable before saving).

Once wired up, cal.com sends METIS a webhook on each of the following, and Coherence reacts
automatically — no manual entry:

| cal.com event | What happens in METIS |
|---|---|
| Booking created | A new Conversation is created, matched participants are attached, and a note records the booking. |
| Booking rescheduled | The existing conversation's start/finish times are updated; a note records the change. |
| Booking cancelled | A note records the cancellation, then the conversation is deleted. |

The booking's video-call link determines which conversation **Journey** the new conversation
is placed on — cal.com event types are matched to Journeys by that link's slug. If a booking
doesn't match a known journey, no conversation is created; instead an error note is attached
to your profile so you can see what needs fixing. Any booking attendee METIS can't match to an
existing Person is also flagged with an error note rather than silently dropped.

---

## Common gotchas

- **"I don't see a create-conversation button"** — expected; see §2. Book the meeting via
  cal.com instead.
- **A booking didn't create a conversation** — check your profile for an error note; it's
  almost always an unmatched Journey (video-call link slug doesn't map to a configured
  Journey) or an unmatched attendee.
- **"Why can't I see this Event/Conversation?"** — a Focus or permissions matter, not a bug;
  see [Focus](../../web/app/focus-and-scoping.md) and
  [Access & permissions](../../core/access-and-permissions.md).
