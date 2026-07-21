# YouTube Publishing — Configuration & Setup

YouTube publishing is three IrisJobs — `youtube_video_upload`, `youtube_metadata_sync`, and
`youtube_thumbnail_sync` — that push conversation recordings and metadata to YouTube via the
YouTube Data API v3. They run inside django-q (`qcluster`), never during the HTTP request cycle.
For what each step does, see [youtube-uploader.md](youtube-uploader.md); this page covers the
one-time GCP setup and per-journey channel connection they share.

**Constraint:** YouTube does not support service accounts for channel uploads. Only OAuth 2.0
credentials authorised by a real channel owner work. Service account keys are explicitly rejected.

The channel is connected **once per journey**, on the `youtube_video_upload` step. The
metadata-sync and thumbnail-sync steps inherit that step's token automatically, so all three
always publish to the same channel. Different journeys can connect different channels.

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
6. Copy the **Client ID** and **Client Secret** from the dialog — you will put these on the agent
   (see below), not on individual journey steps

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

These are the GCP application credentials, not channel-specific. Every YouTube step on this agent
uses the same client to initiate OAuth; the per-journey channel token is stored separately (see
Per-step authorisation below).

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

Only the **video upload** step holds a `refresh_token`, binding the journey to one YouTube
channel — the metadata-sync and thumbnail-sync steps always inherit it and have no Connect
button of their own (connecting a separate channel there would try to sync a video that only
exists on the upload step's channel, and fail). Configure at
`/app/coherence/conversation-journey/<journey-pk>/`:

1. On the `youtube_video_upload` step, click → **configure IRIS step type** → select **YouTube
   Video Upload**
2. Set visibility, category, and other upload options
3. Click **Save**
4. Click **Connect YouTube** — a Google consent screen opens (only this step has the button; the
   sync steps show the inherited channel read-only)
5. Log in as the YouTube channel owner for this journey and grant access
6. You are redirected back to the journey page with a confirmation message naming the connected
   channel ("YouTube connected for step '…' — channel "…"")

The `refresh_token` is saved automatically to the step config and preserved across future saves.
Once connected, the button changes to **Reconnect** — clicking it replaces the stored token.

Notes on the consent flow:

- You must be logged in to METIS to use the button, and the flow must complete within
  **10 minutes** of clicking it (the state token expires after that — just click again).
- The flow always forces a fresh consent screen and account/channel picker
  (`prompt=consent select_account`), so Google issues a new refresh token every time — safe to
  repeat.
- If Google reports "did not return a refresh_token", the channel owner's Google account has
  a stale prior authorisation: revoke the app at https://myaccount.google.com/permissions and
  click **Connect YouTube** again.

---

## Which Google account to connect with — personal vs Brand Account channels

This is the step that most often goes wrong, because YouTube has **two different kinds of
channel** and a permission model that behaves differently for the API than it does for the
Studio website.

The rule that governs everything below:

> **Only an _Owner_ of a channel can authorise API access to it.** People given YouTube Studio
> "channel permissions" of Manager, Editor, etc. can upload and edit on the YouTube website, but
> **their access is invisible to OAuth and the YouTube Data API** — which is exactly what IRIS
> uses. Being able to upload a video by hand in YouTube Studio does **not** mean you can connect
> that channel here.

### Case A — Personal channel (not a Brand Account)

The channel is tied 1:1 to a single Google login (e.g. a channel called "Victor Vorski" on
Victor's own Google account). This is the simple case:

1. Sign in to that Google account during the Connect flow.
2. If that account has only the one channel, Google connects it directly — no picker appears
   because there is nothing to choose between. **This is normal**, not a bug.
3. Confirm the channel name shown next to **Connected** afterward.

### Case B — Brand Account / organisation channel

A Brand Account is an organisation-shaped identity that **owns** a channel but is not itself a
login — there is no email/password for "The Coherence Company". Ordinary Google accounts are
granted roles on it. A channel like this exists even though no one logs in _as_ the channel.

To connect a Brand Account channel:

1. The person doing the Connect must be signed in to a Google account that is an **Owner** of the
   channel — not merely a Studio-invited Manager/Editor (see the rule above).
2. During consent the `select_account` picker appears. **Choose the Brand Account channel, not
   the personal one** — a Google account that owns a Brand Account will see both listed.
3. Confirm the channel name shown next to **Connected** afterward. If it shows the personal
   channel instead of the org channel, the wrong entry was picked (or the account lacks Owner
   access) — click **Reconnect** and try again.

**If the Brand Account channel does not appear in the picker, or connecting "succeeds" but lands
on the personal channel:** the signed-in account almost certainly has only Studio-level
(Manager/Editor) access, which the API cannot see. Grant it real **Owner** access first, using
whichever of these applies to the channel:

- **Channel still on a legacy Brand Account** — an existing owner adds the account as an owner at
  [myaccount.google.com/brandaccounts](https://myaccount.google.com/brandaccounts) → the Brand
  Account → **Manage permissions**.
- **Channel migrated to YouTube Studio Channel Permissions** — an existing owner assigns the
  **Owner** role at **YouTube Studio → Settings → Permissions**. (Google has been migrating
  channels off Brand-Account roles onto this system since 2024; newer channels only have this
  path.)

Then run **Connect YouTube** again. Owner access can take a short while to propagate; if the
channel still isn't offered immediately, wait a few minutes and retry.

> **Why it's this confusing:** three separate systems that grew up in different eras all pretend
> to be one — the underlying **ownership** of the channel/Brand Account, **YouTube Studio access**
> (the Manager/Editor invitations), and the **OAuth/API identity** Google resolves for a
> connecting app. Studio permissions were layered on later and the older API identity model does
> not honour them, which is why someone can upload by hand yet be unable to connect the same
> channel to IRIS. The only permission that satisfies the API is genuine **Owner** access.

Whichever case applies, the channel name displayed next to **Connected** (in the step editor and
on the conversation step inspector) is the source of truth for what IRIS will actually upload to —
always check it after connecting.

### Step config fields (`youtube_video_upload`)

| Field | Required | Default | Notes |
|-------|----------|---------|-------|
| `iris_job` | yes | — | Must be `youtube_video_upload` |
| `youtube_refresh_token` | auto | — | Written by Connect flow — do not edit manually |
| `youtube_channel_id` / `youtube_channel_title` / `youtube_channel_avatar_url` | auto | — | Resolved and stored by the Connect flow; drive the connected-channel display |
| `visibility` | no | `unlisted` | `unlisted` or `private` (`public` is set in the approval step) |
| `category_id` | no | `22` | YouTube category ID — 22 = People & Blogs |
| `processing_timeout_minutes` | no | `30` | Minutes before raising RetryLater on processing poll |

The `iris_job` value binds the step to this job and **must be exactly `youtube_video_upload`**
(underscore). The step's own name/slug is free-form and has no effect on matching.

The metadata-sync step also takes a `category_id` (resent on every metadata update — YouTube
requires it in the snippet); the thumbnail-sync step takes no options. Neither holds its own
channel token. See [youtube-uploader.md](youtube-uploader.md) for those two steps.

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

The upload step checks these before uploading. Missing data raises `RetryLater` and the scheduler
retries on the next run:

- `fields.title` must be set (populated by the content-generator step)
- `fields.youtube_description` must be set
- A recording file must exist on disk. The job prefers the video-editor's cleaned cut
  (`config["iris.downloads"]["edited_recording"]`) when that file exists, and falls back to
  the raw `config["iris.downloads"]["recording"]` otherwise (e.g. journeys without a
  video-editor step).

At upload time, the title is truncated to YouTube's 100-character limit and the description
to its 5000-character limit.

---

## Errors, retries, and quota

The full transient-vs-permanent error classification (and what each of the three steps reads and
owns) lives in [youtube-uploader.md](youtube-uploader.md); it is not repeated here. Two
setup-relevant facts:

- **Re-auth is the one you configure for:** a refresh token that has expired or been revoked
  (`invalid_grant`) is a **permanent** failure — the fix is to reconnect (see Re-authorising
  below). Almost everything else (missing inputs, 500/503, network errors, quota exhaustion,
  processing not finished) is retried automatically on the next scheduled run.
- **Uploads never duplicate:** once a `video_id` is stored, every retry path re-polls or syncs the
  existing video instead of re-uploading.

**Quota:** the free YouTube Data API tier is 10,000 units/day and one video upload costs
~1,600 units, so roughly 6 uploads/day per GCP project. Metadata updates (~51 units), status
polls, and thumbnail sets are comparatively cheap.

---

## Re-running a step

There is no bespoke retry/sync button. To re-run any YouTube step manually, open the conversation
detail page (`/coherence/conversation/<id>/`), select the step in the pipeline inspector, and use
**Reset** — the honest-reset dialog shows exactly what will be cleared before you confirm.

- **Metadata / thumbnail sync** are idempotent and safe to reset and re-run freely (e.g. to
  re-publish an edited title/description or a regenerated thumbnail).
- **Video upload** is the expensive one: resetting it does **not** delete the already-uploaded
  video from YouTube, so a re-run uploads a second copy. The reset dialog warns about this when a
  video already exists. Delete the video on YouTube first if that is not what you want.

---

## Related files

- Jobs: `metis_apps/coherence/iris_youtube.py` (`YouTubeVideoUpload`, `YouTubeMetadataSync`, `YouTubeThumbnailSync`)
- Config schemas: `metis_apps/coherence/iris_models.py` (`YouTubeVideoUploadConfig`, `YouTubeMetadataSyncConfig`, `YouTubeThumbnailSyncConfig`)
- Step config templates: `metis_apps/coherence/templates/coherence/partials/iris_config_youtube_{video_upload,metadata_sync,thumbnail_sync}.html`
- Connected-channel chip: `metis_apps/coherence/templates/coherence/partials/_youtube_channel_chip.html`
- OAuth views: `metis_apps/coherence/views.py` (`journey_step_youtube_auth_start`, `journey_step_youtube_auth_callback`)
- Reset (re-run) views: `metis_apps/coherence/views.py` (`conversation_iris_step_reset_preflight`, `conversation_iris_step_reset`)
