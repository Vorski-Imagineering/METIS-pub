# Access & Permissions: Who Can See and Do What

This page explains access in everyday terms: what you can see, what you can change, why
something is missing or refused, and who to ask. For the full rules and the admin setup,
see [Permissions and roles](PERMISSIONS.md).

---

## The short version

- **You can see almost everything.** Once you are signed in you can read holons, people
  and relationships, except a few private kinds of holon (below) and internal notes.
- **You can change what your team owns.** If you are on the team of a holon, you can edit
  that holon and everything inside it.
- **Apps are opened one by one.** Coherence, The Gathering, Outreach, Audax and Invitations
  each need you to be added to that app.
- **Access is given by an administrator.** There is no "request access" button; you ask a
  person.

---

## Three things decide what you can do

### 1. Which apps you can open

Each app has its own list of people who may use it. If you are not on the list, the app
does not appear in your sidebar, and opening one of its pages tells you that your account
is not in the group for that app.

| App | Opens for |
|---|---|
| METIS (people, holons, relationships) | Everyone who is signed in |
| Coherence | People added to Coherence |
| The Gathering | People added to The Gathering |
| Outreach | People added to Outreach |
| Audax | People added to Audax |
| Invitations | People added to Invitations |

Nobody gets an app automatically, administrators included. Being able to open an app is a
door, not a permission: what you can change inside it still depends on your team rights.

Your profile page has an **App Access** panel showing which apps you have.

### 2. Which holons you are on the team of

Most editing rights come from being on a holon's team. You are on the team when you are
one of its people **and** you sit at a step of its journey that carries team rights (for
example *Member* or *Active*; earlier steps such as *Invited* usually carry none).

A step can carry up to four rights. In practice the first three are almost always given
together:

| Right | What it lets you do |
|---|---|
| **Team member** | Edit the holon's details, pictures and info fields. Add, move and remove its people. Add and edit its relationships. Create holons inside it. Read and write its notes. See it even if it is private |
| **Manage people** | Edit the profile of anyone who belongs to the holon |
| **View private** | See a private holon without being able to change it |
| **Manage logins** | Create a login or reset a password for people in the holon. Rarely given |

**Rights flow downward, never upward or sideways.**

- *Downward:* on the team of a gathering, you can also edit its camps and the experiences
  inside those camps.
- *Not upward:* on the team of one camp, you cannot edit the gathering it belongs to, or
  the other camps.
- *Not sideways:* if your holon is **linked** to an organisation (a relationship), you can
  edit the link itself, but not the organisation, and you cannot add people to it.

### 3. Whether you are a global editor

A small number of people are **global editors**. They can edit every holon and person,
see private holons, and manage journeys. Only full administrators can delete holons or
people.

---

## What you can do, by task

| I want to… | You can if… |
|---|---|
| Look at a holon or a person | You are signed in, and the holon is not a private kind |
| Read or write a holon's notes | You are on that holon's team (or the team of a holon above it) |
| Edit a holon | You are on its team, or the team of a holon above it |
| Add someone to a holon, move them along its journey, or remove them | You are on that holon's team, or the team of a holon above it |
| Add a new person | You are on the team of any holon, with the *Manage people* right |
| Edit a person's profile | It is your own profile, or the person belongs to a holon where you have *Manage people* (or one inside it) |
| Link two holons, or change that link | You are on the team of either of the two holons |
| Create a holon inside another | You are on the team of the holon it goes inside, and that kind of holon is allowed there |
| Create a holon at the top level | Global editors only |
| Change a journey's steps | Global editors. A team may edit a journey only when their holon is the only one using it |
| Import a CSV file | People added to the importers list |
| Delete a holon or a person | Full administrators only |
| Give someone access | Administrators only |

---

## Private holons

A few kinds of holon are private: Outreach networks and Outreach lists, which hold who
someone knows and who they are approaching. If you are not on the team of a private holon
(and have not been given *View private*), it does not show up in search, lists or
suggestions, and its page refuses to open.

Sharing an Outreach list with someone gives them that list only, not the network above it.

---

## Why can't I…?

**…see an app in the sidebar?**
Either you have not been added to that app, or your current Focus has nothing of that kind
in it. Switch Focus first (see [Focus](../web/app/focus-and-scoping.md)); if the app is
still missing, ask an administrator to add you to it.

**…edit a holon I can open?**
Seeing is not the same as editing. You are not on that holon's team, or you are on the team
but at a step that carries no rights yet. The message names the holon: *"You need access to
… to change this — ask someone on its team."*

**…add people to an organisation my event works with?**
Your event is linked to the organisation, not above it, so your team rights stop at the
link. Ask an administrator to put you on that organisation's team.

**…edit a person I just added?**
You can edit a person only while they belong to a holon you manage. If you created them
without adding them to one of your holons, add them to one, or ask a global editor.

**…see a holon a colleague can see?**
It is probably a private kind, and they are on its team.

**…find the notes on a holon?**
Notes are a team's internal record. They show only to that holon's team.

**…delete something?**
Only full administrators delete. Ask one.

---

## Getting access

Ask an administrator, and say which of these you need:

- **An app** ("add me to Coherence").
- **A holon's team** ("put me on the team of this camp"). An administrator, or anyone
  already on that team, can add you; the step you are placed at decides your rights.
- **Wider editing rights**, if your work spans many holons that are not inside one another.

Anyone on a holon's team can open its configuration page (the gear tab) and look at the
**Access** section, which lists who holds which right on that holon and where it comes from.
