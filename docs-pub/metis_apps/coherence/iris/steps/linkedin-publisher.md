# LinkedIn Page Publisher

Publishes the approved post to a **LinkedIn organisation Page**. One approved conversation
produces exactly one public Page post.

For posting as a *person* rather than a Page, see
[LinkedIn Member Publisher](linkedin-member-publisher.md). A journey may run either, both, or
neither.

## At a glance

| | |
|---|---|
| **Needs** | The approved LinkedIn copy, the video URL, a cleared consent gate, and a valid Page connection |
| **Produces** | A public LinkedIn post and its URL |
| **Waits when** | The consent gate hasn't cleared |
| **Re-running** | Safe after success — it makes no call at all. Some states refuse reset entirely |

## What it does

Posts the approved copy to the Page, with the video URL appended once (it won't duplicate a
URL already in the text). **The Page is the author.** Participants don't connect LinkedIn
accounts, don't install anything, and don't leave a browser running — they simply receive the
resulting public post URL afterwards so they can view and reshare it.

An earlier design tried to publish through each participant's own browser via the Chrome
extension. It could never actually complete, and it made a human-operated queue responsible
for a publication that has to be reliable. Any leftover queued actions from that design are
ignored by this step; cancel them in the outreach UI.

## The safety model

Publishing publicly is not undoable, so this step is deliberately cautious.

- **Consent is re-checked immediately before posting**, not just when the step started.
  Waiting means retry later; an opt-out is a permanent stop.
- **The record is written before the network call.** A rerun after a successful publish makes
  no HTTP call at all, and two workers can't both create a post.
- **Uncertain results never retry automatically.** LinkedIn's post creation has no way for a
  caller to say "this is the same request as before", so a timeout, a server error, or a
  response METIS can't interpret leaves the result **unknown** — a permanent stop needing a
  human to check LinkedIn. Retrying could publish the same thing twice, publicly, and that is
  worse than waiting for a person.
- **Reset is refused** while the result is submitting, unknown, or published — clearing
  METIS's record doesn't remove a LinkedIn post. Reset is allowed from failed or retryable.

```
absent ──checks pass──> submitting ──created──────────> published
                             ├─rejected──────────────> failed
                             ├─rate limited / pre-send> retryable ──> submitting
                             └─timeout / error ───────> unknown  (manual only)
```

## Settings

| Setting | Meaning |
|---|---|
| Page | Which Page to publish as. After **Connect LinkedIn**, this is a list of the Pages you administer — pick one. If the list could not be fetched, it falls back to a text field for the Page's API identity, `urn:li:organization:<numeric id>` — **not** the number in a `linkedin.com/company/...` URL |
| Author name | Display name, shown to operators and used to label the reshare link. Filled in from the selected Page; only editable when the Page was entered by hand |
| Access token | A LinkedIn token permitted to post as that Page. Never displayed, never logged. Set by the **Connect LinkedIn** button, or pasted in |
| Token expiry | Optional. Publishing fails before any network call once past it; a warning appears within 7 days |
| Max posts per run | How many posts this step may publish each time the schedule ticks. Blank means **all** — every approved conversation waiting here publishes at once. Anything over the limit is deferred to the next run, never skipped |
| Message template | Optional. Wraps the approved copy in your own text — branding, a call to action, extra links |

### Message template

Left blank (the default), the post is the approved copy with the video URL placed above its
trailing hashtags.

A template lets you add material *around* that copy. `{post}` is required and receives the
approved copy **unedited** — a template can never rewrite, trim, or reword what participants
approved, which is why the placeholder is mandatory rather than optional.

```
{post}

▶ Watch the full conversation: {video_url}

— The Coherence Company
```

`{video_url}` is optional and places the video link yourself. **When a template is set the URL
is no longer inserted automatically** — otherwise a template that positions its own link would
get it twice, in two places. If you want the link, put it in the template.

A template that omits `{post}`, or that uses an unrecognised `{placeholder}`, is refused when
you save — not at publish time, when a silently branded post with no conversation in it would
already be public.

**Connect LinkedIn** runs LinkedIn's consent flow and saves the token and its expiry. It also
looks up the Pages you administer: if there is exactly one and the step has no Page set yet, it
fills it in for you; if there are several the Page setting becomes a list to pick from. It never
changes a Page you have already set — reconnecting to refresh an expiring token cannot move
where the step publishes, so if the message says the Page it found differs from the one
configured, change it yourself in the step's config. When the lookup isn't available the Page
falls back to a text field you fill in yourself (and any list from a previous connection is
dropped, so you are never offered Pages the new token cannot use). LinkedIn doesn't issue most
apps a refreshable connection, so the connection expires (around 60 days) and has to be
reconnected the same way — which also refreshes the Page list.

If the LinkedIn app registration has no permission to list Pages at all, LinkedIn refuses the
whole consent screen rather than granting the rest. Connect notices that and immediately asks
again without the listing permission, so you still get a working publishing connection and fill
the Page in by hand.

## Checking a post before it goes out

The step inspector on a conversation has a **Preview post…** button. It shows the exact
commentary this conversation would publish — approved copy, video URL, and any template
branding — with its character count, plus everything that would stop the run (missing
credentials, an expired token, review not yet approved, an opt-out).

It **makes no call to LinkedIn**, and this is a real limitation rather than caution: publishing
relies on `w_organization_social`, a write-only scope. Connecting also asks for read permission
so it can list your Pages, but that is a convenience LinkedIn may decline and it does not
confirm posting rights either. There is no read endpoint to
confirm "this token can post as this Page" without actually posting, and LinkedIn accepts only
`PUBLISHED` when creating a post — there is no draft to send instead. So a clean preview means
*the copy and the configuration are right*; it is not proof the credentials work. The first
proof of that is the step running.

Available whatever the step's state. After a publish it shows what a *fresh* run would send,
which is what you need when reconciling an `unknown` record against what is actually on
LinkedIn.

## Troubleshooting

| Symptom | Likely cause | What to do |
|---|---|---|
| Waiting with no error | The consent gate hasn't cleared | Check the [Publish Notifier / Waiter](publish-notifier.md) steps |
| Permanently stopped, note mentions an opt-out | A participant opted out | Deliberate. Resolve it with them; there is no override |
| Error before any network call, mentioning expiry | The stored connection has expired | Click **Connect LinkedIn** on the step and reconnect |
| Error: rejected by LinkedIn | The token doesn't permit posting as that Page, or the author URN is wrong | Check the author URN is the organisation's API id, and that the token was granted for that Page |
| Result shows **unknown** | LinkedIn's response was inconclusive | **Do not retry.** Check the Page on LinkedIn: if the post is there, reconcile the record manually; if not, it can be republished deliberately |
| Nothing happened on a re-run after success | Working as designed — the record is a ledger | No action; a published conversation is never posted twice |
| Reset button refuses | The result is published, submitting, or unknown | Deliberate. Remove the post on LinkedIn first if that's the intent |
| Post appeared without the video link | The copy already contained the URL | The URL is only appended when it isn't already present |

## Technical reference

| | |
|---|---|
| **Step type** | `linkedin_publisher` |
| **Runs after** | `youtube_video_upload` (video URL), `publish_waiter` (consent) |
| **Feeds** | `linkedin_link_resolver`, and through it `publish_live_notifier`, `telegram_distributor` |
| **Reads** | `fields.linkedin_post`, `records.youtube.video_url`, `infos["publishing_status"]["state"]` (must be `approved`, re-read immediately before posting) |
| **Writes** | `records.linkedin.organization_post` — status, author URN and name, post URN, `post_url`, content hash, API version, request id, attempt count, timestamps, last error |
| **API** | LinkedIn's official Posts API; the dated API version is a project-wide constant, not a per-step setting |

`post_url` is required for a published result — the pipeline never notifies participants with
only an internal identifier, and no downstream step reconstructs a URL from one.

### Punctuation in the copy

LinkedIn's API does not take the post text as plain text: it parses it as a small markup
language in which `\ | { } @ [ ] ( ) < > # * _ ~` are reserved. The step escapes them for you
before publishing, so the copy publishes exactly as written — including asides in
parentheses, which unescaped would cause LinkedIn to silently drop the parenthesis and
everything after it while still reporting the post as created.

The one exception is a `#` that starts a hashtag (`#SystemsChange`): it is left as-is so it
still publishes as a hashtag. A `#` used any other way (`C#`, `#1`) is shown literally.

### Two URLs, and which one participants get

LinkedIn's API returns only the post's URN, and the URL built from it —
`https://www.linkedin.com/feed/update/urn:li:share:<id>/` — is what LinkedIn's own
documentation calls viewable "by an authorized member" — and someone opening it without a
LinkedIn session meets the sign-in wall rather than the post. That is `post_url`: the identity
link, correct for operators and for reconciliation, useless in an email asking people to go
and look.

The link a participant actually needs is the `https://www.linkedin.com/posts/…` permalink, the
one LinkedIn's own "Copy link to post" produces, which a signed-out visitor can read. No API
returns it, and this step does not look it up: that is
[LinkedIn Link Resolver](linkedin-link-resolver.md)'s only job, as its own step immediately
after this one. The lookup needs its own cadence — the publisher is scheduled slowly so it
cannot spam posts, and LinkedIn often cannot serve a new post's page for some minutes — and
its result is a dependency other steps must be able to see and wait on.

So `post_url` is what this step stores, and it is the identity link, not the link anyone is
sent. Nothing downstream announces the post until the resolver has written the public one;
that step holds the pipeline rather than letting a sign-in-walled link go out, and an
operator can release it by pasting the link in. Posts published before the resolver existed
still carry a `public_url` inside this record — the resolver adopts it rather than asking
LinkedIn again.
