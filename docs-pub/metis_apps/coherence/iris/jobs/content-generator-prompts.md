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
| LinkedIn Post — Host | Post written from the host's perspective |
| LinkedIn Post — Guest | Post written from the guest's perspective |
| Quotes | Selection criteria for pull quotes used in cover images |

---

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
