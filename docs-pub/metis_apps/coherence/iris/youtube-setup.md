# YouTube setup

Connecting IRIS to a YouTube channel. The Google Cloud project and OAuth client are set up once
by a METIS admin; what you do, once per brand, is press **Connect** beside YouTube on a
holon's **Publishing** page and authorise the channel that holon publishes to. Every pipeline
under that holon uses it.

For what the YouTube steps actually do, see
[YouTube publishing](steps/youtube-uploader.md). This page is purely the setup.

**A constraint worth knowing up front:** YouTube does not accept service accounts for channel
uploads. Only credentials authorised by a real channel **owner**, in a browser, will work —
which is why there is a Connect button rather than a key to paste. Service account keys are
explicitly rejected.

All four YouTube steps (upload, metadata sync, thumbnail sync, publisher) use the same login:
the nearest one connected on the conversation's event or a holon above it. Different holons can
connect different channels; a holon below that connects its own overrides the one above.

---

## Connecting a channel

On the Publishing page (paper plane) of the holon that publishes as the brand, for example
the tenant above all its events:

1. In **Connections**, press **Connect** beside YouTube (**Reconnect** if it is already
   connected here)
2. Log in as the YouTube channel owner and pick the channel; grant access
3. You come back to the Publishing page with "Connected YouTube: *channel*", and the block
   says **connected here** with the channel's name and picture

Holons below show **connected via *that holon***. The steps in the journey editor have no
connect button; they say which holon their login comes from. The login's secret is never shown.
See [Publishing settings](publishing-settings.md#connecting-youtube-and-linkedin).

Notes on the consent flow:

- You must be able to open the holon's Configuration, and the flow must complete within
  **10 minutes** of clicking it (the state token expires after that — just click again).
- The flow always forces a fresh consent screen and account/channel picker
  (`prompt=consent select_account`), so Google issues a new refresh token every time — safe to
  repeat.
- If Google reports "did not return a refresh_token", the channel owner's Google account has
  a stale prior authorisation: revoke the app at https://myaccount.google.com/permissions and
  press **Connect** again.

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

Whichever kind of channel it is, the name displayed in **Connections** on the Publishing page
is the source of truth for what IRIS will actually upload to — always check it after connecting.

### Step config fields (`youtube_video_upload`)

| Field | Required | Default | Notes |
|-------|----------|---------|-------|
| `iris_job` | yes | — | Must be `youtube_video_upload` |
| `visibility` | no | `unlisted` | `unlisted` or `private` (`public` is set in the approval step) |
| `category_id` | no | `22` | YouTube category ID — 22 = People & Blogs |
| `processing_timeout_minutes` | no | `30` | How long to keep polling YouTube's processing before giving up for this run and retrying later |

The `iris_job` value binds the step to this job and **must be exactly `youtube_video_upload`**
(underscore). The step's own name/slug is free-form and has no effect on matching.

The metadata-sync step also takes a `category_id` (resent on every metadata update — YouTube
requires it in the snippet); the thumbnail-sync step takes no options. No step holds a
channel token: the login is the holon's. See [YouTube publishing](steps/youtube-uploader.md) for those two steps.

---

## Token lifetime

The refresh token is permanent as long as:
- The GCP app remains in **Production** mode (not Testing)
- The channel owner does not revoke access at https://myaccount.google.com/permissions
- The channel owner does not change their Google password

**If you find yourself reconnecting every week, the first condition is the one to check.**
Google issues 7-day refresh tokens to any OAuth app whose publishing status is still
**Testing** (for every scope beyond basic profile/email, which includes all YouTube scopes).
Publishing the app is the fix; reconnecting is not, it just restarts the same 7-day clock.

---

## Re-authorising (token expired or revoked)

When Google rejects the token, the login is marked **rejected** on the holon that holds it:
its Publishing page says *Rejected since …* with the reason, and its team gets a note
("YouTube login rejected: … Reconnect on Publishing."). Only the conversations under that holon
wait at their YouTube steps; they are not lost or errored, and they go on by themselves once the
login works again. The journey's steps are not blocked.

Open that holon's Publishing page and press **Reconnect**. If you fixed the problem somewhere
else instead (publishing the OAuth app, restoring revoked access), press **Retry now**.

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
| The consent flow times out or says the request is invalid | More than 10 minutes passed between pressing Connect and finishing | Press **Connect** (or **Reconnect**) on the Publishing page again. The page you land on says what went wrong |
| Google "did not return a refresh token" | A stale prior authorisation on that Google account | Revoke the app at [myaccount.google.com/permissions](https://myaccount.google.com/permissions), then Connect again |
| Connected, but the wrong channel name is shown | The personal channel was picked instead of the organisation one, or the account lacks Owner access | Click **Reconnect** and pick carefully — and see [YouTube accounts and channel access](youtube-accounts.md) |
| The organisation channel doesn't appear in the picker | The signed-in account only has Studio Manager/Editor access, which the API cannot see | Have an existing owner grant genuine **Owner** access, then reconnect |
| No account picker appeared at all | That Google account has exactly one channel — there was nothing to choose | Normal. Just confirm the channel name shown afterwards |
| Every upload fails with an authorisation error immediately after connecting, or uploads worked then all failed about a week later | A platform-level OAuth client/config issue, not something fixable from the Connect button | Ask a METIS admin to check the GCP client and agent config |
| Publishing says the login was rejected | Access was revoked, or the owner changed their Google password | Reconnect on that holon's Publishing page |
| A step says "No YouTube login" | Neither the event nor any holon above it has connected YouTube | Connect it on the Publishing page of the holon that publishes as the brand |

Step-level symptoms (waiting for a title, processing delays, duplicate uploads, quota) are in
[YouTube publishing → Troubleshooting](steps/youtube-uploader.md#troubleshooting).
