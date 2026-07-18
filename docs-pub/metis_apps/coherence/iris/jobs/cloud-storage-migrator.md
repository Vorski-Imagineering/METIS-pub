# Cloud Storage Migrator

| | |
|---|---|
| **Label** | Cloud Storage Migrator |
| **Slug** | `cloud_storage_migrator` |
| **File** | `metis_apps/coherence/iris_cloud_storage.py` |
| **Class** | `CloudStorageMigrator` |
| **Depends on** | `youtube_uploader` |

## Purpose

Moves the local recording to cloud object storage (R2 / S3 / GCS S3-compatible) after the
YouTube upload succeeds, then deletes the local copy.

## Pipeline position

- **Upstream (`depends_on`):** `youtube_uploader`.
- **Feeds into:** `podcast_uploader` (prefers the cloud copy).
- **Alternative to:** none.

## Data flow

**Reads**
- `infos["publishing"]["youtube"]["video_id"]` — gate: won't touch the local file until
  YouTube has a confirmed copy.
- `config["iris.downloads"]["recording"]`.

**Writes**
- `config["iris.downloads"]["amazon_s3_url"]`, `["amazon_s3_key"]`, `["cloud_migrated_at"]`.

## Requirements

- **Agent.config:** `cloud_storage.provider` (`r2`|`s3`|`gcs`), `cloud_storage.bucket`,
  `cloud_storage.access_key_id`, `cloud_storage.secret_access_key`, `cloud_storage.endpoint`
  (required for R2/GCS, omit for native AWS S3).
- **System:** none.
- **External credentials:** the cloud provider (above).

## Behavior details

- **Idempotency:** if `amazon_s3_url` is already set, verifies the remote object still exists
  before treating it as done; re-uploads if the bucket was cleared.
- **Verification:** compares ETag to local MD5 for single-part uploads; falls back to size
  comparison for multipart (>5GB).
- **Deletes local file by default** (`delete_local_after_upload=True`) — but only after the
  YouTube gate and a verified remote copy.
- **Done vs error:** "done" once the object is verified in the bucket (and local deleted);
  permanent error on a bad cloud config or upload failure.

## Step slug convention

`"cloud_storage_migrator"` (matches `config["iris_job"] = "cloud_storage_migrator"`).

## Testing this step

No automated test today. Manual scenario (staging): with valid `cloud_storage.*` and a
YouTube `video_id` present, run → object appears in the bucket, ETag/size verified,
`amazon_s3_url`/`amazon_s3_key` written, local file removed. Re-run with the object present →
verified-idempotent; clear the bucket and re-run → re-uploads. See the
*testing guide* (internal engineering doc, not published here).

## Related runbooks

- *manual-retrigger* (internal engineering doc, not published here)
- *cleanup-image-files* (internal engineering doc, not published here) — orphaned local artifacts.
