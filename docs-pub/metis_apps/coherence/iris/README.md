# IRIS — the conversation publishing pipeline

IRIS takes a recorded conversation and carries it all the way to published media: transcript,
title and description, social copy, branded images, a hosted video, participant consent, and
distribution. It does the repeatable production work; people keep control of the message.

**If you read one page, read [How IRIS works](how-iris-works.md).** Almost every question
people ask about IRIS ("why hasn't it moved?", "did it fail?", "can I re-run this?") is
answered by understanding one thing: IRIS is a line of small steps, each run on a timer, each
either doing its work and passing the conversation along, or quietly waiting.

---

## Start here

| If you are… | Read |
|---|---|
| **A participant** who got a link asking you to review a conversation | [Participant review guide](participant-review.md) |
| **New to IRIS** and want to know what it's for | [What IRIS does](what-iris-does.md) |
| **Running conversations** through the pipeline day to day | [How IRIS works](how-iris-works.md), then [Using IRIS](using-iris.md) |
| **Stuck** — something hasn't moved, or shows an error | [Troubleshooting](troubleshooting.md) |
| **Setting a journey up** — choosing steps, wiring a channel | [The pipeline steps](steps/README.md), [Writing prompts](writing-prompts.md), [YouTube setup](youtube-setup.md) |
| **Connecting a YouTube channel** and unsure which Google account can do it | [YouTube accounts and channel access](youtube-accounts.md) |

## The pages

### Understanding it

- **[What IRIS does](what-iris-does.md)** — the plain-English overview: what goes in, what
  comes out, and where people stay in charge.
- **[How IRIS works](how-iris-works.md)** — the mental model. Journeys, steps, the timer that
  runs them, the three things a step can do, and why it is built this way.

### Doing the work

- **[Using IRIS](using-iris.md)** — the click-path for staff: where each panel is on the
  conversation page and what to do at each stage.
- **[Participant review guide](participant-review.md)** — written for the people asked to
  approve what gets published. Safe to forward.
- **[Troubleshooting](troubleshooting.md)** — why a conversation isn't moving, what error
  notes mean, and what resetting a step does (and can't undo).

### Setting it up

- **[The pipeline steps](steps/README.md)** — one reference page per step: what it needs, what
  it produces, and when it waits. Use it to design a journey or to understand one step deeply.
- **[Writing prompts](writing-prompts.md)** — customising the AI instructions that generate
  titles, descriptions, LinkedIn posts, and quotes.
- **[YouTube setup](youtube-setup.md)** — connecting a journey to a YouTube channel: the Google
  Cloud project, the OAuth client, and the Connect click-path.
- **[YouTube accounts and channel access](youtube-accounts.md)** — which Google account can
  connect a channel. Personal vs Brand Account channels, and why Studio Manager/Editor access
  isn't enough. Read it before the first connection, or when the channel you want isn't offered.

---

## The shape of it, in one picture

```
  a conversation is recorded
            │
            ▼
   ┌─────────────────────────────────────────────┐
   │  the recording is fetched and transcribed   │
   │  the draft is written by AI                 │   ← you review and edit here
   │  images are rendered, video is uploaded     │      (video stays unlisted)
   └─────────────────────────────────────────────┘
            │
            ▼
   ┌─────────────────────────────────────────────┐
   │  participants are asked to review           │   ← consent gate: everyone
   │  the pipeline waits                         │      confirms, or the date passes
   └─────────────────────────────────────────────┘
            │
            ▼
   ┌─────────────────────────────────────────────┐
   │  video goes public, LinkedIn posts go out,  │
   │  podcast is published, links are announced  │
   └─────────────────────────────────────────────┘
```

Each box is several individual steps. Which ones a given conversation runs depends on its
journey — see [the step reference](steps/README.md) for the full list and how they connect.
