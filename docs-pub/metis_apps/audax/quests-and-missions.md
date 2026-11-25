# METIS App: Audax — Quests & Missions

Audax tracks bodies of work as **quests**, and the pieces of a quest as
**missions**. A quest is held by an organisation or an event; a mission
belongs to one quest. The work itself is **actions**, inside a quest or a
mission.

## Stages

Every quest and mission has its own stage. A quest moves through the
**Quest Journey** and a mission through the **Mission Journey**, each with
four steps:

| Step | Means |
|---|---|
| Planned | Named, not started yet. Where new quests and missions start. |
| Active | Being worked on. |
| Complete | Done. |
| Retired | No longer pursued, kept for the record. |

The stage belongs to the quest or mission itself, not to its link to the
holon above it. Moving a mission to another quest keeps its stage.

## Creating a quest or mission

- **Quests:** open **Quests**, choose **New**, give the quest a name and pick
  the organisation or event that holds it under **Held by**. The list offers
  only holons whose team you are on (or a team above them).
- **Missions:** open a quest and choose **Add a mission** in its Missions
  section.

Both forms have a **Step** picker, set to Planned. Pick another step if the
work is already under way.

Who may create one: the team of the holder (or of a holon above it).
Staff can change which kinds of holon may hold quests in each class's
**Allowed child classes**.

Organisation, event, camp and gathering pages list the quests they hold in a
**Quests** section, as the same cards the Quests page shows (below). Clicking
a mission there opens the Quests page with that mission's panel. **Add a
quest** there opens the quest form with that holder chosen.

## The Quests page

**Quests** in the Audax menu shows how each quest you can see is going, as one
card per quest, grouped under whoever holds it (the holder's logo, name, kind
and how many quests). Quests with no holder, or whose holder you cannot see,
are last, under **Without a holder**. There is no separate Missions page:
missions open from their quest's card, and the old Missions address lands
here.

A line at the top says how many quests are shown and how many of their actions
are overdue. Each card shows, top to bottom:

- the quest's name (cut short with "…" when long) and its stage;
- a progress bar and "<n> of <m> done", counting the actions of the quest and
  of its missions;
- one line per mission, with its own thin bar and "<done>/<total>";
- "<n> overdue" in red when any action is past its due date, and "Nothing
  moved in <n> days" when nothing has happened in the quest for more than 14
  days;
- **Next due**: the open action due first (in red when it is past), and who
  has it, or "Nothing due";
- the team's faces with **Team of <n>**, and when the quest last moved: the
  newest stage move, change or comment on the quest, its missions or their
  actions.

Above the cards:

- **All** and one tab per stage (Planned, Active, Complete, Retired), each
  with how many quests are on it;
- the **All / Mine** switch: **Mine** keeps the quests where you are
  responsible for an open action, in the quest or one of its missions;
- **Held by**, to show one holder's quests;
- **Portfolio | Board by stage**: the board is the quest board below.

The filters are in the page's address, so a reload or a shared link shows the
same cards.

**The mission panel.** Click a mission on a card to open its panel at the
right of the page (the whole screen on a phone); the address gains
`mission=<id>`, so a reload reopens it. The panel does not repeat the card. It
shows where the mission sits and **Open mission page**, its name and stage,
and **Goal:** with the start of its description (click it to read the rest).
**Needs attention** lists the mission's open actions that are past their due
date, each with its stage chip ("Overdue since <date> · <who>"), or says
"Nothing overdue."; pick another stage there and the panel redraws.
**Activity & comments** is the mission page's own stream and comment box: the
mission's moves, changes and comments together with its actions', newest
first, each action's line naming the action. **Comments** keeps only the
comments. A comment posted here is on the mission page too.

Every number, line and date on the cards and in the panel covers only what you
can see: a mission or action you cannot open changes none of them.

## The quest board

The Quests page's **Board by stage** opens the **Quest Journey** board: its
columns are Planned, Active, Complete and Retired, and every quest you can
see is a card in its own column. Drag a card to move the quest to another
stage. Only people who may edit that quest (its team, or a team above it)
can move it; anyone else is told so and the card stays where it was.

## Actions

An action is one piece of work in a quest or mission. Its name is its next
step: "Send the draft to Ana", not "Draft".

**Types and journeys.** Every action has a type. "Action" is always there;
staff can add others (a video review, say) as kinds of action in Django admin,
each with its own journeys. A type offers one or more journeys, and the action
moves through the steps of the one you choose. The default **Action journey**
has four steps:

| Step | Means |
|---|---|
| To do | Not started. Where new actions start. |
| Waiting | Paused on someone or something else. |
| Done | Finished. |
| Retired | Dropped, kept for the record. |

Done and Retired are marked **finished**: lists of open work leave finished
actions out. Staff set the mark in a step's settings.

**The quest's page.** At the top: the Audax mark, the quest's logo, a
**Quest** chip with the quest's own stage beside it (click it to pick another
stage, if you may edit the quest), the title and the description. Under them,
a progress bar counts the whole quest's actions, its own and its missions':
"<n> of <m> done", where done means on a finished stage (Done or Retired), and
"<n> overdue" in red when any are. Then the faces of the quest's team; **Team
of <n>** opens the Team tab. Under the header are four tabs:

- **Actions** (the default), with the number of open actions you can see;
- **Activity & comments**: the comment box and one stream holding the
  comments, stage moves and changes of the quest, its missions and their
  actions, each saying which one it was on. **Comments** keeps only the
  comments. Only what you may see is in it;
- **About**: Description, Stage, Responsible and Due date, each edited in
  place;
- **Team**: the people on the quest's team, with their number on the tab.

A mission's page is the same, with three tabs (no Team) and no team in its
header. The tab is in the page's address (`?tab=activity`), so a reload or a
link opens the same tab. There is no feed column beside the page.

**The borrowed logo.** A quest, mission or action with no logo of its own shows
the nearest logo above it that you may see, with a small quest, mission or
action icon in its corner, wherever its logo shows: its page, search results,
chips and lists. With none above it, it shows that icon. The logo itself is
not copied: give the holon its own logo and that one shows.

**The Actions tab.** It shows the actions as one outline. Two views, chosen
above the list:

- **By mission** (the default): the quest's own actions first, then one box
  per mission, by name. Each mission's box shows its stage, its own progress
  bar and count, and its description as the mission's goal (its editors edit
  it there). Inside a group, open actions come first, earliest due date first
  and undated last, then by name; finished actions end the group, struck
  through.
- **By due date**: the open actions only, under **Overdue**, **Today**, **Next
  7 days**, **Later** and **No date** (the same groups as My actions), each
  naming its mission.

The **All / Mine** switch (the same switch the Kanban and Calendar pages use)
and the **Journey** picker narrow the lines; the progress bars always count
everyone's actions. On a quest, **+ Mission** adds a mission, for those who
may. The view and the filters are in the page's address, so a reload or a
shared link shows the same list. A mission's page shows the same outline with
only that mission's actions.

Each action is one line: its stage chip (the journey's name, the stage, and
one dot per stage of the journey), its name, who is responsible, and its due
date, in red when it is past. Click the stage chip to pick another stage: the
menu lists the journey's stages with what each one means. Only someone who may
edit the action gets the menu.

**Changing an action's journey.** When the action's type offers more than one
journey, someone who may edit it sees a pencil beside its stage chip, and
beside **Stage** on the action's own page. It opens the **Journey** and
**Step** choice, with a **Journey info** panel showing each step's
description, entry criteria and goal. Only the journeys the action's type
offers are listed. Choosing a journey saves nothing; picking a step moves the
action to that journey and step at once, and its feed records the move with
the new journey's name.

Every count and every line covers only actions you can see: an action you
cannot open is never counted.

**Adding one.** At the end of the quest's group and of each mission's box,
pick a type, type the action's name and press **Enter**. It is added there at
once, at the type's first journey's first stage, with you responsible. Who may
add one: the team of the quest or mission, or of a holon above it.

**More options** opens the full form, which asks for:

- **Type**, then **Journey** (the type's journeys);
- **Name** and **Description**: a rich-text editor, so links go in the
  description. Actions hold no files;
- **Responsible**: you, to start with. The list holds only people who can edit
  the quest or mission (its team and the teams above it), so whoever is
  responsible can always move the action on. If someone is missing, the link
  under the list opens the quest's team, where its team can add them.

**The side panel.** Beside the list sits a panel that says "Pick an action
to see it here." Click an action's name to open it there (on a phone the panel
sits under the list). It shows **In
<quest or mission> ▾**, which moves the action to the quest or another of its
missions; its name, stage, **Responsible**, **Due date** and **Description**,
each saved as you change it; and the action's feed with its comment box.
**Open full page** opens the action's own page. The open action is in the
page's address too, so a link to it opens the panel.

**The action's page** is an ordinary holon page. Under its description it
shows **Stage**, **Responsible** and **Due date**, which anyone who may edit
the action can change there. The feed beside it shows everything that happened
to it: its creation, each move to another stage with who made it, changes of
responsible person and due date, a move to another mission, and comments.
Whoever can edit the action (its team, or a team above it) can add a comment in
the box under the feed; someone who can only see it gets no box. Quests and
missions get the same rows (in About), and the same history and comment box
in their Activity & comments tab.

Everything here can also be done through the API: see
[the API index](../../api/API.md). The holon notes list takes `rollup=true` to
return a quest's or mission's stream with its missions' and actions' notes and
moves, each naming the holon it was on (`holon_id`). `GET /api/v1/quests`
returns the Quests page's cards, built by the same code: per quest its holder,
stage, counts, next due action, last movement, team size and missions, with
the same `stage`, `who` and `held_by` filters.

## My actions

**My actions**, first in the Audax menu, lists the open actions you are
responsible for. An action is open until it reaches a stage marked finished
(such as Done or Retired). It lists only Audax actions, and only ones you can
see.

Three links group the list:

- **By calendar** (the default), by due date: **Overdue** (due before today),
  **Today**, **Next 7 days** (tomorrow to a week from today), **Later**, and
  **No date**. "Today" is the date in UTC.
- **By quest**: under the quest, or "Quest › Mission" for an action in a
  mission. Actions in a quest or mission you cannot see are under **Without a
  visible quest**, at the end.
- **By journey**: under the name of the journey each action runs.

Within a group, the earliest due date comes first and actions with no date
last, then high priority before normal and low, then by name. The grouping
is kept in the page address (`?group=quest`), so a reload or a shared link
shows the same view.

The API returns the same list, grouped the same way: `GET /api/v1/actions`,
with `group` (`calendar`, `quest` or `journey`), `responsible` (`me`, a
Person id, or `any`) and `parent_id` (one quest or mission). It returns at
most 100 actions and says when there are more.

## Who can see quests, missions and actions

Quests, missions and actions are private. You see one when you are on its team or
the team of a holon above it, or when you have been given rights to see
private holons.

For the shared concepts these build on, see
[Getting started](../../web/app/getting-started.md),
[Focus](../../web/app/focus-and-scoping.md), and
[Holons and classes](../metis/holons-and-classes.md).
