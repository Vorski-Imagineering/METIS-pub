# Repair temporal metadata for legacy published conversations

Related: [CoCo live context for public events and published conversations](https://github.com/Vorski-Imagineering/METIS-pub/issues/185).

## Problem

A read-only audit of the METIS development database on 2026-07-18 found 28
legacy Coherence conversations with a public YouTube video (`video_id` and
`url` in `infos["publishing"]["youtube"]`) but no `start` or `finish` value.

Those records are genuinely published material, but their conversation date is
unknown. As a result, METIS cannot truthfully answer time-based questions such
as:

- "What conversations happened recently?"
- "What was published last month?"
- "Show public conversations from 2025."

They must not be mixed into a chronological "recent conversations" result.

## Required behaviour until repaired

Present these records as:

> Published conversations with unknown conversation date

Do not label them "recent", sort them as if their primary key were a date, or
silently use upload/import timestamps as a substitute for the conversation
date.

## Candidate sources, in order of confidence

1. A verified historical source imported with the conversation, if one exists.
2. The original calendar/booking record, when it can be matched unambiguously.
3. The YouTube publication date, explicitly stored as a *publication date* —
   not as the conversation's `start` or `finish` time.
4. A manually verified date supplied by the recording owner or organiser.

YouTube publication date can establish when a recording became public. It does
not prove when the conversation took place, so it must remain a distinct fact.

Do not derive dates from primary-key order, local file timestamps, migration
timestamps, or the date a worker processed a record. Those are operational
artefacts and would create false chronology.

## Proposed repair workflow

1. Inventory every published conversation without `start` and `finish`.
   Record its METIS id, event, Journey, YouTube URL/video id, title, and any
   available external reference.
2. Resolve each record against the sources above. Mark the result as one of:
   `conversation date verified`, `publication date verified only`, or
   `date unknown`.
3. Preserve provenance for every populated value: source URL/reference, who
   verified it, and when. A date without provenance is not a repair.
4. Update `Conversation.start`/`finish` only when the conversation date itself
   is verified. Populate a separate publication-date representation only after
   its ownership and semantics have been designed and approved.
5. Produce an exception report for unresolved records. They remain publicly
   discoverable, but are shown in the undated published section.
6. Add regression coverage for public list/search behaviour so dated and
   undated published records never merge into one chronological bucket.

## Data-model decision required

`Conversation.start` and `Conversation.finish` describe when the conversation
occurred. A YouTube publication date is different domain data.

If METIS needs to answer "when was this published?", introduce an explicit,
provenanced publication-date contract rather than overloading `start` or
`finish`. That may require a schema or controlled JSON-contract change and must
go through the normal model/data-migration approval process, including a
rollback plan.

## Acceptance criteria

- Every legacy published conversation is classified as date-verified,
  publication-date-only, or date-unknown.
- No unknown-date record appears in a "recent" or date-range result.
- A verified YouTube date is displayed as publication date, never as an
  asserted conversation date.
- Every repaired date has traceable provenance.
- CoCo and any public API/UI surface can distinguish scheduled, dated past, and
  published-with-unknown-date records without inventing chronology.

## Out of scope

- Inferring dates from identifiers or operational timestamps.
- Making unpublished/internal conversations publicly visible.
- Changing publication policy or public-visibility rules.
- Choosing a semantic-search or RAG architecture for CoCo.
