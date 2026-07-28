# LinkedIn Member Publisher

Publishes the approved post to **one personal LinkedIn profile**, configured on the step.

```
one journey step
  → one configured LinkedIn member
  → one token that member personally granted
  → one post per conversation
```

The author is set on the step, **not** picked from the conversation's participants. Every
conversation reaching this step publishes publicly as that same person — typically a host,
producer, or employee who has personally given METIS permission to post on their behalf. The
step editor says so plainly.

## At a glance

| | |
|---|---|
| **Needs** | The approved copy, a **public** video, a cleared consent gate, and that member's connection |
| **Produces** | A public LinkedIn post on that person's profile, and its URL |
| **Waits when** | The consent gate hasn't cleared, or the video isn't public yet |
| **Re-running** | Safe after success — it makes no call at all. Some states refuse reset entirely |

## Why it's a separate step, not a mode

Page publishing and member publishing differ in who the author is, what permission the token
carries, who owns that token, and — crucially — **who can take the post down**. A personal post
can only be removed by that person; METIS cannot. Keeping them as separate steps with separate
records means neither can quietly overwrite or reset the other's result, and downstream copy
can label the two links distinctly when a journey runs both.

**One per journey.** At most one active member publisher is allowed, and the journey editor
rejects a second. The step owns a single record path, so two instances would share — and on
reset clear — each other's result.

**Not included:** picking an author from the participant list at run time, publishing for every
participant, a member-facing self-service Connect screen, automatic reconnection, engagement
analytics, or editing/deleting a post after publication. Participants' own sharing stays
assisted: they get the suggested copy and a link, and post it themselves.

## Waiting for the video to be public

Unlike the Page publisher, this step also waits for the video to be flipped public. A public
post on someone's personal profile must not point at an episode that's still unlisted.

## Safety model

Identical to the [Page publisher](linkedin-publisher.md#the-safety-model): consent is re-read
immediately before posting, the record is written before any network call, a rerun after
success makes no call, and an **unknown** result never retries automatically and cannot be
reset away. Read that section — it applies here in full.

## Settings

| Setting | Meaning |
|---|---|
| Author URN | `urn:li:person:<id>`. Must be the same member who granted the token — a mismatch is rejected by LinkedIn, not caught locally |
| Author name | Display name. Used in participant copy ("View or reshare Alex's LinkedIn post"), so it must be filled in |
| Access token | A token that member granted, permitting posts on their behalf. Never displayed, never logged |
| Token expiry | Optional; publishing fails before any network call once past it |

**Connect LinkedIn** runs the consent flow *as that member* — they sign in personally — and
saves the token and expiry. It does not fill in the author URN or name. The connection expires
(around 60 days) and has to be renewed the same way.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| Waiting with no error | The consent gate hasn't cleared, or the video isn't public yet | Check the waiter and the visibility promote steps |
| Error: rejected by LinkedIn | The author URN isn't the member who granted the token | Reconnect as the correct person, or fix the author URN |
| Error mentioning expiry | The member's connection has lapsed | That member must sign in again via **Connect LinkedIn** |
| Journey editor refuses a second member step | Only one is allowed per journey | Use the single step; supporting several needs a change to how records are owned |
| Result shows **unknown** | LinkedIn's response was inconclusive | **Do not retry.** Check the profile on LinkedIn and reconcile manually |
| Published as the wrong person | The step is configured with a different member than expected | Check the author name shown on the step — it's what participant copy will say |
| Need the post removed | METIS cannot delete a personal post | Only that member can remove it, from their own LinkedIn |

## Technical reference

| | |
|---|---|
| **Step type** | `linkedin_member_publisher` |
| **Runs after** | `youtube_video_upload`, `youtube_visibility_promote`, `publish_waiter` |
| **Feeds** | `publish_live_notifier`, `telegram_distributor` |
| **Reads** | `fields.linkedin_post` (the same approved copy the rest of the pipeline uses — no separate first-person version is generated), `records.youtube.video_url`, `records.youtube.promoted_at`, `infos["publishing_status"]["state"]` |
| **Writes** | `records.linkedin.member_post` — same shape as the Page publisher's record, with a `urn:li:person:…` author |
