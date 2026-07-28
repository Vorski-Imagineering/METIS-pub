# Approval Waiter *(legacy)*

Holds the pipeline until every required participant has explicitly approved, then lets it
continue.

> **Use [Publish Notifier + Publish Waiter](publish-notifier.md) instead for new journeys.**
> This is the older consent gate. It waits for explicit approvals only — there is no
> publish-by date, no opt-out, and no notification: something else has to ask the
> participants. The newer pair does the asking, states a deadline, and treats silence and
> opt-out explicitly. This page exists for journeys that still run the old step.

## At a glance

| | |
|---|---|
| **Needs** | Approval recorded for every required participant |
| **Produces** | The approval status the publishing steps check |
| **Waits when** | Any required approval is still outstanding — potentially forever |
| **Re-running** | Safe; it has nothing to undo |

## What it does

Checks the approval state recorded on the conversation. If every required participant has
approved, it advances. If not, it waits and checks again on its next run.

**It only reads approvals; it never collects them.** Approvals are written by the
participant-facing approval page. This step is a gate, not the thing that records a decision —
which is why nothing happens here until participants have been sent links by some other means.

There's no external service to fail against, so in practice this step only ever waits or
advances; it doesn't error.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| Waiting indefinitely, no error | Someone hasn't approved yet | Check who: the step inspector lists each participant as Approved or Awaiting |
| Waiting although everyone says they approved | Their approval wasn't recorded against this conversation | Confirm they used their own link for *this* conversation; re-send links if needed |
| No one has received anything to approve | Nothing sends links in this design | Use **Send Approval Links** on the step, or move the journey to the newer notifier/waiter pair |
| Publishing needs to proceed without one person | This gate has no deadline | Resolve it with them, or switch the journey to Publish Notifier + Publish Waiter, which has a publish-by date |

## Technical reference

| | |
|---|---|
| **Step type** | `approval_waiter` |
| **Runs after** | `youtube_video_upload` (participants approve the hosted video) |
| **Feeds** | `linkedin_publisher` |
| **Reads** | `infos["publishing_approval"]["people"][<person_id>]["approved"]` |
| **Writes** | `infos["publishing_status"]` — `await_approval`, `approval_completed`, `approved`, `state`, `updated_at` |

How approvals are actually captured, from the participant's side, is in the
[participant review guide](../participant-review.md).
