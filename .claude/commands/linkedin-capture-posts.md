---
description: Read one LinkedIn person's or company's posts back to a cutoff (default 12 months) and return them as dated records with their URLs
allowed-tools: Read, mcp__claude-in-chrome__tabs_context_mcp, mcp__claude-in-chrome__tabs_create_mcp, mcp__claude-in-chrome__navigate, mcp__claude-in-chrome__javascript_tool, mcp__claude-in-chrome__get_page_text
---

Read the posts on one LinkedIn activity feed (a person's or a company's) back to a cutoff and
return them as records: date, URL, kind (post or repost), author, text, reaction and comment
counts. Read-only: it never reacts, comments, follows, connects or messages.

This is a single-feed primitive, like `/linkedin-enrich-profile`. Callers that loop over
several people (e.g. work-life's `opportunity-research`) do the looping and the pacing.

All parsing lives in **`automation/linkedin-automation/scripts/linkedin-posts-extract.js`**
(tests: `linkedin-posts-extract.test.js`, run as described in its header). Inject that file
and call it; don't improvise selectors here. A fix goes into the script, with a test.

**Arguments:** `$ARGUMENTS`

```
<profile-or-company-url> [--months N | --since YYYY-MM-DD]
```

Default cutoff: 12 months back from today.

## Steps

1. **Browser context.** As in `/linkedin-enrich-profile` step 1: own tab, user already signed
   in (never log in), and the tab **must be visible**: check `document.visibilityState`
   before reading. A background tab renders an empty feed.
2. **Navigate** to the feed URL: `LinkedInPosts.activityUrl(url)` gives it
   (`/in/<slug>/recent-activity/all/` or `/company/<slug>/posts/?feedView=all`). Wait ~4 s.
3. **Inject** the script: `Read` it and pass its entire contents as one `javascript_tool`
   call, ending with `'loaded: ' + Object.keys(window.LinkedInPosts).length`.
4. **Collect**, repeating until the receipt says `done: true`:
   ```javascript
   JSON.stringify(await LinkedInPosts.collect(document, { reset: <true on the first call only>, months: 12 }))
   ```
   Each call scrolls for up to ~30 s (under the tool's ~45 s timeout) and resumes where the
   last one stopped. Pass `since: 'YYYY-MM-DD'` instead of `months` for a fixed cutoff.
5. **Read out**: `JSON.stringify(LinkedInPosts.writePayloadToDom(document))`, then
   `get_page_text`. The text must end with `<<<END n>>>` where n equals the receipt's
   `kept`; if it doesn't, the read was cut: reload, re-collect, and page through with
   `writePayloadToDom(document, { from: 0, count: 25 })`, then `from: 25`, and so on.
6. **Report** the receipt line, then the posts.

## Reading the receipt

- `mode: 'dom'`: posts came from `data-urn` cards; dates are exact (decoded from the URN).
- `mode: 'text'`: the fallback; no URLs, dates are approximate from the age label. Say so.
- `reachedCutoff: false, done: true`: the feed ended (or stopped loading) before the cutoff.
  Normal for someone who posts rarely; suspicious if `found` is 0 on an active account.
- `found: 0` with `visibility` not `visible`: the tab was in the background. Foreground it
  and retry before concluding anything.
- `undated` > 0 in DOM mode: a card without a decodable URN; keep it, flag the date as
  approximate.

## Limits

- One feed per call. When looping over feeds: tell the user how many feeds will be read
  first (a profile visit is visible to its owner), leave at least a minute between feeds,
  and keep a run to about 10 feeds.
- **Stop at once** on a security checkpoint, a CAPTCHA, a sign-in wall or two empty feeds in
  a row, and hand back to the user. Never try to get past one.

## Caveats (update after live runs)

- Written against LinkedIn's `data-urn="urn:li:activity:…"` cards and the
  "Feed post number N" text label used by `/linkedin-enrich-profile`. **Not yet validated
  live on company `/posts/` pages**; record what the first run finds here.
- Reposts carry the original post's date and author; the cutoff is decided by the feed
  owner's own posts only.
