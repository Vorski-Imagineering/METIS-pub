---
description: Accept the first pending LinkedIn invitation and send them the message from texts/accept-invite.txt
allowed-tools: Read, mcp__claude-in-chrome__tabs_context_mcp, mcp__claude-in-chrome__tabs_create_mcp, mcp__claude-in-chrome__navigate, mcp__claude-in-chrome__javascript_tool, mcp__claude-in-chrome__find, mcp__claude-in-chrome__form_input, mcp__claude-in-chrome__read_page
---

Accept the first pending LinkedIn connection invitation and send them the message from `texts/accept-invite.txt`.

> **Debug mode is ON.** If any step fails or returns an unexpected result, stop immediately and report the exact error to the user. Do NOT try fallbacks, alternative approaches, or workarounds.

> **IMPORTANT:** You MUST accept the invitation before sending a message. LinkedIn does not allow messaging someone until they are a connection.

## Steps

### 1. Read the message text

Use the `Read` tool to read `{workspace}/texts/accept-invite.txt`. Hold the text in memory for use in step 7.

### 2. Get browser context

Use `tabs_context_mcp` to find available tabs. If there is no tab already on the LinkedIn invitation manager page, create a new tab with `tabs_create_mcp`.

### 3. Navigate to the invitation manager

Navigate to `https://www.linkedin.com/mynetwork/invitation-manager/received/` and wait for the page to load.

### 4. Extract the first invitee's name and save the Message link URL

**Before accepting**, use `javascript_tool` to get the name and save the Message link path. The Message link is a sibling element rendered outside the `[role="listitem"]` card div — search the full document:

```javascript
const cards = document.querySelectorAll('[role="listitem"]');
const firstCard = Array.from(cards).find(card => card.querySelector('button[aria-label*="Ignore"]'));
if (!firstCard) { JSON.stringify({ error: 'No invitation cards found' }); } else {
  const ignoreBtn = firstCard.querySelector('button[aria-label*="Ignore"]');
  const name = ignoreBtn.getAttribute('aria-label').replace('Ignore an invitation to connect from ', '');
  const messageLink = Array.from(document.querySelectorAll('a')).find(a =>
    a.href.includes('messaging') && a.querySelector('span') &&
    Array.from(a.querySelectorAll('span')).some(s => s.textContent.trim() === 'Message')
  );
  if (!messageLink) { JSON.stringify({ error: 'Message link not found', name }); }
  else {
    window._savedMsgHref = messageLink.href;
    JSON.stringify({ name, saved: true });
  }
}
```

If this returns an error, **stop and report the error to the user. Do not try alternatives.**

Note the `name` from the result. The href is stored in `window._savedMsgHref` for use in step 6.

### 5. Accept the invitation

Use `javascript_tool` to click the Accept button:

```javascript
const cards = document.querySelectorAll('[role="listitem"]');
const firstCard = Array.from(cards).find(card => card.querySelector('button[aria-label*="Ignore"]'));
const acceptBtn = firstCard?.querySelector('button[aria-label*="Accept"]');
if (acceptBtn) { acceptBtn.click(); 'accepted'; } else { 'accept button not found'; }
```

If this returns anything other than `'accepted'`, **stop and report the error. Do not try alternatives.**

Then use `javascript_tool` to poll until the specific person's Ignore button is removed from the DOM (confirming acceptance registered). Times out after 5 seconds. Replace `NAME_HERE` with the name from step 4:

```javascript
new Promise((resolve, reject) => {
  let elapsed = 0;
  const check = () => {
    const btn = document.querySelector('button[aria-label="Ignore an invitation to connect from NAME_HERE"]');
    if (!btn) return resolve('acceptance confirmed');
    elapsed += 200;
    if (elapsed >= 5000) return reject('timeout: card still present after 5s');
    setTimeout(check, 200);
  };
  check();
}).catch(e => e);
```

If this returns `'timeout: card still present after 5s'`, **stop and report. Do not try alternatives.**

### 6. Navigate to the messaging compose page

Use `javascript_tool` to navigate to the saved href (avoids query string blocking):

```javascript
if (window._savedMsgHref) { window.location.href = window._savedMsgHref; 'navigating'; } else { 'error: no saved href'; }
```

If this returns anything other than `'navigating'`, **stop and report. Do not try alternatives.**

### 7. Wait for editor and type the message

Use `javascript_tool` to poll for the compose editor to appear (up to 10 seconds), then type the message text from step 1:

```javascript
new Promise((resolve, reject) => {
  let elapsed = 0;
  const check = () => {
    const el = document.querySelector('.msg-form__contenteditable, [contenteditable="true"][role="textbox"], textarea[name="message"]');
    if (el) {
      el.focus();
      document.execCommand('insertText', false, MESSAGE_TEXT_HERE);
      return resolve('typed');
    }
    elapsed += 300;
    if (elapsed >= 10000) return reject('editor not found after 10s');
    setTimeout(check, 300);
  };
  check();
}).catch(e => e);
```

Replace `MESSAGE_TEXT_HERE` with the actual message text from step 1.

If this returns `'editor not found after 10s'`, **stop and report. Do not try alternatives.**

### 8. Send

 use `javascript_tool` to click Send:

```javascript
const sendBtn = document.querySelector('button.msg-form__send-button');
if (sendBtn && !sendBtn.disabled) { sendBtn.click(); 'sent'; } else { 'send button not found or disabled'; }
```

### 9. Confirm success

Report to the user: "Message sent to **{name}**."

## Notes

- The Message link is a sibling element rendered **outside** the `[role="listitem"]` card div — `card.querySelector('a[href*="messaging"]')` will always return null. Always search the full document.
- Save the Message link path **before** clicking Accept — after accepting, the card and its Message link are removed from the DOM.
- If any step fails, stop and report. Do not try alternatives.

## Pacing

A single acceptance needs no delay. If you are running this repeatedly, use `/accept-many`,
which paces the iterations — do not loop this command manually without delays. See the
**Pacing** section of `.claude/skills/linkedin-automation/SKILL.md`.
