# LinkedIn Page Publisher

| | |
|---|---|
| **Label** | LinkedIn Page Publisher |
| **Slug** | `linkedin_publisher` |
| **File** | `metis_apps/coherence/iris_linkedin.py` |
| **Class** | `LinkedInPublisher` |
| **Depends on** | `youtube_video_upload`, `publish_waiter` |

## Purpose

Publishes the approved post to a **LinkedIn organization Page** using LinkedIn's official
Posts API. One approved conversation produces exactly one public Page post.

The Page is the author. Participants do not connect LinkedIn accounts to METIS, do not
install the browser extension, and do not leave a browser running. They receive the
resulting public post URL from `publish_live_notifier` so they can view and reshare it.

> **This replaced an extension-based design.** An earlier version queued
> `OutreachAction(PUBLISH_POST)` rows for the Chrome extension to execute in each
> participant's own browser. That path could never complete — the extension had no
> `publish_post` executor and the completion endpoint could not return a post URL — and it
> made a human-operated outreach queue responsible for a reliable server publication. Any
> leftover `publish_post` action rows are untouched by this job; cancel them through the
> outreach UI.

For posting as a **person** rather than a Page, see
[LinkedIn Member Publisher](linkedin-member-publisher.md). A journey may run either or both.

## Pipeline position

- **Upstream:** `youtube_video_upload` (for the video URL) and `publish_waiter` (for the
  approval gate).
- **Feeds into:** `publish_live_notifier` and `telegram_distributor`, both of which link to
  the published post.

## Data flow

**Reads**
- `fields.linkedin_post` — the approved copy.
- `records.youtube.video_url` — appended to the copy exactly once, unless already present.
- `infos["publishing_status"]["state"]` — must be `approved`, re-read immediately before
  publishing.

**Writes** — `records.linkedin.organization_post`:

```json
{
  "status": "published",
  "author_urn": "urn:li:organization:123456",
  "author_name": "The Coherence Company",
  "post_urn": "urn:li:share:987654321",
  "post_url": "https://www.linkedin.com/feed/update/urn:li:share:987654321/",
  "commentary_sha256": "…",
  "api_version": "202607",
  "request_id": "…",
  "attempt_count": 1,
  "started_at": "2026-07-25T12:00:00+00:00",
  "published_at": "2026-07-25T12:00:01+00:00",
  "last_error": ""
}
```

`post_url` is required for `status: "published"` — the job never advances to participant
notification with only a URN, and no downstream consumer reconstructs a URL from one.

## Configuration

Set on the JourneyStep:

| Field | Meaning |
|---|---|
| `author_urn` | The Page's API identity, `urn:li:organization:<numeric id>`. **Not** the number in a `linkedin.com/company/...` URL. |
| `author_name` | Display name, shown to operators and used to label the reshare link. |
| `access_token` | LinkedIn token with `w_organization_social`. Never returned by the API, never rendered, never logged. |
| `access_token_expires_at` | Optional. Publishing fails before any network call once past; a warning shows within 7 days. |

The dated LinkedIn API version is a single project-wide constant, not a per-step setting.

Setup (LinkedIn app, product access, obtaining a token) is an internal engineering doc, not
published here.

## Behaviour details

- **Approval gate:** `publishing_status.state` must be `approved`. `waiting` or missing
  retries later; `blocked` (a participant opted out) is a permanent stop.
- **Idempotency:** the publication record is a durable ledger. A rerun after success makes
  no HTTP call at all. Two concurrent workers produce one create attempt (the claim is
  serialised with `SELECT … FOR UPDATE`).
- **Uncertain results never retry.** LinkedIn's create-post operation has no
  client-supplied idempotency key, so a read timeout, a 5xx, a 409, or a `201` METIS cannot
  interpret leaves the record in `unknown`. That is a permanent stop requiring manual
  reconciliation, because retrying could publish a second public post.
- **Reset is refused** while the record is `submitting`, `unknown`, or `published` — clearing
  METIS state does not delete a LinkedIn post. Reset is allowed from `failed` or `retryable`.

### Publication states

```
absent ──preconditions ok──> submitting ──201───────────> published
                                  ├─rejected───────────> failed
                                  ├─429 / pre-send─────> retryable ──> submitting
                                  └─timeout/5xx/409────> unknown  (manual only)
```

## Step slug convention

`"linkedin_publisher"` (matches `config["iris_job"] = "linkedin_publisher"`).

## Testing this step

`metis_apps/coherence/tests/test_iris_linkedin.py` covers the adapter, preconditions,
approval gate, success and idempotency, every failure classification, and the reset guard.
No test makes a live LinkedIn call.

## Related runbooks

- *takedown-linkedin* — reconciling an `unknown` result or removing a published post
  (internal engineering doc, not published here).
- *manual-retrigger*, *consent-withdrawal* (internal engineering docs).
