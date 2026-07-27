# IRIS Job Reference

One page per registered IRIS JobStep type. This index is the entry point that used to be
IRIS.md's "Existing Jobs" section; *IRIS.md* (internal engineering doc, not published here) now holds only the cross-cutting
material (architecture, concurrency model, registration, troubleshooting).

For **how to test** any of these, see the shared
*IRIS pipeline testing guide* (internal engineering doc, not published here); each page's *Testing this step*
section links back to it rather than repeating the verification pattern.

The jobs form a soft dependency chain off `realtimekit_downloader`, which branches two
ways: a **transcript/publishing branch** and a **video/clips branch**. Dependencies are
**derived** from what each job declares it reads against what other jobs declare they
write — nothing enforces them at run time, so they tell you how to order Journey steps,
not what will happen if you don't.

Every registered job is listed. A journey uses a subset: the waiters and notifiers are
optional if you are not gating a publish on participant consent, and the two transcription
jobs are alternatives.

| # | Job | Slug | Depends on | Purpose |
|---|-----|------|-----------|---------|
| 1 | [Recording Downloader](realtimekit-downloader.md) | `realtimekit_downloader` | *(none — first stage)* | Download the RealtimeKit recording to local storage. |
| 2 | [Transcript Importer](transcript-importer.md) | `transcript_importer` | `realtimekit_downloader` | Import the provider (Cloudflare) transcript into `TranscriptSegment` rows. |
| 3 | [Google Transcribe](google-transcribe.md) | `google_transcribe` | `realtimekit_downloader` | Transcribe the audio with Google Chirp-3 — **alternative** to Transcript Importer. |
| 4 | [Video Editor](video-editor.md) | `video_editor` | `realtimekit_downloader` | Trim the raw recording into the cleaned long-form + edit map. Separate branch. |
| 5 | [Content Generator](content-generator.md) (+ [prompt guide](content-generator-prompts.md)) | `content_generator` | `transcript_importer` *or* `google_transcribe` | Generate title, subtitle, description, LinkedIn posts, quotes via one Gemini call. |
| 6 | [Cover Image Generator](cover-image-generator.md) | `cover_image_generator` | `content_generator` | Render thumbnail / LinkedIn header / quote cards. |
| 7 | [YouTube Video Upload](youtube-uploader.md) | `youtube_video_upload` | `content_generator` | Upload the recording as **unlisted**. Prefers the cleaned cut if `video_editor` ran. |
| 8 | [YouTube Metadata Sync](youtube-uploader.md) | `youtube_metadata_sync` | `youtube_video_upload` | Push the current title/description to the uploaded video. Independently re-runnable. |
| 9 | [YouTube Thumbnail Sync](youtube-uploader.md) | `youtube_thumbnail_sync` | `youtube_video_upload`, `cover_image_generator` | Push the generated thumbnail. Independently re-runnable. |
| 10 | [Cloud Storage Migrator](cloud-storage-migrator.md) | `cloud_storage_migrator` | `youtube_video_upload` | Move the local recording to cloud object storage, delete local. |
| 11 | [Podcast Uploader](podcast-uploader.md) | `podcast_uploader` | `content_generator` | Publish the episode audio via Buzzsprout. |
| 12 | [Publish Notifier](publish-notifier.md) | `publish_notifier` | `youtube_video_upload` | Send every participant the unlisted video, their review/opt-out link, and the publish-by date. |
| 13 | Publish Waiter | `publish_waiter` | `publish_notifier` | Hold the pipeline until the grace period elapses or everyone confirms early; an opt-out blocks it. Writes the single `publishing_status` gate. |
| 14 | [Approval Waiter](approval-waiter.md) | `approval_waiter` | `youtube_video_upload` | Older consent gate: waits for explicit per-participant approval. **Superseded** by Publish Notifier + Publish Waiter — see the note below. |
| 15 | [YouTube Visibility Promote](youtube-uploader.md) | `youtube_visibility_promote` | `youtube_video_upload` (and, in a journey, `publish_waiter`) | Flip the video public once publishing is cleared. |
| 16 | [LinkedIn Page Publisher](linkedin-publisher.md) | `linkedin_publisher` | `youtube_video_upload`, `publish_waiter` | Publish the approved post to a LinkedIn organization Page via the official API. |
| 17 | [LinkedIn Member Publisher](linkedin-member-publisher.md) | `linkedin_member_publisher` | `youtube_visibility_promote`, `publish_waiter` | Publish the approved post as one configured LinkedIn member. |
| 18 | [Publish Live Notifier](publish-live-notifier.md) | `publish_live_notifier` | `youtube_visibility_promote` | Announce "it's live" with the public links, including the LinkedIn reshare link. |
| 19 | [Telegram Distributor](telegram-distributor.md) | `telegram_distributor` | `youtube_video_upload`, LinkedIn publishers | Create a Note that `metis_telegram_update` delivers to Telegram. |

Not every job has a page of its own. **Publish Waiter** is described under
[Publish Notifier](publish-notifier.md), the step that starts its clock; the three
YouTube sync/promote jobs share [youtube-uploader.md](youtube-uploader.md) with the
upload step they extend.

**Approval Waiter is legacy.** It gates on a separate approval record written by the
participant-facing approval page, and predates the notify/opt-out flow that
`publish_notifier` + `publish_waiter` provide. Prefer those for new journeys.

## The two branches

```
realtimekit_downloader
├─ transcript/publishing branch
│    transcript_importer  (or  google_transcribe)
│      → content_generator
│          → cover_image_generator
│          → youtube_video_upload  (→ youtube_metadata_sync, youtube_thumbnail_sync)
│              → cloud_storage_migrator → podcast_uploader
│              → publish_notifier → publish_waiter
│                  → youtube_visibility_promote
│                  → linkedin_publisher / linkedin_member_publisher
│                      → publish_live_notifier → telegram_distributor
└─ video branch
     video_editor   (cleaned long-form + edit map; clip generation is a
                     build-vs-buy decision, not a METIS job)
```

`transcript_importer` and `google_transcribe` are mutually exclusive — a journey uses
exactly one (both do a delete-then-insert of `TranscriptSegment` rows). See
[google-transcribe.md](google-transcribe.md) for the choice.
