---
description: Message existing LinkedIn connections who haven't been messaged yet
allowed-tools: Read, Write, Grep, mcp__claude-in-chrome__tabs_context_mcp, mcp__claude-in-chrome__tabs_create_mcp, mcp__claude-in-chrome__navigate, mcp__claude-in-chrome__javascript_tool, mcp__claude-in-chrome__find, mcp__claude-in-chrome__form_input, mcp__claude-in-chrome__read_page
---

Message **$ARGUMENTS** existing LinkedIn connections who haven't been messaged yet, using the message from `texts/accept-invite.txt`.

> **Debug mode is ON.** If any step fails or returns an unexpected result, stop immediately and report the exact error to the user. Do NOT try fallbacks, alternative approaches, or workarounds.

## Steps

### 1. Parse arguments

Parse `$ARGUMENTS` as an integer `N`. If it is missing, not a number, or less than 1, stop and tell the user: "Please provide a number, e.g. `/message-connections 3`."

### 2. Read the message text

Use the `Read` tool to read `/Users/vvorski/dev/auto-li/texts/accept-invite.txt`. Hold the text in memory for use when typing.

### 3. (No pre-loading of log needed)

Do not read `messaged-log.txt` upfront. Instead, check it on demand in step 7a using `Grep`.

### 4. Get browser context

Use `tabs_context_mcp` to find available tabs. If there is no tab already on the LinkedIn connections page, create a new tab with `tabs_create_mcp`.

### 5. Navigate to the connections page

Navigate to `https://www.linkedin.com/mynetwork/invite-connect/connections/` and wait for the page to load.

### 6. Extract connection cards

The connection cards use Message **links** (`<a>` tags with `href*="messaging"`), not buttons. Each card has two profile links: the first is the avatar (image only), the second contains a `<div>` whose first child element (`<p>`) holds the name text.

Use `javascript_tool` to poll until connection cards appear (up to 10 seconds), then extract all visible connections and store Message link references on `window`:

```javascript
new Promise((resolve, reject) => {
  let elapsed = 0;
  const check = () => {
    const msgLinks = document.querySelectorAll('main a[href*="messaging"]');
    if (msgLinks.length > 0) {
      const allMsgLinks = Array.from(msgLinks);
      window._msgLinks = allMsgLinks;
      const results = allMsgLinks.map((msgLink, i) => {
        let card = msgLink;
        for (let j = 0; j < 8; j++) { card = card.parentElement; if (card.querySelectorAll('a[href*="/in/"]').length > 0) break; }
        const profLinks = Array.from(card.querySelectorAll('a[href*="/in/"]'));
        const nameLink = profLinks.length > 1 ? profLinks[1] : profLinks[0];
        const profileUrl = nameLink ? nameLink.href.split('?')[0] : '';
        const outerDiv = nameLink ? nameLink.querySelector('div') : null;
        const nameEl = outerDiv ? outerDiv.firstElementChild : null;
        const name = nameEl ? nameEl.textContent.trim() : '';
        return { index: i, name, profileUrl };
      });
      window._connections = results;
      return resolve(JSON.stringify(results));
    }
    elapsed += 500;
    if (elapsed >= 10000) return reject('no connection cards found after 10s');
    setTimeout(check, 500);
  };
  check();
}).catch(e => e);
```

If this fails, **stop and report**. Use `read_page` with `filter: "interactive"` to inspect the page structure and adapt selectors. If you still can't find cards after one adaptation attempt, stop and report.

### 7. Process connections one by one

Initialize a counter `sent = 0` and an index `i = 0` into the connections list. For each connection:

#### 7a. Check the messaged log

Use `Grep` to search for the connection's `profileUrl` in `/Users/vvorski/dev/auto-li/messaged-log.txt`. If the file doesn't exist or the URL is not found, proceed. If found, skip this connection. Print: `Skipping {name} (already in log)`. Do NOT count toward N. Move to next.

#### 7b. Navigate to the messaging page

The Message element is an `<a>` link, not a button. Use `javascript_tool` to navigate via `window.location.href` using the stored link reference:

```javascript
window.location.href = window._msgLinks[INDEX].href;
'navigating';
```

Replace `INDEX` with the current card index.

If this fails, **stop and report.**

#### 7c. Wait for messaging editor to load

Use `javascript_tool` to poll for the messaging editor (up to 10 seconds):

```javascript
new Promise((resolve, reject) => {
  let elapsed = 0;
  const check = () => {
    const el = document.querySelector('.msg-form__contenteditable, [contenteditable="true"][role="textbox"], textarea[name="message"]');
    if (el) return resolve('editor ready');
    elapsed += 300;
    if (elapsed >= 10000) return reject('editor not found after 10s');
    setTimeout(check, 300);
  };
  check();
}).catch(e => e);
```

If this fails, **stop and report.**

#### 7d. Check if conversation is empty

Use `javascript_tool` to check for existing messages in the thread:

```javascript
(() => {
  const msgs = document.querySelectorAll('.msg-s-message-list__event, .msg-s-event-listitem, li.msg-s-message-list-item');
  return JSON.stringify({ messageCount: msgs.length, empty: msgs.length === 0 });
})();
```

- If `empty` is `false` (messages exist): this person was messaged before the log existed. Append their profile URL to `messaged-log.txt` using the `Write` tool (append mode — read the file, add the URL on a new line, write it back). Print: `Skipping {name} (existing conversation)`. Do NOT count toward N. Close the messaging panel and continue.
- If `empty` is `true`: proceed to type and send.

**To return to the connections page** (when skipping or after sending), navigate back to the connections URL and re-extract cards (repeat step 6). The `window._msgLinks` references will be stale after navigation, so they must be rebuilt.

#### 7e. Type the message

Use `javascript_tool` to type the message:

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

Replace `MESSAGE_TEXT_HERE` with the actual message text from step 2, properly escaped as a JS string literal.

If this fails, **stop and report.**

#### 7f. Click Send

Use `javascript_tool`:

```javascript
new Promise((resolve, reject) => {
  let elapsed = 0;
  const check = () => {
    const sendBtn = document.querySelector('button.msg-form__send-button');
    if (sendBtn && !sendBtn.disabled) { sendBtn.click(); return resolve('sent'); }
    elapsed += 300;
    if (elapsed >= 5000) return reject('send button not found or disabled after 5s');
    setTimeout(check, 300);
  };
  check();
}).catch(e => e);
```

If this fails, **stop and report.**

#### 7g. Log and report

Append the connection's profile URL to `/Users/vvorski/dev/auto-li/messaged-log.txt` (read file, append URL on new line, write back). If the file doesn't exist yet, create it with just this URL.

Increment `sent`. Print: `[{sent}/{N}] Message sent to **{name}**.`

#### 7h. Navigate back and continue

Navigate back to `https://www.linkedin.com/mynetwork/invite-connect/connections/` and re-run the extraction from step 6 to rebuild `window._msgLinks` and `window._connections`. Then continue processing from the next connection (matching by profile URL to find where you left off, since card order may shift between page loads).

### 8. Handle pagination / lazy-loading

If you exhaust all visible connection cards before reaching N sent messages, scroll to the bottom of the page to trigger lazy-loading:

```javascript
window.scrollTo(0, document.body.scrollHeight);
'scrolled';
```

Then wait 2 seconds and re-extract connection cards (repeat step 6). Continue processing new cards. If no new cards appear after scrolling, stop and report how many were sent vs. requested.

### 9. Final summary

When `sent` reaches N, print: `Done — sent messages to {sent} connections: {name1}, {name2}, ...`

## Notes

- The messaged log file (`messaged-log.txt`) is append-only, one LinkedIn profile URL per line.
- Skipped connections (already in log or with existing conversations) do NOT count toward N.
- Use the same Promise-based polling pattern as accept-one — no `await`, no `sleep`.
- If any step fails, stop and report the exact error. Do not try alternatives.

## Pacing — required between messages

Sending messages in a tight loop gets accounts restricted, and it reads as spam to the
recipients. **After each message is confirmed sent, wait before starting the next
connection:**

```javascript
const humanDelay = (meanMs, minMs, maxMs) => {
  // Shifted exponential. Do NOT clamp at the minimum instead: clamping puts ~30%
  // of draws on the exact same value, which is itself a machine fingerprint.
  const scale = Math.max(1, (meanMs - minMs) / 1.2);
  let d = minMs - scale * Math.log(1 - Math.random());
  if (Math.random() < 0.1) d += -scale * 2 * Math.log(1 - Math.random());  // distracted
  return Math.min(maxMs, Math.round(d));
};
await new Promise(r => setTimeout(r, humanDelay(90000, 40000, 600000)));  // 90 s mean
```

After every 8–15 messages (re-randomise the threshold), take a longer break of 2–10 minutes:
`humanDelay(300000, 120000, 600000)`.

**Announce every long break before it starts**, with its length and the current position:

```
[8/25] Taking a 4 min break to stay within LinkedIn's limits — resuming after.
```

Do not announce the short 90-second waits between messages; the `[{sent}/{N}]` lines already
show the run is alive.

**Before sending the first message**, tell the user roughly how long N will take — at ~90 s
apiece plus breaks, 25 messages is about an hour. Because the log is written per message, a
stopped run resumes cleanly, so prefer stopping early over pushing through. See the
**Pacing** section of `.claude/skills/linkedin-automation/SKILL.md`.
