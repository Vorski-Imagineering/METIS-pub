# Question Linker

Links each line of a video answer's transcript to the question that was on screen when it
was said. Part of the [Answers journey](../../../ask/asks.md#several-questions-in-one-ask)
of an ask; a Coherence conversation has no use for it.

## At a glance

| | |
|---|---|
| **Needs** | The answer's transcript, from the [Transcript Importer](transcript-importer.md) |
| **Produces** | Each transcript line linked to its question |
| **Waits when** | Never: a video answer with no transcript is an error, with a message |
| **Re-running** | Safe; the same links every time |

## What it does

An ask can hold several questions, shown one after another during one recording. With a
video answer, the room sends the moment each question came up. The transcript's lines are
timed from the start of the take, so each line belongs to the last question that had come
up by then. Lines spoken before the first question came up go with the first question.

- **An answer to one question** has no moments: every line is linked to its one question.
- **A text answer** is linked as it arrives, one line per question, and never meets this
  step.

The answer's page then shows the transcript question by question, each question as a
heading with what was said under it.

## How it behaves

- **Place it after the Transcript Importer,** whose lines it links, and before *Received*.
- **No transcript fails** with *No transcript to link to questions.* Re-run the Transcript
  Importer, then this step.
- **Re-running gives the same links.** Resetting the step clears every line's question.
- **A question with nothing said under it** (*Next question* pressed without speaking) has
  no lines, and shows no heading.

## Settings

None.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| Failed: *No transcript to link to questions.* | The transcript was not imported, or was cleared | Re-run the [Transcript Importer](transcript-importer.md), then this step |
| One undivided transcript on an answer to several questions | The step has not run yet | Wait a few minutes; check the step's state on the answer |

## Technical reference

| | |
|---|---|
| **Step type** | `answer_question_linker` |
| **Runs after** | `transcript_importer` |
| **Feeds** | The answer card's transcript, and the [Instagram Card](answer-card-generator.md)'s question |
| **Reads** | the answer (`infos["ask"]`: its `parts` and `capture_started_at`), its transcript lines' `offset_ms` |
| **Writes** | Each transcript line's question (a shared `Question`, found by its exact words or made) |
