---
description: Send a LinkedIn message to a single connection by profile URL
allowed-tools: mcp__claude-in-chrome__tabs_context_mcp, mcp__claude-in-chrome__tabs_create_mcp, mcp__claude-in-chrome__navigate, mcp__claude-in-chrome__javascript_tool, mcp__claude-in-chrome__computer
---

Send a LinkedIn message to a single existing connection.

Usage: `/message-person <profile-url> <message text>`

> **Debug mode is ON.** If any step fails or returns an unexpected result, stop immediately and report the exact error to the user. Do NOT try fallbacks, alternative approaches, or workarounds.

**Known quirks, confirmed in production runs:**
- `javascript_tool` frequently returns `{}` for the `new Promise(...).catch(e => e)` snippets below instead of the resolved string, even when the action genuinely succeeded. Treat `{}` as "unknown, go verify" — not as a failure. After any such call, make a separate plain (non-promise) `javascript_tool` call to check state directly, per the steps below.
- LinkedIn can have **multiple conversation panels docked** in `#interop-outlet`'s shadow DOM at once (minimized ones from earlier in the session). `shadow.querySelectorAll(...)` then returns more than one match, and the extra one(s) can be off-screen or oddly sized. Never act on the first match blindly — steps 6–8 below disambiguate explicitly.

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

This click can silently no-op — button found, `.click()` called, promise resolves, but no panel actually opens (observed on a real profile, reproducibly, across both `.click()` and a real mouse click). So don't trust the resolved value; verify directly:

```javascript
document.getElementById('interop-outlet')?.shadowRoot?.innerHTML.length || 0;
```

If a compose/conversation panel was already open before step 5 (e.g. from a prior person in this session), note that length now as a baseline *before* clicking Message, and compare — a truly new panel changes it. If step 6 below can't find a visible editor within two retries of step 5 (re-click, wait 2s, recheck), **stop and tell the user the Message button isn't responding — a page reload has fixed this before.** Do not loop indefinitely.

### 6. Wait for the compose editor, then pick the right one

LinkedIn renders the messaging panel inside a **shadow DOM** on `#interop-outlet`. Poll up to 10 seconds for at least one editor inside that shadow root:

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

Then — **regardless of what the above returned** — make a plain follow-up call to enumerate every match and its position, because a second, stale editor (from an earlier minimized conversation) is a common false match:

```javascript
const shadow = document.getElementById('interop-outlet').shadowRoot;
const boxes = Array.from(shadow.querySelectorAll('[contenteditable="true"][role="textbox"]'));
JSON.stringify(boxes.map((b,i) => { const r = b.getBoundingClientRect(); return {i, top:r.top, left:r.left, w:r.width, h:r.height}; }));
```

Pick the box whose `top` is within `[0, window innerHeight]` (i.e. actually on-screen) and whose `w` is around 440 — a stale/wrong box typically has `top` far below the viewport or an unusually narrow `w` (e.g. 141). If more than one box still looks plausible, take a screenshot to see which one is the visible "Write a message..." field for this profile, and use that index consistently in steps 7 and 8. If no box is found at all, **stop and report the error.**

If a fresh "New message" page opened instead of a docked panel (no existing thread), the composer is a `[contenteditable="true"]` inside `<iframe src=".../preload/?_bprMode=vanilla">` (`frame.contentDocument.querySelector(...)`), not in the shadowRoot — use that instead.

**This same shadowRoot — never the iframe — is also where any prior-message check must read from.** The iframe element persists across profile navigations in the same tab, so after a successful send its `contentDocument` can still hold the previous person's text even once you've moved to someone new. A duplicate-check against the iframe can therefore report "already messaged" for someone who wasn't. Read `document.getElementById('interop-outlet').shadowRoot.firstElementChild.innerText` for that check instead (see holon-outreach.md step 6c and linkedin-automation's General notes).

### 7. Type the message, then verify visually

Use `javascript_tool` to focus the correct editor (the index picked in step 6) and insert the message text. Replace `MESSAGE_TEXT_HERE` with the actual `message_text` value, properly escaped as a JS string literal, and `N` with the chosen index:

```javascript
const shadow = document.getElementById('interop-outlet').shadowRoot;
const boxes = Array.from(shadow.querySelectorAll('[contenteditable="true"][role="textbox"]'));
const el = boxes[N];
el.focus();
document.execCommand('insertText', false, MESSAGE_TEXT_HERE);
el.textContent.slice(0, 60);
```

The returned text confirms *something* got the text — it does NOT confirm it's the visible box. **Take a screenshot and visually confirm the message text is showing in the on-screen composer** (not empty, not a different conversation) before proceeding to step 8. If the composer still looks empty in the screenshot despite the JS reporting success, re-run step 6's enumeration — another index is the real one.

### 8. Click Send, scoped to this conversation only

Do not search the whole shadow root for a "Send" button — with multiple panels docked, that can find and click a **different conversation's** Send button with no error. Scope the search to the container around the confirmed-correct editor from step 7:

```javascript
const shadow = document.getElementById('interop-outlet').shadowRoot;
const boxes = Array.from(shadow.querySelectorAll('[contenteditable="true"][role="textbox"]'));
const el = boxes[N]; // same N as step 7
let container = el;
for (let i = 0; i < 8; i++) { container = container.parentElement; if (!container) break; }
const sendBtn = Array.from(container.querySelectorAll('button')).find(b => b.textContent.trim() === 'Send');
sendBtn ? (sendBtn.click(), 'clicked-send') : 'send-not-found';
```

If this returns `'send-not-found'`, **stop and report the error.** Otherwise, verify the send actually happened — don't trust the click alone:

```javascript
const shadow = document.getElementById('interop-outlet').shadowRoot;
const boxes = Array.from(shadow.querySelectorAll('[contenteditable="true"][role="textbox"]'));
boxes[N] ? boxes[N].textContent.length : 'gone';
```

A length of `0` means the composer cleared — the message sent. Confirm with a screenshot: the message should now appear as a delivered bubble in the thread. If the composer still holds the text, the send did not go through — **stop and report the error.**

### 9. Confirm

Report to the user: "Message sent to **{person_name}**."

## Pacing

A single message needs no delay. If you are messaging several people, use
`/message-connections`, which paces sends and keeps the messaged log — do not loop this
command manually without delays. See the **Pacing** section of
`.claude/skills/linkedin-automation/SKILL.md`, including the "Pacing from the agent loop"
subsection for how to actually wait between sends when you (the agent) are driving the loop
via Bash rather than in-page JavaScript.
