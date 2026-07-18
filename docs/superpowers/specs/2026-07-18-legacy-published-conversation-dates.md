# Repair dates for legacy YouTube-imported conversations

Related: [CoCo live context for public events and published conversations](https://github.com/Vorski-Imagineering/METIS-pub/issues/185).

## Problem

A read-only audit of the METIS development database on 2026-07-18 found 28
legacy Coherence conversations with a public YouTube video (`video_id` and
`url` in `infos["publishing"]["youtube"]`) but no `start` or `finish` value.

Those records were created by
`import_youtube_playlist`. The command already reads a `published_at` value
from each *playlist item*, but it never persists that value. More importantly,
that value is publication/playlist metadata, not proof of when a conversation
occurred, so it must not be copied into `Conversation.start` or `finish`.

Consequently METIS cannot truthfully answer time-based questions about these
published recordings. Until repaired, they must be presented as:

> Published conversations with unknown conversation date

They must not appear in chronological "recent conversations" results.

## Proposed change

Extend the existing `import_youtube_playlist` management command with an
explicit **date-backfill mode** for conversations it previously imported.

Normal import behaviour remains unchanged:

- new playlist videos create conversations;
- existing `video_id` matches remain skipped;
- no existing conversation is changed during a normal import.

The new mode is intentionally separate, for example:

```text
python3 manage.py import_youtube_playlist <journey_slug> <playlist_id> <agent_slug> \
  --backfill-dates --dry-run
```

After reviewing the dry-run report, repeat without `--dry-run` to apply only
the verified updates.

## Backfill algorithm

1. Fetch the playlist as the command does today and identify existing
   conversations by `infos["publishing"]["youtube"]["video_id"]`.
2. Fetch each matched video through YouTube's **videos** resource with
   `part=snippet,recordingDetails`.
3. Classify the result:

   | YouTube field | Meaning | METIS action |
   |---|---|---|
   | `recordingDetails.recordingDate` | Date/time the video was recorded | When present and `Conversation.start` is null, use it as a candidate conversation start date; retain source/provenance. |
   | `snippet.publishedAt` | Date/time the video became public (which may differ from upload time) | Record as a distinct publication-date fact; never write it to `start` or `finish`. |
   | Neither field | No verified temporal value | Leave conversation dates unchanged and report it as date unknown. |

4. Never overwrite a non-null `start` or `finish` value in this mode.
5. Do not invent `finish`: YouTube metadata does not establish the conversation
   end time.
6. Produce a per-record report with METIS conversation id, video id, values
   found, intended/applied changes, and classification:
   `conversation-date-backfilled`, `publication-date-only`, `date-unknown`,
   `already-dated`, or `video-not-found`.

## Data contract and provenance

`Conversation.start` and `Conversation.finish` mean when the conversation
occurred. YouTube `publishedAt` means when the recording became public. They
are different facts.

Before applying the non-dry-run command, agree the controlled metadata contract
for the publication date and provenance. A reasonable candidate is a namespaced
extension under `infos["publishing"]["youtube"]`, containing the API value,
source URL/video id, and retrieval timestamp. This is a public-data contract
change and must be reviewed deliberately; it is not an excuse to overload
`start` or `finish`.

For a `recordingDate` written to `start`, preserve enough provenance to show
that it came from the YouTube API and which video supplied it. If the API value
is absent, ambiguous, or conflicts with an existing METIS date, do not guess;
report it for manual resolution.

## Safety requirements

- `--backfill-dates` operates only on existing conversations matched by video
  id in the requested Journey/playlist.
- `--dry-run` performs all reads and prints the complete report without writing
  to METIS.
- The command is idempotent: a second run does not overwrite dates or create
  duplicate conversations.
- API failures, deleted/private videos, malformed dates, and ownership
  mismatches are reported and do not cause unrelated records to change.
- The command does not alter publication policy, Journey steps, participants,
  transcript data, generated content, or YouTube metadata other than the
  approved temporal/provenance fields.

## Acceptance criteria

- The 28 legacy YouTube-imported conversations can be audited in dry-run mode.
- `recordingDetails.recordingDate` fills only previously-null `start` values;
  `finish` remains unchanged.
- `snippet.publishedAt` is retained only as a publication date, never as a
  conversation date.
- Records lacking an actual recording date remain visible as "published
  conversations with unknown conversation date" and are omitted from date-based
  "recent" results.
- Re-running normal import still skips existing videos without changing them.
- Re-running date backfill is idempotent and emits an auditable summary.
- Tests cover dry run, date backfill, publication-date-only, missing metadata,
  existing-date protection, and API errors.

## Out of scope

- Guessing dates from primary keys, local file timestamps, migration timestamps,
  or import/worker activity.
- Reconstructing `finish` from YouTube metadata.
- Making unpublished/internal conversations public.
- Choosing CoCo search or RAG architecture.
