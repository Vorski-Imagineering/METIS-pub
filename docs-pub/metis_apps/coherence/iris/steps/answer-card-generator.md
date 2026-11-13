# Instagram Card

Renders one Instagram card from an answer to an ask: the question at the top, the
person's words, and the name they gave. Part of the
[answer publishing pipeline](../../../ask/asks.md#publishing-answers); a Coherence
conversation has no use for it.

## At a glance

| | |
|---|---|
| **Needs** | The answer; for a long answer, the quotes the Content Generator picked |
| **Produces** | One portrait image, 1080 × 1350 (4:5), PNG |
| **Waits when** | Never: a long answer with no quote yet is an error, with a message |
| **Re-running** | Safe and cheap; the card is replaced |

## What it does

Makes one card per answer, from an HTML template in the step's **template pack**, as the
[Cover Image Generator](cover-image-generator.md) does — not with an image-generating AI.

- **Which words.** An answer of 40 words or fewer goes on the card whole. A longer answer
  shows the first quote the [Content Generator](content-generator.md) picked from it: one
  striking sentence or two, never the whole answer. Long text shrinks to fit the card.
- **Which question.** The one the answer was given to. For a video answer, the question
  linked to the part of the transcript the words came from, when there is one.
- **Whose name.** The person linked to the answer, with their photo; otherwise the name
  they typed, with its initials in a cell. An answer with no name has no name line.

The card is portrait 4:5, the tallest shape Instagram's feed shows without cropping. Nothing
is posted: the team downloads the card from the answer while approving it and posts it by
hand.

## How it behaves

- **Place it after the Content Generator,** whose quotes it reads, and before the team's
  approval. Placed before it, a long answer has no quote yet and the step fails (below).
- **A long answer with no quote fails** with *No excerpt to put on the card: run the
  content step first.* Re-run the content step, then this one.
- **Re-running replaces the card.** Resetting the step deletes the image.
- **Deleting the answer deletes the card.** Copies already posted on Instagram stay up.

## Settings

Set on the step: the **template pack**. Only packs with an answer card can be chosen — today
*The Gathering* (the default) and *Default*. Any other is refused with *This style has no
answer card yet.*

To see a pack's answer card without running the pipeline, open the card gallery (the **Card
gallery** card on the Coherence settings page): it shows the answer card, with sample text,
for every pack that has one.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| Failed: *No excerpt to put on the card* | A long answer, and the content step stored no quotes | Re-run the [Content Generator](content-generator.md), then this step |
| Failed: *could not be rendered* | The rendering browser isn't installed or can't start on the server | An administrator installs it; then re-run |
| Settings refused: *This style has no answer card yet* | The chosen pack has no answer card | Choose *The Gathering* or *Default* |
| Initials instead of a photo | No person is linked to the answer, or the person has no photo | Link the person (*Link a person*) or add their photo, then re-run |

## Technical reference

| | |
|---|---|
| **Step type** | `answer_card_generator` |
| **Runs after** | `content_generator` |
| **Feeds** | Nothing; the image is for download |
| **Reads** | the answer (`infos["ask"]`), its transcript for a video answer, its linked person's photo, `fields.instagram_quotes`; step setting `template_pack` |
| **Writes** | `artifacts.instagram.answer_card` |
| **Needs on the server** | A headless Chromium for rendering |
