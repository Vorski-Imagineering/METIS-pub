# Getting Started — Navigating METIS

This orients a brand-new user in the METIS shell. Other guides link back here for the
navigation and place vocabulary rather than re-explaining it.

METIS is the platform The Gathering runs on: a CRM for people and organisations, plus
product apps built on top of it — **Coherence** (conversations and the IRIS publishing
pipeline), **The Gathering** (camps and local gatherings), **Audax** (quests and missions),
and **Outreach** (LinkedIn outreach). What you see depends on your access; not everyone has
every app.

> Some UI details below (exact labels, icons) are described from the app's structure. If
> anything doesn't match what you see, trust the app — layouts evolve.

---

## The strip and the band

Every page has the same two rows at the top.

**The strip** is the dark row across the very top:

- **The place switcher**, on the left, names the place you are in. Open it to go
  somewhere else. It lists **You** first, then **your places** (the holons you are a
  member of), then **All** (the globe). Places are important enough to have
  [their own guide](focus-and-scoping.md).
- **Search**, on the right, finds people and holons in your place (see below).
- **The bug icon** opens the form for reporting a bug or asking for a feature, in a new
  tab.
- **Your picture** opens your menu: your own profile, **Settings**, **Admin** (staff
  only) and **Log out**.

**The band** sits under the strip. It shows the place's picture, what kind of place it
is ("Organisation", "Local Gathering", "You", "All"), its name, and its **tabs**. The tab
you are on is underlined.

- **In a holon** the tabs start with **Overview**, the holon's own page. Then come
  **Feed** and **Calendar** (for people with broad edit rights), **People** and
  **Organisations** when the place has any, and one tab per app section the place holds,
  such as Camps, Quests or Conversations. A section with nothing in this place has no
  tab, and an app you have no access to has none either.
- **In You** the tabs are **Start** (your own page), **My actions** (if you use Audax)
  and **Outreach** (for people with broad edit rights).
- **In All** the tabs are the same as a holon's, without Overview, and each list shows
  everything you may see, in every place.

On a phone the tabs scroll sideways.

## Pages inside a place

Opening something from a tab, such as a quest from the Quests tab or a person from the
People tab, shows it as a **card** under the band. The band stays, and the tab the
record belongs to stays underlined. The card's top row says what it is and where, for
example "Quest in The Coherence Company › Quests". For a holon it also has:

- **History**, every change made to the record;
- **Go in →**, which makes that holon your place. The band becomes the holon's, on its
  Overview.

On a place's **Overview**, a gear at the band's top right opens the holon's
Configuration, and if you may edit the holon you can rename it in its name box (see
[Editing](#editing-fields-save-as-they-change)).

## Editing: fields save as they change

On a holon's page, a person's page, and the other edit screens (journeys and their steps,
classes, agents, a conversation's own page, an invitation page's settings), each field
you may edit is already open. There is no Save button: a field saves when you change it
or leave it (a text box when you click out of it or press Enter, a choice as soon as you
pick it, a picture as soon as you choose the file). Beside the field's name you then see
**Saved**, or **Not saved** with the reason under the field, for example "A name cannot
be empty." What you typed stays in the box, so you can correct it. Esc in a text box
puts back the last value saved.

- A field with several rows (links, contact details) saves as one field when you change,
  add, remove or move a row.
- A group of fields (a camp's chapter, a step's colours) saves together, with one
  **Saved** beside its heading.
- Changing a journey saves it at once with that journey's first step; pick another step
  and it saves again.
- **Making something new or sending something keeps its button**: creating a holon,
  adding a membership, sending an invitation, posting a comment, and the **Add note**
  button in a membership's or relationship's editor.
- The room editors of Coherence and Asks still save a whole room with one **Save**.
- A quick correction shows once in a holon's feed: the same field changed by the same
  person within five minutes is one line, from the first value to the last, and a change
  undone within five minutes shows no line. The **History** page still lists every save.

## Creating something

**+ Add** on a list (a person, an organisation, a quest, an event, a camp, …) and the
other create buttons ("Add a mission", "Create invitation page", …) open the create form
in the side panel on the right, with your list still beside it. Fill it in and press its
create button: the new person or holon then opens in the panel, and the list is where
you left it. Close the panel with its ✕ or **Cancel**. A form with a problem stays open
with the reason shown. Opening the button in a new tab (middle-click) still opens the
form as a page of its own. When the Chrome extension saves a new LinkedIn profile, METIS
opens on People (or Organisations) with that form filled in, in the side panel, ready to
review.

## Search

Search finds People and Holons (organisations, camps, events, …) by name. Results are
grouped by kind; pick one to jump to its detail page.

## Feed

The Feed is what has been happening (notes, updates) in your place. With **All**, it
spans everything you can see; in a holon, it is scoped to that holon.

## You › Start and You › Outreach

**Start** is your own page: your follow-ups, your runs through them, your camp's chapters
and, last, the events and organisations you are part of. With no place chosen, this is
where you land when you sign in.

**Outreach** is the people and organisations you are responsible for, from every place,
in one list. It is grouped by follow-up date under the headings **Overdue**, **Today**,
**Coming up** and **No follow-up date**, in that order.

## The organiser's blocks

If you are on the team of a Local Gathering that is not marked **Past**, METIS shows
blocks for organising it in two places:

- **The gathering's Overview** has the blocks about the gathering and its team, on top
  of the gathering's own sections (description, stage, people, camps). Its address is
  `/<gathering>/`.
- **You › Start** has the blocks about your own people: your follow-ups due and your runs
  through them.

**Which gathering** You › Start is about: your one active gathering. If you are on the team
of several, it asks you to **Pick a gathering**. A gathering's Overview shows these blocks
only to its own team.

On the gathering's Overview, from the top:

- **The banner** — the gathering's name, place and dates, a welcome, how many days until
  the village opens, and three counts: its camps, the camps with every chapter filled in,
  and the people on the gathering's journeys.
- **Since you were here** — in the banner, what changed in the gathering since you last
  opened its Overview: people moved on by someone else (grouped, as "Sanne moved 3 people
  to Invited"), camps that filled in a chapter, new people on the gathering's journeys,
  and comments others wrote on people you are responsible for. Your own moves and
  comments are not listed, nor METIS's own records (such as "Membership created"), nor
  private notes, nor a comment that names something you cannot open. It shows up to five
  lines, then how many more; each opens the board, camp or person it is about. Opening
  the Overview again within six hours is the same visit, so a reload keeps the list;
  after that, the next visit counts from your last look. On your first visit it says it
  will start counting from then. When an administrator views the page as you, your place
  is left as it was.
- **The team this week** — who moved how many people to which step in the last seven
  days.
- **What the team is working on** — a card for each person on the team (you first): the
  people they are responsible for, by journey and step, and how many follow-ups are
  overdue. Everyone on the team sees every card.
- **People on their way** — the gathering's three biggest journeys, each step with its
  count and how many are yours. A journey's name opens its board.
- **This week** — the gathering's week, Monday to Sunday in the gathering's own timezone
  (UTC when it has none), today marked, then **Coming up**. Each day shows how many
  follow-ups each person on the team has due that day (yours filled in, a teammate's
  outlined), the open Audax actions held by someone on the team that you can see (each
  with its quest's name, highest priority first; shown if you use Audax), and the day the
  gathering opens and closes. Follow-ups and actions whose date has passed move to today:
  one line per person, with how many are late and the earliest date. **Coming up** lists
  the next five actions and gathering dates after Sunday, up to 30 days ahead. On a phone
  the days stack one under another, and the days already past are left out (anything
  late is on today).
- **The camps** — every camp's hexagon and how many of its chapters are filled in.

The part METIS cannot show yet (tickets) shows in its place as **Coming soon**.

On You › Start:

- **Your follow-ups due** — up to five people on the gathering you are responsible for
  whose follow-up date has come, oldest first, as the same rows as the gathering's People
  list. Edit one in place; when its date moves on, it leaves the list without a reload.
- **One person at a time** — short runs through the same people, one card each. A run is
  offered only when it has someone in it:
  - **Due** — your follow-ups due today or earlier, oldest first (up to 10);
  - **Oldest** — those more than 30 days overdue (up to 5);
  - **First invites** — your people still at the first step of their journey, with no
    follow-up date (up to 10).

  **Start** opens the first card: who the person is, their journey and step, why they are
  on the run ("Follow-up was due 2 Oct"), the last shared note on them, how to reach them,
  and buttons to move them to one of the next steps (keys 1–3), give them a later date —
  3 days, 1 week or 2 weeks (key D) — or skip them (key S). Moving someone on also clears
  their follow-up date, since the follow-up is done; skipping changes nothing. A run's
  people are fixed when it starts, and its place is kept in the address, so a reload
  shows the same card. Someone a teammate moved meanwhile is passed over. At the end a
  recap says who moved on and to which step, who has a next date, how many you skipped
  and how many changed meanwhile; **Finish** returns to this page.

## Calendar

The Calendar shows dated items (for example, camp and gathering dates). It offers a list
view and a calendar view; what it shows depends on your place.

## Settings

There are two Settings pages: one for your own account, one for the system.

**Home › Settings** (`/settings/`, also in your picture's menu) is your own account: the
email you sign in with (and a box to change it), your password, your Telegram
connections, **Memory consent** (if you have Coherence) and the Chrome extension
download. Who you are — your name, contact details, the QR code to share them and which
apps you can use — is on **Profile**.

**All › Settings** (`/all/settings/`) is the system's settings, one section per app:
**Journeys**, **Classes**, **Apps directory**, **Podcasts**, **IRIS card gallery** and
**Agents** (each agent's configuration). Its tab shows at the end of All's row only for
someone it has a card for — the journey and class cards for people with broad edit
rights, Podcasts, the card gallery and Apps for staff, Agents for agent editors. Every
page a card opens keeps **Settings** underlined, so you always know where you are.

All's row also has an **Invitations** tab, for people with the Invitations app: every
sign-up page and every ask you can see, under the holon each belongs to.

See [Access and permissions](../../core/access-and-permissions.md) for why a card or tab
might not be visible to you.

## Reporting a bug or requesting a feature

The bug icon in the strip opens a form for bugs and feature requests, in a new tab. Use it
whenever something's broken or missing.

---

## Where to go next

- [Places: the holon scoping model](focus-and-scoping.md) — the one concept everything
  else assumes.
- [Working with people & orgs](../../metis_apps/metis/people-and-orgs.md) — the core CRM
  workflow.
- [Access and permissions](../../core/access-and-permissions.md) — why you can (or can't)
  see certain things.
