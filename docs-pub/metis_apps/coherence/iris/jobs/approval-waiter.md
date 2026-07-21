# Approval Waiter

| | |
|---|---|
| **Label** | Approval Waiter |
| **Slug** | `approval_waiter` |
| **File** | `metis_apps/coherence/iris_approval.py` |
| **Class** | `ApprovalWaiter` |
| **Depends on** | `youtube_video_upload` |

## Purpose

Holds the pipeline until all required **participant approvals** are in, then advances.

## Pipeline position

- **Upstream (`depends_on`):** `youtube_video_upload` (participants approve the hosted video).
- **Feeds into:** `linkedin_publisher` (which also depends on this job).
- **Alternative to:** none.

> **Boundary to call out:** this job only *reads* approval state. That state is written by
> the **participant-facing approval page view**, not by this job. The job is a gate, not the
> thing that records an approval.

## Data flow

**Reads**
- `infos["publishing_approval"]["people"][<person_id>]["approved"]`

**Writes**
- `infos["publishing_status"]` (await_approval, approval_completed, approved, state,
  updated_at).

## Requirements

- **Agent.config:** none.
- **System:** none.
- **External credentials:** none.

## Behavior details

- **`RetryLater` conditions:** any required approval is still outstanding — the job re-waits
  each run.
- **Done vs error:** "done" once every required approval is in; there's no external call to
  fail, so this job effectively only "done"s or `RetryLater`s.

## Step slug convention

`"approval-waiter"` (matches `config["iris_job"] = "approval_waiter"`).

## Testing this step

No automated test today. Manual scenario (staging): set
`infos["publishing_approval"]["people"][<id>]["approved"]` for a subset of required
participants → `RetryLater`; set all required → advances and `infos["publishing_status"]`
records completion. See the *testing guide* (internal engineering doc, not published here), and the
public-facing [participant approval guide](../participant-approval.md)
for how approvals are actually captured.

## Related runbooks

- *manual-retrigger* (internal engineering doc, not published here)
