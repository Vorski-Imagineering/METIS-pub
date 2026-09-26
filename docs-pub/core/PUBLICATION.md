# Publication: what the public site shows

Something is on the public site when **the relationship to its parent rests on a
publishing step, and its parent is on the public site too.**

That is the whole rule. Everything below is a consequence of it.

Before this, every gathering and every camp was on the public site simply by
existing. There was no way to see why something was there and no way to take it
off — which is how a camp nobody had decided to publish ended up on the site,
with nobody able to say what had put it there.

## The chain

Publication travels down the tree from the public site's own root holon:

    the site root  →  a gathering  →  a camp  →  an experience

Each link needs its own publishing step. A camp whose own relationship publishes
is still **not** public if its gathering is not public — the chain is only as
strong as its weakest link, and that is deliberate: taking a gathering off the
site takes everything under it off too, in one move.

Nothing is published by default. A kind of holon that has not been set up for
publication at all is never public, whatever its relationships say.

## How to publish something, and how to stop

Open the holon and find the **Public** section. It shows:

- whether it is on the public site right now;
- the chain, one row per link, with the journey and step each link rests on;
- **the first link that fails**, marked as the reason — the answer to "why is my
  camp not showing?";
- a link to the live public page when it is published.

To publish or unpublish, use **Change step** on that section. It opens the
relationship to the parent, and you move it to a step that publishes (or off
one). There is no separate "publish" button and no separate permission: if you
may edit that relationship, you may publish it, and if you may not, you cannot.

If the holon has no relationship to its parent yet, the section offers **Add
relationship** instead — until that relationship exists there is nothing for
publication to rest on, so the holon is not public.

## Which steps publish

A step publishes when it carries the `public-visible` setting. A journey can
carry it too, in which case **every** step of that journey publishes.

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

## People and organisations

People and organisations are not published directly. They are published by what
they are attached to:

- A **person** has a public profile when they hold a public role on something
  that is itself published. A person with no such role has no public page.
- An **organisation** has a public page when it is related to something published
  by a relationship that rests on a publishing step.

So taking a camp off the public site also removes the camp from the public pages
of the people and organisations attached to it. Their own pages stay up if they
are attached to something else that is still published.

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
