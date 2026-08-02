# Podcast Publisher

Masters the conversation recording into a publish-ready MP3 and publishes it as an episode
in the event's own podcast RSS feed.

## At a glance

| | |
|---|---|
| **Needs** | An approved title, a recording, and a complete show (set up on the event page) |
| **Produces** | A published episode: the mastered audio, an entry in the RSS feed, and a public episode page |
| **Waits when** | The title hasn't been approved yet, or the recording isn't available |
| **Re-running** | Safe — the episode keeps its identity and the audio is never re-mastered |

## What it does

There is no external podcast host. **The feed is ours**, and an episode is a published
conversation:

- **One event is one show.** The show — its title, description, artwork, category and owner
  email, all of which Apple, Spotify and YouTube read — is settings on the *event*, edited on
  the event's own page. It is not part of this step's settings.
- **One conversation is one episode.** An event holds many conversations, and they are the
  episodes; they may run through several different journeys and still land in the one show.
- **One event is one feed**, at a permanent address derived from the event's name.

This step's own settings are only *how this journey publishes* into that show — the publish
delay, whether to append the transcript, and the episode defaults. Two journeys under the
same event may answer those differently while sharing one show.

For each conversation that reaches the step, it:

1. Finds the event's show and checks it is complete enough to publish, naming any missing field.
2. Waits for an approved title.
3. Masters the recording's audio — see below.
4. Publishes the audio and records the episode.
5. Builds the show notes and publishes the episode to the feed.

### The audio is mastered, not just converted

Loudness is the single biggest difference in perceived quality between a homemade podcast and
a professional one. A conversation recorded quietly plays quiet next to every other show in
someone's queue, and the listener reaches for the volume knob.

So the audio is **loudness-normalised in two passes** — the first measures the recording, the
second encodes using those measurements — rather than simply converted to MP3. A high-pass
filter removes rumble and handling noise that is inaudible for speech but wastes bitrate. The
result is encoded at a consistent quality, and the show's title, cover art and episode name
are embedded in the file itself, so car stereos and podcast apps display them even where the
feed does not reach.

This takes a few minutes per episode. That cost is paid **once**: the mastered audio is saved
before anything else happens, so a later failure and re-run never repeats it.

### Publishing can be scheduled

**Publish delay** schedules the episode forward instead of publishing the moment the step
runs, which is how you line an episode up for a particular morning. The feed's caching is
tied to the next scheduled publication, so an episode appears on time rather than whenever a
cache happens to expire.

## How it behaves

**Episode identity never changes.** Each episode is given a permanent identifier the first
time it publishes, and nothing afterwards changes it — not editing the title, not replacing
the audio, not re-running the step. This matters more than it sounds: podcast directories key
on that identifier, so a change makes every app treat the episode as brand new and show it to
subscribers a second time.

**Published text is a snapshot.** The title and description are copied into the episode when
it publishes. Editing the publishing fields afterwards does not silently rewrite a published
episode; re-running the step is the deliberate way to refresh it.

**Re-running is safe.** An already-published conversation is recognised immediately: the step
refreshes the title and description if they changed, and returns. It does not re-master, and
it does not republish.

**Resetting the step withdraws the episode; it does not erase it.** The episode leaves the
feed and its page reports that it was withdrawn, but its identity and audio are kept. Erasing
it would orphan the copies that listeners' apps already hold, and would let a later run
publish the same episode under a new identity.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| Waiting with no error | The title hasn't been approved | Normal. Approve the content. |
| Error listing show fields | The show is incomplete | Fill in the named fields on the event's Podcast section. Waiting won't fix it — a feed can't publish without them. |
| "This event has no podcast show yet" | Nothing has set the show up | Open the event page and press *Set up the podcast*. |
| Error about the category | The category isn't one Apple recognises | Pick from the dropdown; Apple rejects a feed with an unknown category. |
| Error that the recording is missing | The recording isn't on disk or in storage | Check the recording steps ran. |
| Episode published but not visible in Apple or Spotify | Normal delay | Directories refresh on their own schedule, often hours. The canonical feed is already correct. |
| Artwork not updating in Apple | Apple only re-reads artwork when its address changes | Publish the artwork as a new version rather than replacing the existing file. |
| Episode appears twice in listeners' apps | Its identifier changed | Should be impossible; report it. Check whether the record was erased rather than withdrawn. |
| Audio plays but can't be skipped through | The media host isn't answering range requests | An administrator checks the media host configuration. |

## The show — set up on the event page

Open the event, find the **Podcast** section, and press *Set up the podcast* (or *Edit show*).
Everything below is public: it is what podcast directories read.

| Field | Notes |
|---|---|
| Show title | The show's name in every directory |
| Show description | Required |
| Cover artwork URL | Square, 1400×1400 to 3000×3000, JPEG or PNG, RGB with no transparency. *Generate artwork* renders one from the event's card pack |
| Show website | Optional; the show page is used when empty |
| Owner name | Shown as the publisher |
| **Owner email** | **Appears publicly in the feed — use an organisational address.** Spotify and YouTube both verify ownership by emailing a code to it, so neither can be connected without it |
| Author name | Defaults to the owner name |
| Language | e.g. `en`, `en-gb` |
| Category / subcategory | From Apple's published list |
| Show type | Episodic or serial |
| Explicit | Show-wide default |

The form never refuses an incomplete show — a show can be saved half-filled while you decide
what it is called. Publishing is what requires the fields to be there, and it names the ones
that are missing. **Diagnostics** on the same section checks the feed as an outside directory
sees it.

## Step config fields

Publishing behaviour for this journey. The show is not here.

| Field | Public? | Notes |
|---|---|---|
| Season | Yes | Blank uses the publication year |
| Episode type | Yes | Full, trailer or bonus |
| Publish delay (hours) | No | 0 publishes immediately |
| Append transcript to show notes | No | Truncated to the 4000-character description limit |

## Technical reference

| | |
|---|---|
| **Step type** | `podcast_publisher` |
| **Runs after** | Content generation and approval; optionally `cloud_storage_migrator` |
| **Reads** | `fields.title` (the gate), `fields.subtitle`, `fields.youtube_description` |
| **Writes** | `records.podcast` |
| **Needs on the agent** | Nothing. Storage credentials are only needed if the recording is read from cloud storage |
| **Runtime requirement** | FFmpeg |
| **Feed address** | `/podcasts/<event-slug>/feed.xml` — permanent once submitted to a directory |
| **Episode page** | `/podcasts/<event-slug>/<episode-id>/` — what publication notifications link to |

Connecting the show to Apple, Spotify, YouTube and others is a one-time manual procedure:
see the [platform connection guide](../IRIS-podcast-RSS-platform-connection-guide.md).
