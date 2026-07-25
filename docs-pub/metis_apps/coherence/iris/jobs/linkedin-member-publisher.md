# LinkedIn Member Publisher

| | |
|---|---|
| **Label** | LinkedIn Member Publisher |
| **Slug** | `linkedin_member_publisher` |
| **File** | `metis_apps/coherence/iris_linkedin_member.py` |
| **Class** | `LinkedInMemberPublisher` |
| **Depends on** | `youtube_video_upload`, `youtube_visibility_promote`, `publish_waiter` |

## Purpose

Publishes the approved post to **one personal LinkedIn profile**, configured on the step:

```
one JourneyStep
  -> one configured LinkedIn member
  -> one access token belonging to that member
  -> one LinkedIn post per conversation
```

The author is set on the step, **not** discovered from the conversation's participants.
Every conversation reaching this step publishes publicly as that same person — typically a
host, producer, or employee who has personally granted METIS permission to post on their
behalf.

This is deliberately not a mode of [`linkedin_publisher`](linkedin-publisher.md). Page and
member publishing differ in author identity, OAuth scope, token owner, and who can take a
post down, so they are separate jobs writing separate records. A journey may run either or
both; when both run, downstream copy labels the two links distinctly.

**Not included:** choosing an author from the participant list at runtime, publishing to
every participant, more than one member publisher per journey, a member-facing LinkedIn
Connect screen, automatic token refresh, engagement analytics, or automatic edit/delete
after publication. Participants' own sharing remains assisted — copy the suggested caption
and open LinkedIn.

## Pipeline position

- **Upstream:** `youtube_video_upload` (video URL), `youtube_visibility_promote` (the video
  must actually be public), and `publish_waiter` (the approval gate).
- **Feeds into:** `publish_live_notifier` and `telegram_distributor`.

Unlike the Page publisher, this step waits for `records.youtube.promoted_at`. A public
personal post must not point at an episode that is still unlisted.

## One member means one member

At most one **active** `linkedin_member_publisher` step is allowed per journey; the journey
editor rejects a second one. The job owns a single record path rather than an
instance-scoped subtree, so two instances would share — and on reset clear — each other's
result. Supporting several member publishers means giving the registry instance-scoped
ownership first, not just lifting the check.

## Data flow

**Reads**
- `fields.linkedin_post` — the same approved copy the rest of the pipeline uses. V1 does not
  generate separate first-person copy for the member; if a journey runs both publishers,
  both use this text.
- `records.youtube.video_url`, `records.youtube.promoted_at`.
- `infos["publishing_status"]["state"]` — must be `approved`, re-read immediately before
  publishing.

**Writes** — `records.linkedin.member_post`, the same shape as the Page publisher's record
(see [LinkedIn Page Publisher](linkedin-publisher.md)) with `author_urn` being a
`urn:li:person:…` value.

## Configuration

| Field | Meaning |
|---|---|
| `author_urn` | `urn:li:person:<id>`. Must be the same member who granted the token — a mismatch is rejected by LinkedIn, not caught locally. |
| `author_name` | Display name. Used in participant copy such as "View or reshare Alex's LinkedIn post", so it must be present. |
| `access_token` | Token with `w_member_social`, granted by that member. Never returned by the API, never rendered, never logged. |
| `access_token_expires_at` | Optional; publishing fails before any network call once past. |

The step editor states plainly that every conversation reaching it publishes publicly as the
configured person.

## Behaviour details

Identical safety model to the Page publisher: approval re-read immediately before the call,
a durable publication ledger written before any network I/O, no HTTP on a rerun after
success, and `unknown` results that never retry automatically and cannot be reset away. See
[LinkedIn Page Publisher](linkedin-publisher.md#behaviour-details) for the state machine.

## Step slug convention

`"linkedin_member_publisher"`.

## Testing this step

Covered by `metis_apps/coherence/tests/test_iris_linkedin.py` alongside the Page publisher,
including the person/organization URN split, the public-video gate, record independence
between the two publishers, and the single-instance journey rule.

## Related runbooks

- *takedown-linkedin* — reconciliation and takedown (internal engineering doc, not published
  here). Removing a personal post is the member's own action; METIS cannot do it.
