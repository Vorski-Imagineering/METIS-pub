# LinkedIn Publisher

| | |
|---|---|
| **Label** | LinkedIn Publisher |
| **Slug** | `linkedin_publisher` |
| **File** | `metis_apps/coherence/iris_linkedin.py` |
| **Class** | `LinkedInPublisher` |
| **Depends on** | `youtube_uploader`, `approval_waiter` |

## Purpose

Queues `OutreachAction(PUBLISH_POST)` records so the **Chrome extension** posts the approved
LinkedIn content on each participant's behalf, then polls until done. It does **not** post to
LinkedIn directly — posting is delegated to the extension.

This is one of only two multi-dependency jobs, and the one place Coherence and Outreach
genuinely intersect (it produces Outreach actions).

## Pipeline position

- **Upstream (`depends_on`):** `youtube_uploader` **and** `approval_waiter` (needs the video
  and the participants' approvals before posting on their behalf).
- **Feeds into:** `telegram_distributor` (which includes LinkedIn URLs if available).
- **Alternative to:** none.

## Data flow

**Reads**
- `infos["publishing"]["linkedin"]["posts"]` (approved post bodies), participants ordered by
  `person.pk` (first = host, second = guest).

**Writes**
- `infos["publishing"]["linkedin"]["posts"][<person_id>]` — result post URL, taken from
  `OutreachAction.infos["post_url"]`.
- `infos["publishing"]["linkedin"]["published_at"]`.

## Requirements

- **Agent.config:** none (delegates posting to the Chrome extension).
- **System:** none.
- **External credentials:** none directly — the extension holds the LinkedIn session.

## Behavior details

- **Idempotency:** `batch_id = "iris-linkedin-{conversation.pk}"` — skips participants that
  already have an active or completed action.
- **Polling:** `RetryLater` while queued actions are still pending completion by the
  extension.
- **Done vs error:** "done" once every participant's action is complete and its post URL is
  recorded; permanent error on malformed post data.

See the [Chrome extension usage guide](../../../../extension/using-the-extension.md)
for the human side of how these `OutreachAction`s get posted.

## Step slug convention

`"linkedin_publisher"` (matches `config["iris_job"] = "linkedin_publisher"`).

## Testing this step

No automated test today. Manual scenario (staging): with approved LinkedIn post bodies and
participants resolved, run → `OutreachAction(PUBLISH_POST)` rows appear under
`batch_id="iris-linkedin-<pk>"`; complete them via the extension flow → post URLs land in
`infos["publishing"]["linkedin"]["posts"]`. Re-run mid-flight → already-active participants
skipped. See the *testing guide* (internal engineering doc, not published here).

## Related runbooks

- *manual-retrigger* (internal engineering doc, not published here)
- *consent-withdrawal* (internal engineering doc, not published here).
