# IRIS Job Reference

One page per registered IRIS JobStep type. This index is the entry point that used to be
IRIS.md's "Existing Jobs" section; *IRIS.md* (internal engineering doc, not published here) now holds only the cross-cutting
material (architecture, concurrency model, registration, troubleshooting).

For **how to test** any of these, see the shared
*IRIS pipeline testing guide* (internal engineering doc, not published here); each page's *Testing this step*
section links back to it rather than repeating the verification pattern.

The 13 jobs form a soft dependency chain off `realtimekit_downloader`, which branches two
ways: a **transcript/publishing branch** and a **video/clips branch**. `depends_on` is
declarative only — nothing enforces it at runtime; it tells you how to order Journey steps.

| # | Job | Slug | Depends on | Purpose |
|---|-----|------|-----------|---------|
| 1 | [Recording Downloader](realtimekit-downloader.md) | `realtimekit_downloader` | *(none — first stage)* | Download the RealtimeKit recording to local storage. |
| 2 | [Transcript Importer](transcript-importer.md) | `transcript_importer` | `realtimekit_downloader` | Import the provider (Cloudflare) transcript into `TranscriptSegment` rows. |
| 3 | [Google Transcribe](google-transcribe.md) | `google_transcribe` | `realtimekit_downloader` | Transcribe the audio with Google Chirp-3 — **alternative** to Transcript Importer. |
| 4 | [Content Generator](content-generator.md) (+ [prompt guide](content-generator-prompts.md)) | `content_generator` | *(none declared; needs transcript)* | Generate title, subtitle, description, LinkedIn posts, quotes via one Gemini call. |
| 5 | [Cover Image Generator](cover-image-generator.md) | `cover_image_generator` | `content_generator` | Render thumbnail / LinkedIn header / quote cards via Playwright. |
| 6 | [Video Editor](video-editor.md) | `video_editor` | `realtimekit_downloader` | Trim the raw recording into the cleaned long-form + edit map. |
| 7 | [YouTube Uploader](youtube-uploader.md) (+ [setup guide](youtube-uploader-setup.md)) | `youtube_uploader` | `content_generator` | Upload the recording to YouTube as an unlisted video. |
| 8 | [Approval Waiter](approval-waiter.md) | `approval_waiter` | `youtube_uploader` | Wait until all required participant approvals are in. |
| 9 | [Clip Generator](clip-generator.md) | `clip_generator` | `video_editor` | Plan short vertical clips from the best moments (rendering not built). |
| 10 | [Cloud Storage Migrator](cloud-storage-migrator.md) | `cloud_storage_migrator` | `youtube_uploader` | Move the local recording to cloud object storage, delete local. |
| 11 | [Podcast Uploader](podcast-uploader.md) | `podcast_uploader` | `cloud_storage_migrator` | Publish the episode audio via Buzzsprout. |
| 12 | [LinkedIn Publisher](linkedin-publisher.md) | `linkedin_publisher` | `youtube_uploader`, `approval_waiter` | Queue `OutreachAction`s so the Chrome extension posts on LinkedIn. |
| 13 | [Telegram Distributor](telegram-distributor.md) | `telegram_distributor` | `youtube_uploader`, `linkedin_publisher` | Create a Note that `metis_telegram_update` delivers to Telegram. |

## The two branches

```
realtimekit_downloader
├─ transcript/publishing branch
│    transcript_importer  (or  google_transcribe)
│      → content_generator
│          → cover_image_generator
│          → youtube_uploader
│              → approval_waiter
│              → cloud_storage_migrator → podcast_uploader
│              → linkedin_publisher → telegram_distributor
└─ video/clips branch
     video_editor → clip_generator   (clip rendering not built yet — dead end for now)
```

`transcript_importer` and `google_transcribe` are mutually exclusive — a journey uses
exactly one (both do a delete-then-insert of `TranscriptSegment` rows). See
[google-transcribe.md](google-transcribe.md) for the choice.
