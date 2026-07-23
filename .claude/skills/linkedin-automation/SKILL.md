---
name: linkedin-automation
description: >
  LinkedIn automation workflows for accepting connection invitations, messaging connections,
  listing pending invites, extracting people search results to a Google Sheet or a JSON file,
  and sending connection requests from a Google Sheet. Use this skill whenever the user wants
  to do anything with LinkedIn — accepting invites, bulk accepting, messaging connections,
  checking pending invitations, scraping search results to a spreadsheet, capturing a filtered
  people search by keyword/location/degree, or sending outreach connection requests from a
  spreadsheet.
  Trigger on phrases like: "accept LinkedIn invites", "message my connections", "check my pending invitations",
  "how many invites do I have", "save LinkedIn search results", "bulk accept", "send connection requests
  from my sheet", "connect with people in the spreadsheet", "search LinkedIn for people in
  <place>", "find my connections in <place>", "capture this LinkedIn search", or any
  request involving LinkedIn connection management or outreach automation.
---

# LinkedIn Automation

This skill automates LinkedIn connection management and outreach using the Chrome browser connector.
All workflows require the Chrome extension to be active with a LinkedIn session open.

## Workspace paths

All file operations use paths relative to the user's workspace folder. Resolve the actual mounted path for that folder at the start of each session — do not hardcode session-specific paths.

- **Message template**: `{workspace}/texts/accept-invite.txt`
- **Messaged log**: `{workspace}/messaged-log.txt`

## Workflow routing

Read the user's message and pick the right workflow:

| Intent | Command file |
|---|---|
| "List / show my pending invitations" | `{workspace}/.claude/commands/invites.md` |
| "Accept one invitation" | `{workspace}/.claude/commands/accept-one.md` |
| "Accept N invitations" / "bulk accept" | `{workspace}/.claude/commands/accept-many.md` |
| "Message N connections" | `{workspace}/.claude/commands/message-connections.md` |
| "Search LinkedIn / extract search results to a Google Sheet" | `{workspace}/.claude/commands/search-to-sheet.md` |
| "Search LinkedIn people by keyword / location / degree and capture the results" | `{workspace}/.claude/commands/linkedin-search-capture.md` |
| "Find a person's LinkedIn URL by name" / "fill empty LinkedIn column" | `{workspace}/.claude/commands/linkedin-find-person.md` |
| "Send connection requests from a spreadsheet / sheet" | `{workspace}/.claude/commands/connect-from-sheet.md` |

Read the appropriate command file before starting work.

## General notes

- **Debug mode is always ON.** If any step fails, stop immediately and report the exact error. Do not try fallbacks or workarounds.
- LinkedIn uses obfuscated CSS class names — prefer `aria-label`, `role`, and text content to locate elements.
- Use Promise-based polling (not `await` or `sleep`) for all wait loops.
- Always use `tabs_context_mcp` first to get a valid tab ID before any browser operations.
