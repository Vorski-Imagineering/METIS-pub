# Publication: what the public site shows

Something whose parent can be on the public site — a gathering's camp, a camp's
experience — is on the public site when **its parent is, and its relationship to
that parent rests on a step that publishes.** Anything else — something with no
parent, such as an organisation, or something whose parent can never be public,
such as a Coherence event under a tenant — is on the public site when a
publishing relationship connects it to something public.

That is the whole rule. Everything below is a consequence of it.

Before this, every gathering and every camp was on the public site simply by
existing. There was no way to see why something was there and no way to take it
off — which is how a camp nobody had decided to publish ended up on the site,
with nobody able to say what had put it there.

## The parent decides

Publication spreads outward from the public site's own root holon, down the tree
along relationships that rest on a publishing step:

    the site root  →  a gathering  →  a camp  →  an experience

Something whose parent can be on the public site gets its own public page only
through that parent. Its other relationships — to an organisation, to another
gathering — can list it on another public page while it is published, but they
never put it on the site. So **cancelling a camp's relationship to its
gathering, or deleting it, takes the camp and its experiences off the site**,
whatever else links to them, and taking a gathering off the site takes
everything under it off too. Which way round the relationship was created
carries no meaning.

Anything else — something with no parent, such as an organisation, or
something whose parent can never be public, such as a Coherence event under a
tenant — is public when a relationship resting on a publishing step connects it
to something public: a published camp,
a published gathering, the site itself.

Nothing is published by default. A kind of holon that has not been set up for
publication at all is never public, whatever its relationships say.

## How to publish something, and how to stop

Open the holon, go to **Configuration**, and find **Where this appears**. It
shows:

- whether it is on the public site right now;
- every relationship that bears on it, one per row, with the journey and step
  each rests on, and whether that step publishes;
- for each row, whether the holon at the other end is itself public;
- a link to the live public page when it is published.

There is no single "the reason" row any more, because there is no single chain.
The reason lives on the other holon's own page, one click away, where the same
section answers the same question about it — so every other end is a link.

To publish or unpublish, use **Change step**. It opens the relationship and you
move it to a step that publishes (or off one). There is no separate "publish"
button and no separate permission: if you may edit that relationship, you may
publish it, and if you may not, you cannot.

When something with a parent is off the site because of that parent, the section
says so in one sentence naming the parent: it has no relationship to it, its
relationship to it rests on a step that doesn't publish (with **Change step** on
that relationship), or the parent itself is not on the public site.

## Which steps publish

A step publishes when it carries the `public-visible` setting. A journey can
carry it too, in which case **every** step of that journey publishes.

On a Coherence conversation journey, the same setting makes a conversation
listable on the room's public video page: a conversation is listed there when
its event is on the public site and it rests on a step marked **Public** (or
its whole journey is marked). Until a team marks a step, the journey is not
shown there at all. Only participants who are themselves on the public site
are named with the conversation. See the
[Coherence API's public lists](../api/coherence-PLAYBOOK.md#authentication).

Wherever a step is shown — a kanban column, a journey's step list, a step
picker, a roster row — a publishing step carries the same globe chip. A kanban
column that publishes is marked, and moving a card onto or off it warns you that
the card is joining or leaving the public site before the move happens.

⚠️ **The setting belongs to the step, not to one holon.** Putting
`public-visible` on a step of a journey that many holons share publishes
*everything* resting on that step — including things you were not thinking about
when you set it. On a shared journey, prefer marking one specific step; use the
journey-level setting only when the entire pipeline is genuinely public.

The journey editor shows a count of how many things are published through each
step, so you can see the size of what a step is publishing before changing it.

## People, organisations and events

People, organisations and Coherence events are not published directly. They are published by what
they are attached to:

- A **person** has a public profile when they hold a public role on something
  that is itself published.
- A **person** also has a public profile when they appear in a Coherence
  conversation whose video has been made public on YouTube. Making the video
  private again, or removing them from the conversation, takes the profile down.
- An **organisation** has a public page when it is related to something published
  by a relationship that rests on a publishing step. An organisation that is not
  linked to a published camp can be published from The Gathering's page:
  **Related Organisations → Add relationship**, on a publishing step.

- A **Coherence event** that belongs to a company is public when the company is
  public and the event's relationship to that company rests on a publishing
  step. An event whose owner can never be public (a tenant) is made public as
  before: open **The Gathering**, go to **Events → Connect event**, pick the
  event, and choose the "Public Event" journey's "Public" step. It is never published just because one
  of its conversations has a public video. Its page shows its conversations whose
  video is public, the dates they span, its hosts and, when that is itself
  public, what it belongs to. Hosting a published event is a public role, so it
  gives the host a public profile, and that profile lists the event under
  "Events" — as does the profile of anyone in one of its public videos.

So taking a camp off the public site also removes the camp from the public pages
of the people and organisations attached to it. Their own pages stay up if they
are attached to something else that is still published — the rule for anything
whose parent cannot decide it, above.

## What a visitor sees

A page for something that is not published returns **not found**, exactly as if
it had never existed — on the public site and in the public data feeds alike.
Guessing a web address does not reveal anything: "nothing links to it" was never
a way of keeping something private, and it is not one now.

Lists follow the same rule, so nothing unpublished is named, linked, or counted
anywhere a visitor can reach — including the site's own navigation.

## Share links

A **share link** keeps working for a person who is not published. A share link is
something its owner deliberately handed out, so it is honoured on its own terms
rather than through publication. It is the one carve-out from the rule above, and
it applies only to links that were explicitly created to be shared.
