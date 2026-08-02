# LinkedIn Link Resolver

Finds the public link for each LinkedIn post this journey published, so that everything
downstream — participant emails, community broadcasts, anything added later — hands out a
link that works for people who are not signed into LinkedIn.

## Why this step exists

LinkedIn's API tells METIS a post's internal identifier and nothing else. The URL built
from it looks like this:

```
https://www.linkedin.com/feed/update/urn:li:share:7489628193746862080/
```

LinkedIn's own documentation describes that address as viewable *by an authorized member*.
Open it without a LinkedIn session and you meet the sign-in wall instead of the post. It is
the right link for reconciling what METIS published against what is on LinkedIn, and the
wrong link to put in an email asking someone to go and read it.

The link that works for everyone is the one LinkedIn's own **Copy link to post** produces:

```
https://www.linkedin.com/posts/the-coherence-company_startup-structure-…-activity-7489628196015910912-0RFz
```

No API returns it, and it cannot be worked out from the identifier METIS already has — it is
keyed on a different number. The only way to learn it is to read it off the published post's
own page, and LinkedIn often cannot serve that page for a few minutes after publishing. That
wait is what this step is for.

## Pipeline position

Runs after every LinkedIn publisher in the journey, and before anything that announces the
post. A journey that publishes to LinkedIn but omits this step — or places it out of that
order — will stop at the announcing step with an error saying which, rather than quietly
sending the member-only link or waiting forever for a step that can no longer run.

```
LinkedIn Page Publisher ─┐
                         ├─> LinkedIn Link Resolver ─> Publish Live Notifier
LinkedIn Member Publisher┘                          └─> Telegram Distributor
```

## What it produces

| Field | Filled from |
|---|---|
| **LinkedIn Public URL** | the Page post |
| **LinkedIn Public URL (member)** | the member post, if the journey publishes one |

Both appear on the conversation page alongside Title and LinkedIn Post, and both are
editable.

## Blocking behaviour, and how to clear it

This step **holds the pipeline until every published post has a public link**. That is
deliberate: an announcement is sent once, and a sign-in-walled link in it cannot be recalled.
There is no timeout.

Normally the wait is a few minutes and needs nothing from you. If LinkedIn still has not
provided a link after several hours, the step's message in the console changes to say so, and
the way out is manual:

1. Open the post on LinkedIn.
2. Use **Copy link to post** — or just copy the address bar once the post is open.
3. Paste it into the field the step's message names — **LinkedIn Public URL** for the Page
   post, **LinkedIn Public URL (member)** for the member post. They are separate posts with
   separate links; a link in the wrong box does not release the step.

Your edit outranks anything this step generates and is never overwritten, so pasting a link
both releases the pipeline and settles the matter permanently. If you paste the wrong link,
resetting this step clears the field — your edit included — and lets it resolve again. An
operator with shell access can instead run `python3 manage.py linkedin_public_urls --apply`,
which does the same lookup for every conversation missing one.

If the post is republished (its publisher step reset and re-run), the link is looked up
again: the stored one belongs to the previous post, which has usually been deleted.

## Step config fields

None. There is nothing to tune: the lookup is anonymous by design — it is asking what a
stranger sees — and the step blocks rather than giving up, so there is no timeout to set.

## Testing

`metis_apps/coherence/tests/test_linkedin_public_url.py` covers resolution, the wait while a
link is missing, an operator-supplied link releasing the step, and the refusal to accept a
canonical that is not a public post URL. No test contacts LinkedIn.
