# YouTube Uploader — Configuration & Setup

The `youtube-uploader` IrisJob uploads conversation recordings to YouTube via the YouTube Data API v3.
It runs inside django-q (`qcluster`), never during the HTTP request cycle.

**Constraint:** YouTube does not support service accounts for channel uploads. Only OAuth 2.0
credentials authorised by a real channel owner work. Service account keys are explicitly rejected.

Credentials are stored **per journey step**, not per agent. Each `youtube-uploader` step connects
independently to its own YouTube channel, so different journeys can post to different channels.

---

## GCP one-time setup

Do this once when setting up a new OAuth client. One client can be reused across all journey steps
and channels — you do not need a separate GCP project per channel.

### Step 1 — Create or select a GCP project

**Console:** https://console.cloud.google.com/projectselector2/home

- Click **Select a project** at the top → **New Project** (or pick an existing one)
- Give it a name (e.g. `the-gathering`) and note the **Project ID**

**CLI:**
```bash
# Authenticate
gcloud auth login

# Create a new project (skip if reusing an existing one)
gcloud projects create YOUR_PROJECT_ID --name="The Gathering"

# Set it as the active project
gcloud config set project YOUR_PROJECT_ID

# Verify
gcloud config get-value project
```

---

### Step 2 — Enable the YouTube Data API v3

**Console:** https://console.cloud.google.com/apis/library/youtube.googleapis.com

- Click **Enable**

**CLI:**
```bash
gcloud services enable youtube.googleapis.com

# Verify
gcloud services list --enabled --filter="name:youtube.googleapis.com"
```

---

### Step 3 — Configure the OAuth consent screen

**Console:** https://console.cloud.google.com/apis/credentials/consent

This screen is shown to the YouTube channel owner when they click Connect YouTube.

1. **User type:** External → click **Create**
2. Fill in the required fields:
   - **App name:** e.g. `The Gathering`
   - **User support email:** your email
   - **Developer contact email:** your email
3. Click **Save and Continue**
4. On the **Scopes** screen, click **Add or Remove Scopes** and add:
   - `https://www.googleapis.com/auth/youtube.upload`
   - `https://www.googleapis.com/auth/youtube`
5. Click **Update** → **Save and Continue** → **Save and Continue**
6. Back on the consent screen overview, click **Publish App** and confirm
   - **This is critical.** Apps in Testing status issue tokens that expire after 7 days.
     Production tokens do not expire unless the user revokes access.

> The consent screen configuration has no CLI equivalent — it must be done in the console.

---

### Step 4 — Create the OAuth 2.0 client

**Console:** https://console.cloud.google.com/apis/credentials

1. Click **+ Create Credentials → OAuth 2.0 Client ID**
2. **Application type:** Web application
3. **Name:** e.g. `The Gathering YouTube`
4. Under **Authorised redirect URIs**, click **+ Add URI** and enter:
   ```
   https://<your-domain>/app/coherence/journey-step/youtube-auth/callback/
   ```
   For example: `https://dev.the-gathering.earth/app/coherence/journey-step/youtube-auth/callback/`

   The path must match exactly (including the `/app/` prefix and trailing slash) or Google
   will reject the consent flow with `redirect_uri_mismatch`. If you use the Connect button
   from more than one domain (e.g. dev and production), add one redirect URI per domain.
5. Click **Create**
6. Copy the **Client ID** and **Client Secret** from the dialog — you will enter these into each
   journey step that uploads to YouTube

> OAuth client creation also has no CLI equivalent — it must be done in the console.

---

### Step 5 — Verify the setup (CLI)

```bash
# Confirm the API is enabled
gcloud services list --enabled --filter="name:youtube.googleapis.com"

# Confirm you are on the right project
gcloud config get-value project
```

---

## Agent config (app credentials)

The GCP OAuth client ID and secret are shared across all steps. Set them once on the agent:

In Django Admin, open the agent that owns these journeys and add to `config`:

```json
{
  "youtube": {
    "client_id": "YOUR_OAUTH_CLIENT_ID",
    "client_secret": "YOUR_OAUTH_CLIENT_SECRET"
  }
}
```

These are the GCP application credentials, not channel-specific. Every `youtube-uploader` step
on this agent uses the same client to initiate OAuth, but each step connects to its own channel.

**Put the credentials on exactly one agent — the one whose schedule runs the uploader jobs.**
Two things read this config and must agree:

- The upload job reads `client_id`/`client_secret` from **its own** agent (the one named by
  `agent_slug` in the job schedule).
- The **Connect YouTube** button searches all agents and uses the **first** one that has both
  `client_id` and `client_secret` set.

If a second agent carries a different YouTube client, the token minted by the Connect button
may belong to a different OAuth client than the one the job uses, and every upload will fail
with `invalid_grant`.

---

## Per-step authorisation

Each `youtube-uploader` journey step holds its own `refresh_token`, binding it to one YouTube
channel. Configure at `/app/coherence/conversation-journey/<journey-pk>/`:

1. Click the step → **configure IRIS step type** → select **YouTube Uploader**
2. Set visibility, category, and other upload options
3. Click **Save**
4. Click **Connect YouTube** — a Google consent screen opens
5. Log in as the YouTube channel owner for this journey and grant access
6. You are redirected back to the journey page with a confirmation message
   ("YouTube connected for step '…' — refresh token saved")

The `refresh_token` is saved automatically to the step config and preserved across future saves.
Once connected, the button changes to **Reconnect** — clicking it replaces the stored token.

Notes on the consent flow:

- You must be logged in to METIS to use the button, and the flow must complete within
  **10 minutes** of clicking it (the state token expires after that — just click again).
- The flow always forces a fresh consent screen (`prompt=consent`), so Google issues a new
  refresh token every time — safe to repeat.
- If Google reports "did not return a refresh_token", the channel owner's Google account has
  a stale prior authorisation: revoke the app at https://myaccount.google.com/permissions and
  click **Connect YouTube** again.

### Step config fields

| Field | Required | Default | Notes |
|-------|----------|---------|-------|
| `youtube_refresh_token` | auto | — | Written by Connect flow — do not edit manually |
| `iris_job` | yes | — | Must be `youtube_uploader` |
| `visibility` | no | `unlisted` | `unlisted` or `private` (`public` is set in the approval step) |
| `category_id` | no | `22` | YouTube category ID — 22 = People & Blogs |
| `set_thumbnail_if_available` | no | `true` | Sync cover image as YouTube thumbnail after upload |
| `processing_timeout_minutes` | no | `30` | Minutes before raising RetryLater on processing poll |

The `iris_job` value binds the step to this uploader and **must be exactly `youtube_uploader`**
(underscore). The step's own name/slug is free-form and has no effect on matching.

---

## Token lifetime

The refresh token is permanent as long as:
- The GCP app remains in **Production** mode (not Testing)
- The channel owner does not revoke access at https://myaccount.google.com/permissions
- The channel owner does not change their Google password

---

## Re-authorising (token expired or revoked)

If the job fails with a note like:

```
IRIS error (<step-slug>): YouTube OAuth token has expired or been revoked.
To fix: open /app/coherence/conversation-journey/<pk>/ → find step '<step-slug>' → click 'Connect YouTube'.
```

Go to the journey step, click **Connect YouTube**, and complete the consent flow again. The new
token overwrites the old one; no other config changes are needed.

---

## Prerequisites (runtime)

The job checks these before uploading. Missing data raises `RetryLater` and the scheduler retries
on the next run:

- `infos["publishing"]["title"]` must be set (populated by the content-generator step)
- `infos["publishing"]["youtube"]["description"]` must be set
- A recording file must exist on disk. The job prefers the video-editor's cleaned cut
  (`config["iris.downloads"]["edited_recording"]`) when that file exists, and falls back to
  the raw `config["iris.downloads"]["recording"]` otherwise (e.g. journeys without a
  video-editor step).

At upload time, the title is truncated to YouTube's 100-character limit and the description
to its 5000-character limit.

---

## Errors, retries, and quota

The job distinguishes transient conditions (retried automatically) from permanent failures
(pipeline halts with an error note on the conversation):

| Condition | Behaviour |
|-----------|-----------|
| Title/description/recording not ready | Retried on the next scheduled run |
| YouTube 500/503 or network error | Up to 3 attempts with backoff, then retried next run |
| Daily API quota exceeded (403 `quotaExceeded`) | Retried — completes when quota resets (midnight Pacific) |
| Processing not finished within `processing_timeout_minutes` | Retried — the video is already uploaded; the next run only re-polls |
| Refresh token expired or revoked (`invalid_grant`) | Permanent — see Re-authorising below |
| Other 4xx errors, or YouTube reports processing `failed` | Permanent — error note on the conversation |
| Thumbnail sync failure | Non-fatal — logged as a warning, upload still succeeds |

Quota: the free YouTube Data API tier is 10,000 units/day and one video upload costs
~1,600 units, so roughly 6 uploads/day per GCP project. Status polls and thumbnail sets are
comparatively cheap.

A permanent error never uploads twice: once a `video_id` is stored, every retry path re-polls
or syncs the existing video instead of re-uploading.

---

## What the job writes

All output lands in `conversation.infos["publishing"]["youtube"]`:

| Key | Set when |
|-----|----------|
| `video_id` | After successful upload |
| `video_url` | After successful upload |
| `visibility` | After successful upload |
| `upload_status` | After upload (`uploaded`) and after processing (`processed` / `failed`) |
| `processing_status` | After processing poll |
| `uploaded_at` | After upload |
| `processed_at` | After processing completes |
| `thumbnail_synced_at` | After thumbnail sync (if enabled) |

---

## Manual staff actions (UI)

On the conversation detail page (`/coherence/conversation/<id>/`), the **Hosted Video** section has:

- **Retry Upload** — re-triggers the upload if it failed completely (e.g. quota exceeded)
- **Sync Status** — re-polls YouTube processing state without re-uploading; use this if the job
  uploaded successfully but timed out waiting for processing to complete

---

## Related files

- Job: `metis_apps/coherence/iris_youtube.py`
- Config schema: `metis_apps/coherence/iris_models.py` (`YouTubeUploaderConfig`)
- Step config template: `metis_apps/coherence/templates/coherence/partials/iris_config_youtube_uploader.html`
- OAuth views: `metis_apps/coherence/views.py` (`journey_step_youtube_auth_start`, `journey_step_youtube_auth_callback`)
- UI template: `metis_apps/coherence/templates/coherence/partials/hosted_video_panel.html`
- Retry/sync views: `metis_apps/coherence/views.py` (`conversation_youtube_sync`, `conversation_youtube_retry`)
