# YouTube setup

Connecting IRIS to a YouTube channel. The Google Cloud project and OAuth client are set up once
by a METIS admin; what you do, per journey, is click **Connect YouTube** on the video-upload
step and authorise the channel that journey publishes to.

For what the YouTube steps actually do, see
[YouTube publishing](steps/youtube-uploader.md). This page is purely the setup.

**A constraint worth knowing up front:** YouTube does not accept service accounts for channel
uploads. Only credentials authorised by a real channel **owner**, in a browser, will work —
which is why there is a Connect button rather than a key to paste. Service account keys are
explicitly rejected.

The channel is connected on the **video upload** step only. The metadata-sync and
thumbnail-sync steps inherit that connection, so all three always publish to the same channel.
Different journeys can connect different channels.

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

## Which Google account to connect with

This is the step that most often goes wrong, and it has its own page:
**[YouTube accounts and channel access](youtube-accounts.md)** — personal vs Brand Account
channels, how to grant the Owner access the API requires, and why someone who uploads to the
channel by hand every week may still be unable to connect it.

The short version:

> **Only an _Owner_ of a channel can authorise API access to it.** YouTube Studio "channel
> permissions" of Manager, Editor and so on let someone upload on the website, but **that access
> is invisible to OAuth and the YouTube Data API** — so the channel won't appear at Connect
> time. For an organisation channel, the connecting Google account must hold Owner on the Brand
> Account.

Whichever kind of channel it is, the name displayed next to **Connected** (in the step editor
and on the conversation step inspector) is the source of truth for what IRIS will actually
upload to — always check it after connecting.

### Step config fields (`youtube_video_upload`)

| Field | Required | Default | Notes |
|-------|----------|---------|-------|
| `iris_job` | yes | — | Must be `youtube_video_upload` |
| `youtube_refresh_token` | auto | — | Written by Connect flow — do not edit manually |
| `youtube_channel_id` / `youtube_channel_title` / `youtube_channel_avatar_url` | auto | — | Resolved and stored by the Connect flow; drive the connected-channel display |
| `visibility` | no | `unlisted` | `unlisted` or `private` (`public` is set in the approval step) |
| `category_id` | no | `22` | YouTube category ID — 22 = People & Blogs |
| `processing_timeout_minutes` | no | `30` | How long to keep polling YouTube's processing before giving up for this run and retrying later |

The `iris_job` value binds the step to this job and **must be exactly `youtube_video_upload`**
(underscore). The step's own name/slug is free-form and has no effect on matching.

The metadata-sync step also takes a `category_id` (resent on every metadata update — YouTube
requires it in the snippet); the thumbnail-sync step takes no options. Neither holds its own
channel token. See [YouTube publishing](steps/youtube-uploader.md) for those two steps.

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

The upload step checks these before uploading. Anything missing makes the step wait and try
again on its next run — it doesn't error:

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

What each of the three steps reads and owns, and how errors are classified, is in
[YouTube publishing](steps/youtube-uploader.md); it isn't repeated here. Two setup-relevant
facts:

- **Re-authorisation is the failure you configure for:** an expired or revoked connection is a
  **permanent** failure — the fix is to reconnect (see [Re-authorising](#re-authorising-token-expired-or-revoked)
  above). Almost everything else (missing inputs, server errors, network failures, quota
  exhaustion, processing not finished) is retried automatically on the next scheduled run.
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

## Troubleshooting the setup

| Symptom | Likely cause | What to do |
|---|---|---|
| The consent flow times out or says the request is invalid | More than 10 minutes passed between clicking Connect and finishing | Just click **Connect YouTube** again |
| Google "did not return a refresh token" | A stale prior authorisation on that Google account | Revoke the app at [myaccount.google.com/permissions](https://myaccount.google.com/permissions), then Connect again |
| Connected, but the wrong channel name is shown | The personal channel was picked instead of the organisation one, or the account lacks Owner access | Click **Reconnect** and pick carefully — and see [YouTube accounts and channel access](youtube-accounts.md) |
| The organisation channel doesn't appear in the picker | The signed-in account only has Studio Manager/Editor access, which the API cannot see | Have an existing owner grant genuine **Owner** access, then reconnect |
| No account picker appeared at all | That Google account has exactly one channel — there was nothing to choose | Normal. Just confirm the channel name shown afterwards |
| Every upload fails with an authorisation error immediately after connecting, or uploads worked then all failed about a week later | A platform-level OAuth client/config issue, not something fixable from the Connect button | Ask a METIS admin to check the GCP client and agent config |
| Error: connection expired or revoked | Access was revoked, or the owner changed their Google password | Reconnect on the step |
| A sync step fails with permission denied or video not found | That step has its own stale authorisation pointing at a different channel | Clear it so the sync steps inherit the upload step's channel |

Step-level symptoms (waiting for a title, processing delays, duplicate uploads, quota) are in
[YouTube publishing → Troubleshooting](steps/youtube-uploader.md#troubleshooting).
