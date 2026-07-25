# Content Generator — Prompt Authoring Guide

The Content Generator step lets you customise the AI instructions for each publishing asset. This guide covers the prompt sections available and how to use context injection tokens to include live conversation data in your prompts.

---

## Prompt Sections

Each section is an instruction string sent to the AI. Leave a section blank to use no special instruction for that output.

| Section | Used for |
|---------|----------|
| Base Instructions | Applied to all outputs — brand voice, tone, audience context |
| Title | Episode or video title |
| Subtitle | Tagline or short summary line |
| YouTube Description | Full video description with timestamps, speaker bios, links |
| LinkedIn Post | The single post every participant shares to their own network |
| Quotes | Selection criteria for pull quotes used in cover images |

---

## The LinkedIn post must not contain the video link

The Content Generator runs **before** the video is uploaded — the upload step needs the title and description this step writes, so at generation time there is no video URL to link to.

The URL is therefore inserted afterwards, automatically, on its own line beneath the post's closing line and above the hashtags. Every consumer does this identically: what the publish notifier shows a participant as "the post you can share" is exactly what the LinkedIn Publisher posts.

This means a LinkedIn prompt that asks for a link produces a placeholder. Asked to end with a call to action *and* a link, the model has no URL, so it writes something like `[Link to Video]` — which then goes out publicly alongside the real appended URL.

State the contract in the prompt instead:

```
End with that invitation — write no link and no placeholder for one. The video URL
is inserted automatically on its own line beneath your closing line, above the
hashtags.
```

Describing the slot as already filled is what stops the placeholder; forbidding a link on its own leaves the model with a closing section that still implies a missing one.

## Context Injection Tokens

You can paste the following tokens anywhere in any prompt section. At runtime, the token is replaced with formatted text built from the conversation's connected records.

### `[[people]]`

Expands to a block of information about each conversation participant (from the `participants` field on the conversation).

**What gets included per person:**
- `Name:` — always present
- `Description:` — if the Person record has a non-empty description
- Contact fields — any non-empty entries from the person's contact JSON (e.g. `linkedin:`, `website:`, `email:`, `twitter:`, `instagram:`, `youtube:`)
- Info fields — any non-empty entries from the person's infos JSON

**Example output:**

```
Name: Alice Smith
Description: Host of The Gathering podcast, facilitator and community builder.
linkedin: https://linkedin.com/in/alicesmith
website: https://alicesmith.com
role: Host

Name: Bob Jones
linkedin: https://linkedin.com/in/bobjones
```

Multiple participants are separated by a blank line.

---

### `[[holons]]`

Expands to a block of information about each connected holon (from the `connected` field on the conversation).

**What gets included per holon:**
- `Name:` — always present
- `Type:` — the holon's class (e.g. `organisation`, `event`, `domain`, `camp`)
- `Description:` — if the Holon record has a non-empty description
- Link fields — any non-empty entries from the holon's links JSON (e.g. `website:`, `linkedin:`)
- Info fields — any non-empty entries from the holon's infos JSON (nested values are rendered as compact JSON)

**Example output:**

```
Name: The Gathering Earth
Type: organisation
Description: A global community creating spaces for deep conversation and collective intelligence.
website: https://the-gathering.earth
linkedin: https://linkedin.com/company/the-gathering-earth
```

Multiple holons are separated by a blank line.

---

## Usage Examples

### Inject participant bios into the YouTube description

```
Write a YouTube video description including:
- A 2-sentence summary of the conversation themes
- A "Participants" section using the bios below — keep each bio to 2 sentences

[[people]]
```

### Personalise the LinkedIn post with guest's links

```
Write a LinkedIn post from the guest's perspective (1st person).
Reference their LinkedIn profile where appropriate.

Guest info:
[[people]]
```

### Include organisation context in base instructions

```
This conversation is produced by the following organisation. Reference its name and mission where relevant.

[[holons]]

Brand voice: warm, thoughtful, community-oriented. Audience: people interested in dialogue and systems change.
```

### Use both tokens together

```
Generate assets for this conversation.

PARTICIPANTS
[[people]]

ORGANISATIONS
[[holons]]

Tone: conversational and inviting. Length: concise.
```

---

## Tips

- Tokens can appear in any of the 7 prompt sections, including Base Instructions.
- A token can appear more than once in the same section — it will be replaced each time.
- If the conversation has no connected holons, `[[holons]]` is replaced with an empty string (no error).
- Only non-empty fields are included in the expanded output. If a person has no description and no contact info, only their name will appear.
- Nested JSON values in the `infos` field are rendered as compact JSON (e.g. `locations: [1, 2, 3]`).
- The expanded context counts against the prompt token budget. If a conversation has many participants with extensive bios, monitor the token count logged at generation time.
