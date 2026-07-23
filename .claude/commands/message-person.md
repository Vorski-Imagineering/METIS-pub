---
description: Send a LinkedIn message to a single connection by profile URL
allowed-tools: mcp__claude-in-chrome__tabs_context_mcp, mcp__claude-in-chrome__tabs_create_mcp, mcp__claude-in-chrome__navigate, mcp__claude-in-chrome__javascript_tool
---

Send a LinkedIn message to a single existing connection.

Usage: `/message-person <profile-url> <message text>`

> **Debug mode is ON.** If any step fails or returns an unexpected result, stop immediately and report the exact error to the user. Do NOT try fallbacks, alternative approaches, or workarounds.

## Steps

### 1. Parse arguments

Split `$ARGUMENTS` on the first whitespace:
- First token → `profile_url`
- Everything after the first token → `message_text`

If `profile_url` is empty or `message_text` is empty, stop and tell the user:

> "Usage: `/message-person <profile-url> <message text>`  
> Example: `/message-person https://www.linkedin.com/in/guyvankoolwijk/ Hey Guy, wanted to reach out!`"

### 2. Get browser context

Use `tabs_context_mcp` to find available tabs. Create a new tab with `tabs_create_mcp` if needed.

### 3. Navigate to the profile

Navigate to `profile_url` and wait for the page to load.

### 4. Extract the person's name

Use `javascript_tool` to read the name from the profile heading before clicking anything:

```javascript
const el = document.querySelector('h1, h2.text-heading-xlarge, .text-heading-xlarge');
el ? el.textContent.trim() : 'unknown';
```

Store this as `person_name` for the confirmation message.

### 5. Click the Message button

LinkedIn's Message action is an `<a>` tag, not a `<button>`. Use `javascript_tool` to poll up to 10 seconds for an `<a>` or `<button>` whose visible text is exactly "Message", then click it:

```javascript
new Promise((resolve, reject) => {
  let elapsed = 0;
  const check = () => {
    const btn = Array.from(document.querySelectorAll('a, button'))
      .find(el => el.textContent.trim() === 'Message');
    if (btn) { btn.click(); return resolve('clicked'); }
    elapsed += 300;
    if (elapsed >= 10000) return reject('Message button not found after 10s — person may not be a 1st-degree connection');
    setTimeout(check, 300);
  };
  check();
}).catch(e => e);
```

If this returns anything other than `'clicked'`, **stop and report the error.**

### 6. Wait for the compose editor

LinkedIn renders the messaging panel inside a **shadow DOM** on `#interop-outlet`. Poll up to 10 seconds for the editor inside that shadow root:

```javascript
new Promise((resolve, reject) => {
  let elapsed = 0;
  const check = () => {
    const shadow = document.getElementById('interop-outlet')?.shadowRoot;
    const el = shadow?.querySelector('[contenteditable="true"][role="textbox"]');
    if (el) return resolve('editor ready');
    elapsed += 300;
    if (elapsed >= 10000) return reject('editor not found after 10s');
    setTimeout(check, 300);
  };
  check();
}).catch(e => e);
```

If this returns anything other than `'editor ready'`, **stop and report the error.**

### 7. Type the message

Use `javascript_tool` to focus the shadow DOM editor and insert the message text. Replace `MESSAGE_TEXT_HERE` with the actual `message_text` value, properly escaped as a JS string literal:

```javascript
const shadow = document.getElementById('interop-outlet').shadowRoot;
const el = shadow.querySelector('[contenteditable="true"][role="textbox"]');
el.focus();
document.execCommand('insertText', false, MESSAGE_TEXT_HERE);
'typed';
```

If this returns anything other than `'typed'`, **stop and report the error.**

### 8. Click Send

The Send button is also inside the shadow root. Poll up to 5 seconds for it to be enabled, then click it:

```javascript
new Promise((resolve, reject) => {
  let elapsed = 0;
  const check = () => {
    const shadow = document.getElementById('interop-outlet').shadowRoot;
    const btn = shadow?.querySelector('button[type="submit"]') ||
      Array.from(shadow?.querySelectorAll('button') || []).find(b => b.textContent.trim() === 'Send');
    if (btn && !btn.disabled) { btn.click(); return resolve('sent'); }
    elapsed += 300;
    if (elapsed >= 5000) return reject('send button not found or disabled after 5s');
    setTimeout(check, 300);
  };
  check();
}).catch(e => e);
```

If this returns anything other than `'sent'`, **stop and report the error.**

### 9. Confirm

Report to the user: "Message sent to **{person_name}**."

## Pacing

A single message needs no delay. If you are messaging several people, use
`/message-connections`, which paces sends and keeps the messaged log — do not loop this
command manually without delays. See the **Pacing** section of
`.claude/skills/linkedin-automation/SKILL.md`.
