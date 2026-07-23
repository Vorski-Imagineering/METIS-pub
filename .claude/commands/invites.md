---
description: Read LinkedIn invitation manager page and extract all pending invitation names
allowed-tools: mcp__claude-in-chrome__tabs_context_mcp, mcp__claude-in-chrome__tabs_create_mcp, mcp__claude-in-chrome__navigate, mcp__claude-in-chrome__javascript_tool, mcp__claude-in-chrome__read_page
---

Extract all pending LinkedIn connection invitations from the invitation manager page.

## Steps

1. **Get browser context** using `tabs_context_mcp` to find available tabs.

2. **Navigate to the LinkedIn invitation manager** at `https://www.linkedin.com/mynetwork/invitation-manager/received/` (create a new tab if needed).

3. **Wait for page load** (~2.5s), then use `javascript_tool` to extract invitation data. Use this script:

```javascript
const cards = document.querySelectorAll('[role="listitem"]');
const invitations = Array.from(cards).map(card => {
  const ignoreBtn = card.querySelector('button[aria-label*="Ignore"]');
  if (!ignoreBtn) return null;
  const name = ignoreBtn.getAttribute('aria-label').replace('Ignore an invitation to connect from ', '');
  const profileLink = Array.from(card.querySelectorAll('a[href*="/in/"]')).find(a => a.textContent.trim().length > 0);
  const profileUrl = profileLink?.href || null;
  return { name, profileUrl };
}).filter(Boolean);
// Total comes from the filter nav link "All (N)" — NOT the first span on the page.
const navLink = Array.from(document.querySelectorAll('nav a')).find(a => /^All \(\d+\)$/.test(a.textContent.trim()));
const total = navLink ? parseInt(navLink.textContent.trim().match(/\((\d+)\)/)[1]) : null;
JSON.stringify({ total, loaded: invitations.length, invitations });
```

4. **Try to load more (best-effort)**: The invitation list is lazy-loaded inside the `<main>` element — **not** the window, and there is **no "Load more" button** anymore. If `loaded < total`, attempt to load more by scrolling the `<main>` scroll container to its bottom until the count stops increasing:

```javascript
new Promise(async (resolve) => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const main = document.querySelector('main');
  const count = () => document.querySelectorAll('[role="listitem"] button[aria-label*="Ignore"]').length;
  let prev = -1, stable = 0;
  for (let i = 0; i < 25 && stable < 4; i++) {
    if (main) main.scrollTo(0, main.scrollHeight);
    await sleep(1000);
    const c = count();
    if (c === prev) stable++; else { stable = 0; prev = c; }
  }
  resolve(JSON.stringify({ loaded: count() }));
});
```

Then re-run the step 3 extraction script to capture whatever loaded.

> **Known LinkedIn limitation (verified 2026-06):** the `/received/` view often renders only the first ~10 invitations and will not load the rest in-page — scrolling does nothing and the `/received/ALL/` URL just redirects back to `/received/`. Do **not** loop forever or claim you fetched everything. If `loaded < total` after the scroll attempt, report honestly (see step 5).

5. **Report results** to the user as a numbered list with name and profile URL for each loaded invitation. At the top, state the count honestly:
   - If `loaded === total` (or `total` is null): "You have **N** pending invitations:"
   - If `loaded < total`: "Showing the **{loaded}** invitations LinkedIn rendered on this page (you have **{total}** total — LinkedIn doesn't load the rest on this view):"

## Key page structure details

- Each invitation card is a `div[role="listitem"]`
- The **Ignore** button `aria-label` contains the inviter's full name in the format: `"Ignore an invitation to connect from {Name}"`
- Profile links match `a[href*="/in/"]` - the one with text content holds the display name
- The total count lives in the filter **nav link** `"All (N)"` (`nav a`), **not** in an arbitrary `span`. `document.querySelector('span')` returns the wrong element and yields `null`.
- The list scrolls inside the `<main>` element (overflow-y auto), not the window — `window.scrollTo` has no effect.
- There is **no "Load more" button**, and the `/received/` view caps the inline list at ~10 invitations.

## Pacing

This command is read-only and loads a single page, so it needs no inter-action delay. If you
follow it with acceptances, pace those — see the **Pacing** section of
`.claude/skills/linkedin-automation/SKILL.md`.
