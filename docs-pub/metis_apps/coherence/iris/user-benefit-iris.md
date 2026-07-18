# IRIS: From Great Conversations to Published Stories

IRIS turns recorded conversations into polished, reviewable, publication-ready media.

Instead of asking a team to manually download recordings, write summaries, draft posts,
create thumbnails, upload videos, chase approvals, and prepare distribution, IRIS moves
the work through a clear publishing journey. It handles the repeatable production steps
while keeping people in control of the message before anything is shared more widely.

## The Value in One Sentence

IRIS helps your team turn a raw conversation into a finished media package: text,
visuals, hosted video, approvals, and distribution support, all tracked from inside
the conversation record.

## What IRIS Does

### Captures the Raw Recording

IRIS can collect meeting recordings from RealtimeKit and attach them to the right
conversation. The recording becomes the source material for the rest of the publishing
workflow, so the team does not have to hunt through external tools or manually pass
files around.

**User benefit:** the conversation starts becoming useful immediately after it is
recorded. The source material is connected to the people, journey, transcript, and
publishing workflow in one place.

### Generates a Complete First Draft

IRIS uses the transcript to generate the core publishing copy in one structured pass:

- a clear title
- a concise subtitle
- an internal summary
- a YouTube-style description
- LinkedIn post drafts for host and guest perspectives
- key quotes suitable for social sharing

The generation step includes transcript quality checks. If the transcript is too short
or speakers still need to be matched to real people, IRIS stops and leaves a clear
remediation note instead of producing weak or misleading content.

**User benefit:** teams start from a strong editable draft rather than a blank page,
while still avoiding the common trap of publishing content from incomplete or messy
source material.

### Keeps Humans in the Editorial Loop

Generated copy appears in the existing conversation detail page as a Publishing Draft.
Staff can review it, edit it field by field, regenerate it when prompts or transcript
quality improve, and mark it ready for the next stage.

**User benefit:** IRIS accelerates editorial work without removing judgment. People
still decide whether the story is accurate, useful, and ready.

### Makes Prompts Easy to Tune

The prompts that drive IRIS generation are configurable through the web UI. Staff can
adjust the instructions for titles, subtitles, descriptions, LinkedIn posts, summaries,
quotes, and other generated outputs without needing a developer to change code.

**User benefit:** the team can refine voice, format, audience fit, and campaign goals
as the publishing strategy evolves. IRIS can stay consistent where it should be
consistent, and adapt quickly where the message needs to change.

### Creates Branded Visual Assets

IRIS can render deterministic, on-brand visual assets from the approved conversation
content:

- YouTube thumbnail
- LinkedIn header image
- quote cards for social channels

These are generated from templates rather than freeform image generation, which keeps
the output predictable, repeatable, and easier to keep aligned with the brand.

**User benefit:** every conversation can have professional-looking promotional assets
without needing a custom design pass for each episode.

### Hosts the Video for Review

IRIS can upload the conversation recording to YouTube as an unlisted video and track
the upload and processing state. If a video already exists, retry flows sync the current
metadata instead of creating duplicates.

**User benefit:** reviewers can approve the real hosted video, not a local placeholder
or a file someone has to download. The team also gets a stable shareable asset before
broader publication.

### Collects Participant Approval

IRIS supports participant-specific approval links. Participants can review the hosted
video, title, subtitle, thumbnail, quotes, and their own LinkedIn draft. They can edit
their LinkedIn copy before approving.

Approval state is tracked per person, and the pipeline can wait until the required
approvals have been received before advancing.

**User benefit:** participants are not surprised by how they are represented. Consent
and final review become part of the publishing process rather than an informal side
conversation.

### Supports Post-Approval Publishing Work

After approval, IRIS has pipeline stages for the practical work that usually follows:

- moving local recordings into cloud object storage
- preparing podcast publication through Buzzsprout
- queuing LinkedIn publishing actions for participants
- creating Telegram-ready distribution notes through the existing notification flow

**User benefit:** once content is approved, the system can carry the operational work
forward without forcing the team to rebuild the same checklist for every conversation.

## Why This Matters

### Faster Turnaround

The slowest part of publishing is often not one big task; it is the chain of small
handoffs. IRIS reduces those handoffs by keeping the recording, transcript, generated
copy, visual assets, hosted video, approval state, and publication metadata together.

### More Consistent Output

IRIS uses journey-step configuration for prompts, model settings, templates, and
publishing behavior. That means each conversation can follow a repeatable production
standard while still allowing staff to tune the voice and format for a specific journey.
Because those prompts are exposed through the web UI, editorial teams can improve
generation results directly instead of waiting on code changes.

### Safer Publishing

IRIS is designed around checkpoints:

- transcript quality gates before generation
- internal review before downstream steps
- unlisted hosting before public promotion
- participant approval before wider distribution
- visible notes when something fails or needs attention

The result is automation that helps the team move quickly without making publishing
feel reckless.

### Less Operational Guesswork

Every IRIS stage writes status back to the conversation. Successes, failures, retries,
and manual retriggers are visible in the activity timeline. If a step cannot continue,
the conversation stays in place with a clear note instead of silently disappearing into
a background queue.

### Built for the Existing Workflow

IRIS is not a separate publishing app bolted onto the side. It works through
conversation journeys, conversation detail panels, existing notes, agent configuration,
and established outreach and notification paths.

**User benefit:** teams can adopt IRIS without learning an entirely separate system.

## Who IRIS Helps

### For Hosts and Facilitators

IRIS makes conversations easier to share. Hosts get a draft title, description,
summary, social copy, quotes, and visual assets without having to coordinate every
production detail manually.

### For Participants

Participants get a review surface that shows what will be published and how they will
be represented. Their LinkedIn draft can be edited before approval.

### For Editorial and Operations Teams

IRIS gives the team a reliable production trail: what was generated, what was edited,
what is waiting, what failed, and what is ready. It reduces manual follow-up and makes
the next action visible.

### For the Organisation

Good conversations stop getting trapped as raw recordings. IRIS helps turn them into
reusable, discoverable, shareable assets that can support community building,
education, marketing, and long-term knowledge capture.

## A Practical Publishing Journey

With IRIS, a conversation can move from recording to publishing package like this:

1. Record the conversation.
2. Download and attach the recording.
3. Generate the first publishing draft from the transcript.
4. Review, edit, and mark the draft ready.
5. Generate branded visual assets.
6. Upload the video as an unlisted hosted asset.
7. Send participant approval links.
8. Wait for approvals.
9. Continue with cloud archiving, podcast preparation, LinkedIn actions, and Telegram distribution.

The important point is not just that these steps can be automated. It is that each step
is visible, recoverable, and connected to the conversation it came from.

## Next Steps for IRIS

IRIS is already positioned to support a broader publishing loop around Coherence
conversations. The next product steps are:

1. Publish the transcript to the collective-intelligence memory for the Coherence Conversations event.
2. Create tailored posts for social media channels.
3. Create video shorts using external specialist services.

These additions extend the same principle as the current workflow: take the value
already present in a conversation, turn it into useful public and internal artefacts,
and keep the human review points clear.

The same configurable-prompt approach should apply here too. As these new generation
steps are added, teams should be able to tune the prompt instructions through the web
UI, so transcript publishing, social copy, and video-short briefs can all match the
voice and goals of the event.

## The IRIS Promise

IRIS does not replace taste, consent, or editorial responsibility.

It replaces repetitive production friction.

It gives teams a faster path from meaningful conversations to useful public stories,
while preserving the review points that keep those stories accurate, respectful, and
ready to share.
