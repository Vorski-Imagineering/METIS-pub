# Cover Image Generator

Renders the branded images for a conversation: the video thumbnail, the LinkedIn header, and
quote cards for social sharing.

## At a glance

| | |
|---|---|
| **Needs** | The generated title (and, for quote cards, the quotes) |
| **Produces** | Thumbnail, LinkedIn header, quote card images |
| **Waits when** | The draft hasn't been generated yet |
| **Re-running** | Safe and cheap — re-render freely after the content changes |

## What it does

Renders images from HTML templates using the conversation's title, quotes and participant
photos — not from an image-generating AI. Templates are why every episode looks like it
belongs to the same show: same layout, same type, same treatment, only the content differs.

Each journey picks a **template pack**, and the pack supplies all three templates. Changing
the pack on a journey step changes the design of everything that journey renders from then on.

Some packs ship their own image library and pull artwork from it at render time, so their
cards differ between runs and between sibling cards in the same run. Draws come from a
shuffled deck, so a batch exhausts the library before repeating an image. Because the choice
happens during rendering, it isn't recorded with the result — if you want a specific image,
re-render until you get one you like, or use a pack without a library.

Packs also differ in whether they show participants' faces. The step always looks up each
participant's photo and hands it to the pack; whether the card draws it is the pack's choice.
The default pack sets the names as a list instead, so a conversation with no portraits on file
looks exactly like one where everybody has a good headshot.

## How it behaves

- **It waits for the title.** No title means no card to render, so the step waits rather than
  failing.
- **Partial success counts as success.** If one card fails to render, it's skipped and logged;
  the step only fails outright if *nothing* rendered.
- **Re-rendering is expected.** Changed the title or the quotes? Re-render. The images are
  cheap to make.
- Pushing a regenerated thumbnail to an already-uploaded video is a **separate** step — see
  [YouTube publishing](youtube-uploader.md).

## Settings

Set on the step: the template pack, whether to generate each of the thumbnail / LinkedIn
header / quote cards, and the maximum number of quote cards.

To judge whether a card actually *looks* right, use the card preview route in a browser
(`?pack=<name>&conversation=<id>`) — automated checks can only confirm that a card rendered,
not that it's good.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| Waiting with no error | The draft hasn't been generated yet | Normal. Check the [Content Generator](content-generator.md) step. |
| No cards at all, step failed | The rendering browser isn't installed or can't start on the server | An administrator installs it; then re-run |
| Some quote cards missing | Those individual renders failed, or there were fewer quotes than the card limit | Check the quotes in the Publishing panel; re-render |
| Cards show the old title | They were rendered before the content changed | Re-render this step |
| Video still shows the old thumbnail | The thumbnail is pushed to YouTube by a separate step | Re-run the thumbnail sync step |
| Participant photos missing from cards | Those People have no photo on record | Add photos to the Person records, then re-render |
| Wrong branding | The journey step is using a different template pack | Change the pack on the step, then re-render |
| Old image files piling up | Each re-render writes new files | Harmless; an administrator can clean up orphaned image files |

## Technical reference

| | |
|---|---|
| **Step type** | `cover_image_generator` |
| **Runs after** | `content_generator` |
| **Feeds** | `youtube_thumbnail_sync` (and any other consumer of the generated images) |
| **Reads** | `fields.title`, `fields.subtitle`, `fields.instagram_quotes`, participant `Person.photo`; step settings `template_pack`, `generate_thumbnail`, `generate_linkedin_header`, `generate_quote_cards`, `quote_card_limit` |
| **Writes** | `artifacts.thumbnail`, `artifacts.linkedin_header`, `artifacts.instagram_quote_cards`, `records.cover_images` |
| **Needs on the server** | A headless Chromium for rendering |
