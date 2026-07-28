# The pipeline steps

One reference page per IRIS step: what it does, what it needs before it can run, what it
produces, and what to do when it goes wrong.

New to IRIS? Read [How IRIS works](../how-iris-works.md) first — it explains what a step *is*
and why one might sit there doing nothing. This page assumes it.

A journey uses a **subset** of these steps, in this order. Nothing here is compulsory except
the first: a journey that stops after generating a transcript and a summary is a perfectly
good journey.

---

## The steps, in order

### 1. Capture — get the material

| Step | What it does | Notes |
|---|---|---|
| [Recording Downloader](realtimekit-downloader.md) | Fetches the meeting recording and stores it | Always first. Everything else builds on it. |
| [Transcript Importer](transcript-importer.md) | Imports the meeting provider's transcript | **Pick one** transcription source |
| [Google Transcribe](google-transcribe.md) | Transcribes the audio instead, with speaker separation | **Pick one** transcription source |
| [Video Editor](video-editor.md) | Trims the recording into a clean cut and records the time-shift | Optional. Runs on its own branch. |

### 2. Create — write and render

| Step | What it does | Notes |
|---|---|---|
| [Content Generator](content-generator.md) | Writes title, subtitle, description, LinkedIn copy and quotes from the transcript | Needs a transcript with resolved speakers. See [Writing prompts](../writing-prompts.md). |
| [Cover Image Generator](cover-image-generator.md) | Renders thumbnail, LinkedIn header and quote cards | Optional |

### 3. Host — put the video somewhere reviewable

Three separate steps so metadata or a thumbnail can be re-pushed without re-uploading the
video. All three share one page: [YouTube publishing](youtube-uploader.md).

| Step | What it does | Notes |
|---|---|---|
| [YouTube Video Upload](youtube-uploader.md) | Uploads the recording as **unlisted** | The expensive one. Prefers the cleaned cut if the video editor ran. |
| [YouTube Metadata Sync](youtube-uploader.md) | Pushes the current title and description | Cheap, re-runnable |
| [YouTube Thumbnail Sync](youtube-uploader.md) | Pushes the generated thumbnail | Cheap, re-runnable |

One-time channel setup: [YouTube setup](../youtube-setup.md).

### 4. Consent — ask the people in it

| Step | What it does | Notes |
|---|---|---|
| [Publish Notifier](publish-notifier.md) | Sends each participant the unlisted video, their review/opt-out link, and the publish-by date | Blocks if anyone can't be reached |
| Publish Waiter | Holds the pipeline until everyone confirms or the date passes; an opt-out stops it | Described on the [Publish Notifier](publish-notifier.md) page — the step that starts its clock |
| [Approval Waiter](approval-waiter.md) | Older consent gate: waits for explicit per-person approval | **Legacy** — use Publish Notifier + Publish Waiter instead |

A journey that isn't gating publication on consent can omit all three — but then nothing asks
the participants anything, which is rarely what you want.

### 5. Publish — make it public

| Step | What it does | Notes |
|---|---|---|
| [YouTube Visibility Promote](youtube-uploader.md) | Flips the video from unlisted to public | Only after the consent gate clears |
| [LinkedIn Page Publisher](linkedin-publisher.md) | Publishes the post as an organisation Page | Optional; either, both, or neither |
| [LinkedIn Member Publisher](linkedin-member-publisher.md) | Publishes the post as one configured person | Optional; at most one per journey |

### 6. Follow through — archive, distribute, announce

| Step | What it does | Notes |
|---|---|---|
| [Cloud Storage Migrator](cloud-storage-migrator.md) | Moves the recording to cloud object storage and frees the local disk | Optional; any time after the upload |
| [Podcast Uploader](podcast-uploader.md) | Publishes the episode audio to the podcast host | Optional |
| [Publish Live Notifier](publish-live-notifier.md) | Tells participants it's live, with the public links | Optional |
| [Telegram Distributor](telegram-distributor.md) | Creates the note that gets delivered to Telegram | Optional |

---

## How the steps connect

Each step declares what it reads and what it produces, so the order above isn't arbitrary —
it's what those declarations imply.

```
Recording Downloader
├─ transcript / publishing branch
│    Transcript Importer  (or  Google Transcribe)
│      → Content Generator
│          → Cover Image Generator
│          → YouTube Video Upload  (→ Metadata Sync, Thumbnail Sync)
│              → Cloud Storage Migrator → Podcast Uploader
│              → Publish Notifier → Publish Waiter
│                  → YouTube Visibility Promote
│                  → LinkedIn Page / Member Publisher
│                      → Publish Live Notifier → Telegram Distributor
└─ video branch
     Video Editor   (a cleaned cut the uploader prefers over the raw recording)
```

**Nothing enforces this order at run time.** The dependencies tell you how to arrange a
journey's steps; they don't stop you arranging them wrongly. A step placed before the step
that feeds it doesn't error — it waits, indefinitely, which looks like nothing happening. If a
journey stalls with no error, mis-ordering is worth checking early.

Three rules the diagram doesn't make obvious:

- **The two transcription steps are alternatives, never both.** Each one replaces the whole
  transcript when it runs, so a journey with both would have whichever ran last silently
  discard the other's work. Pick the provider import when the provider's transcript is good;
  pick Google Transcribe when the recording is good but the provider's transcript isn't.
- **Publish Notifier needs Publish Waiter in the same journey.** The notifier announces a
  publish-by date; the waiter is what actually honours it. Announcing a date nothing enforces
  is worse than not announcing one, so the journey editor treats a notifier without a waiter
  as a misconfiguration.
- **The Video Editor is a branch, not a link in the chain.** It sits after the downloader and
  before the upload; the uploader prefers its cleaned cut when there is one.

The canonical starting point is the *IRIS Standard Journey* template — clone it rather than
wiring a journey up from scratch.

## How to read a step page

Every page follows the same shape:

- **At a glance** — what it needs, what it produces, when it waits, what it costs to re-run.
- **What it does** — in plain terms.
- **How it behaves** — the details worth knowing: what makes it wait, what makes it fail,
  what happens on a re-run.
- **Settings** — what's configurable on the step, where that exists.
- **Troubleshooting** — symptom, cause, fix, for the things that actually go wrong with this
  step.
- **Technical reference** — slugs and stored field paths, for anyone configuring or
  integrating.

General troubleshooting that applies to every step — reading the rail, what reset clears,
what it can't undo — lives in [Troubleshooting](../troubleshooting.md).
