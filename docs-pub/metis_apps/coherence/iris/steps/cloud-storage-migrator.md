# Cloud Storage Migrator

Moves the recording off the application server into cloud object storage, then deletes the
local copy to free disk space.

## At a glance

| | |
|---|---|
| **Needs** | A confirmed YouTube upload, and the recording still on local disk |
| **Produces** | The recording in the cloud bucket, and its location on the conversation |
| **Waits when** | The YouTube upload hasn't confirmed yet |
| **Re-running** | Safe — verifies the object is really there before treating it as done |

## What it does

Uploads the recording to object storage (Cloudflare R2, Amazon S3, or a Google Cloud bucket
speaking the S3 protocol), verifies it arrived intact, and then deletes the local file.

**It won't touch the local file until YouTube has a confirmed copy.** That ordering is the
whole safety story: deleting the only usable copy of a recording because an upload half
succeeded is the failure this step is designed never to have.

Verification compares a checksum for normal files, falling back to a size comparison for very
large multi-part uploads.

Once migrated, later steps that need the media — such as the
[Podcast Publisher](podcast-publisher.md) — use the cloud copy.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| Waiting with no error | The YouTube upload hasn't confirmed | Normal. Check the upload step. |
| Error mentioning credentials, bucket, or endpoint | Storage settings are missing or wrong on the agent | An administrator fixes them, then re-run |
| Error on upload or verification | The transfer failed or the stored copy doesn't match | Re-run; a partial object is replaced rather than trusted |
| Local disk still full after it ran | Only the recording is removed; other derived files remain | An administrator can clean up orphaned derived files |
| A later step says the recording is missing | Expected after migration | Steps that need the media read the cloud copy — check they're configured with the same storage settings |
| Re-run says nothing to do | The object is already in the bucket and verified | Expected. If the bucket was cleared, the re-run uploads again |

## Technical reference

| | |
|---|---|
| **Step type** | `cloud_storage_migrator` |
| **Runs after** | `youtube_video_upload` |
| **Feeds** | `podcast_publisher` (prefers the cloud copy) |
| **Reads** | `records.youtube.video_id` (the gate), `config["iris.downloads"]["recording"]` |
| **Writes** | `config["iris.downloads"]["amazon_s3_url"]`, `["amazon_s3_key"]`, `["cloud_migrated_at"]` |
| **Needs on the agent** | `cloud_storage.provider` (`r2`/`s3`/`gcs`), `cloud_storage.bucket`, `cloud_storage.access_key_id`, `cloud_storage.secret_access_key`, `cloud_storage.endpoint` (required for R2 and GCS, omitted for native S3) |
| **Deletes the local file** | Yes, by default (`delete_local_after_upload`) — only after the YouTube gate and a verified remote copy |
