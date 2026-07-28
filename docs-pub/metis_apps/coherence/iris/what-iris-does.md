# What IRIS does

IRIS turns a recorded conversation into a finished, reviewed, published media package.

Without it, publishing one conversation means someone downloading the recording, getting it
transcribed, writing a title and a description, drafting social copy, making a thumbnail,
uploading the video, chasing everyone for approval, and finally posting it in four places —
each handoff a chance for the whole thing to stall. IRIS does the repeatable parts and keeps
the judgement calls with people.

**How the machinery works** — the timer, the steps, why things wait — is
[How IRIS works](how-iris-works.md). This page is what it produces and why that's worth
having.

---

## What goes in, what comes out

**In:** a recorded conversation, its participants, and the journey it should follow.

**Out:**

- a transcript, with speakers attributed to real people;
- a title, subtitle, and internal summary;
- a YouTube description;
- LinkedIn post copy;
- pull quotes suitable for sharing;
- branded images — video thumbnail, LinkedIn header, quote cards;
- a hosted video, unlisted for review and then public;
- a podcast episode;
- a record of who was asked, who approved, and when;
- the published links, sent to everyone who took part.

Which of these a given conversation produces depends on the steps in its journey. Nothing is
all-or-nothing — a journey that only wants a transcript and a summary is a valid journey.

## The stages

### It collects the raw material

The meeting recording is fetched automatically and attached to the conversation, and a
transcript is produced — either imported from the meeting provider or generated from the
audio. From that point everything lives with the conversation record: the people, the
recording, the transcript, the drafts, and the publishing state.

### It writes a first draft

One pass over the transcript produces the title, subtitle, summary, YouTube description,
LinkedIn copy, and quotes. Teams edit a draft rather than face a blank page.

The draft generator checks its source material first. If the transcript is too short, or
speakers still aren't matched to real people, it stops and says so instead of producing
confident nonsense from thin input. That check is the difference between a useful default and
a plausible-sounding one.

The instructions given to the AI are settings on the journey step, editable in the web UI —
so voice, format, and audience can be tuned without a developer. See
[Writing prompts](writing-prompts.md).

### It keeps people in the editorial loop

Generated copy lands in the Publishing panel on the conversation. Staff read it, edit any
field, regenerate it after the transcript or the prompts improve, and mark it ready. IRIS
accelerates editorial work; it does not decide whether the story is accurate or worth telling.

### It produces the visual assets

Thumbnails, LinkedIn headers, and quote cards are rendered from templates rather than
generated freehand — so they are consistent, repeatable, and recognisably yours. Each journey
picks its template pack.

### It hosts the video for review

The recording is uploaded to YouTube as an **unlisted** video: reachable by link, not public,
not searchable. Reviewers approve the actual video with its actual title and thumbnail, rather
than a promise about one. Making it public is a separate step that happens later, after
consent.

### It asks the participants

Everyone who took part gets a personal review link and a stated publish-by date. They see the
video, the title, the thumbnail, the quotes, and the LinkedIn post — and they can edit the
LinkedIn copy so the words attached to their name are words they'd choose.

Three outcomes, all explicit:

- **Everyone confirms early** → publishing goes ahead immediately.
- **Nobody objects by the date** → publishing goes ahead on the date. Which is precisely why
  the date is stated up front, in every message.
- **Anyone opts out** → publishing stops, and stays stopped until it's resolved with them.
  No deadline overrides an opt-out.

The participant's side of this is [its own guide](participant-review.md), written to be
forwarded.

### It carries the publishing work through

Once the gate clears: the video goes public, LinkedIn posts are published, the recording is
archived to cloud storage, the podcast episode is created, and everyone who took part gets the
public links. Each of these is a step with its own state and its own note on the conversation.

---

## Why this matters

**The slow part of publishing is the handoffs, not the tasks.** Recording, transcript, copy,
images, video, approvals, and links all sitting on one record — with the next action visible —
removes most of the waiting-on-someone that makes publishing take weeks.

**Consistency comes from configuration, not discipline.** Prompts, templates, channels, and
notification copy are settings on a journey. Every conversation on that journey gets the same
treatment without anyone remembering to apply it.

**The checkpoints are deliberate.** Quality gates before generation, human review before
anything downstream, unlisted hosting before promotion, participant consent before
distribution, and a visible note whenever something needs attention. Automation that a team
trusts is automation that stops when it should.

**Nothing disappears into a background queue.** Every stage writes its outcome back to the
conversation — successes, failures, retries, manual re-runs. If something stopped, the
conversation says where and why.

**It's part of the existing workflow.** IRIS runs on Coherence conversations, journeys, notes,
and the notification paths already in use. There is no separate publishing app to learn.

## Who it's for

- **Hosts and facilitators** get their conversations shared without personally coordinating
  production.
- **Participants** get to see and shape how they're represented before it's public.
- **Editorial and operations teams** get a production trail: what was generated, what was
  edited, what's waiting, what failed, what's ready.
- **The organisation** stops leaving good conversations trapped as raw recordings.

## Where IRIS is heading

Current direction, same principle — take value already present in a conversation, turn it
into useful artefacts, keep the human review points clear:

1. publishing transcripts into the collective-intelligence memory for the event;
2. tailored posts for additional social channels;
3. short-form video clips via specialist services.

## What IRIS is not

It does not replace taste, consent, or editorial responsibility. It does not decide what is
worth publishing, and it never posts from a participant's own account. It removes the
repetitive production friction between a good conversation and a public story — and keeps the
review points that make that story accurate and fair.
