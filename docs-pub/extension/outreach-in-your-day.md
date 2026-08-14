# Outreach with the extension, day to day

This is the practical guide to the part of the Chrome extension that does LinkedIn outreach
work: reading a search into a list, reading people's profiles, and working through the queue
of connects, messages and checks that METIS has lined up.

If you only want to look people up while browsing, [Using the Chrome
Extension](using-the-extension.md) covers that and is all you need. This page is for the days
when the extension is doing work *for* you.

> **The one rule to remember:** the extension drives your own browser, using your own LinkedIn
> account. Everything it does, LinkedIn sees as you doing it. That is why it is slow on
> purpose, why it holds one tab, and why there is a ceiling on how much it will do in a day.

---

## The two halves of the work

It helps to know which half you are looking at, because they behave differently.

| | **Your browser** | **The METIS queue** |
|---|---|---|
| Does what | Reads LinkedIn search pages and profile pages | Connects, messages, connection-state checks |
| Runs when | You press start, and only while the tab and panel stay open | You press start, then it works at the pace METIS sets |
| Needs you | Yes — it is your window it is driving | Only to start it and leave it be |

Both are started from the same place: the **play tab** in the panel.

## Opening the panel

The panel has two tabs:

- **the eye** — what METIS knows about the page you are on right now (a person, a company, an
  email thread);
- **the play triangle** — what there is *to do*, and the buttons that do it.

The play triangle tells you things without being opened. It pulses while work is running, sends
out a slow ring when work is waiting for you, and carries a count of what is queued. Amber and
still means there is work but today's allowance is spent — it will carry on tomorrow.

## A typical day

### 1. Find people: read a search into a list

Run a people search on LinkedIn, as you normally would — keywords, filters, the lot. With the
results on screen, open the panel's play tab and press **Read this search**.

The extension then walks the result pages one at a time, saving everyone it finds into METIS as
People, gathered on a new Outreach list. You will see it move: the page counter, a running
tally of who is new to METIS and who was already known, and a live list of names as they land.

Leave the tab in front while it reads. Chrome slows and sometimes misdraws pages in background
tabs, and a misdrawn page is a page read wrong. Put the window aside and use another window if
you want to carry on working.

When it finishes you have a list — **Outreach → Lists** in METIS — full of candidates with
whatever the search results showed: name, headline, location.

### 2. Decide who is worth reading

Search results are thin. The full profile — experience, education, skills — is a separate
page per person, and opening one is a visit LinkedIn shows to its owner. So METIS never opens
them off its own bat: you choose the people on the list's page in METIS, see exactly how many
profiles that is, and confirm it.

That confirmation creates a **profile-reading pass**: a queue of people, in the order METIS
will work through them.

### 3. Read the profiles

Back in the panel's play tab, the pass is now the thing on offer:

> **Read 84 profiles from Impact investing**
> Holds this tab while it runs. 40 left in today's allowance; the rest continues tomorrow.

Press it and the extension takes the tab to LinkedIn and starts working through the queue. It
opens one person, reads what it was asked for, pauses, opens the next. The pauses are not
padding — they are what keeps the pattern human — so a pass of a hundred people is a
background-of-the-morning job, not a two-minute one.

While it runs, the panel shows you:

- **Now** — whose profile is open this second, and what it is doing with it;
- **Done** — a progress rail, tallies (complete, partial, blocked, remaining), and
- **People read** — the last few people, newest first, each with a word for how it went.

That last list is worth watching for a moment when you start a pass. If people are appearing
with **not read** against them, the pass is opening profiles and getting nothing from them —
and after three of those with nothing read at all, it stops itself and says so rather than
spending the day's allowance on pages it cannot use.

### 4. Pause whenever you like

**Pause** sits at the top of the panel, beside the clock.

It keeps everything read so far and leaves the rest of the queue exactly where it is. The panel
returns to the play tab and offers the same pass again — same people, same order — so pausing
costs you nothing but the time you were away. Closing the panel or the tab does the same thing:
the pass simply stops moving.

Pause is the strongest thing the extension can do to your queue, on purpose. The extension
works through what METIS has lined up and never decides that work should stop existing. Clearing a queue is a decision you make in METIS — select the rows on
**Outreach → Actions** and cancel them there.

### 5. Work the queue

Connects, messages and connection-state checks are queued in METIS — by you, by a campaign, by
a colleague. The play tab offers them together:

> **Run 12 queued actions**
> Connects, messages and state checks, at the pace METIS sets.

This one also drives your browser, so the same rule applies: leave it in front. It ends on its
own when the queue is empty, when the day's allowance is spent, when it reaches its time budget,
or when you press stop. Whichever it was, it tells you which — and offers the move that follows
from it. If work remains and the day allows, starting again is one press. If the day's allowance
is spent, or LinkedIn is throttling the account, there is deliberately no start button and a
sentence saying so instead: pressing on would only make it worse.

**A message always waits for you.** When the next action is a message, the run stops before it
opens anybody's page and shows you the draft. Edit it, send it, or skip this one — skipping
cancels that message and the run carries on with the next person. Nothing is sent until you say
so, and your edit is saved on the action, so closing the panel mid-draft does not lose it.

Stopping a run ends *the shift*, not the work: anything still queued stays queued and is there
for the next run. As with a paused pass, removing queued actions is done in METIS.

You can see the same queue any time at **Outreach → Actions** — *Up Next* for what is coming,
*History* for what happened.

### 6. Watch the allowances

**Done today** on the play tab shows what has already been used: profiles read, connection
requests sent, and so on, each against its ceiling.

These are per person and they reset on their own. Most are daily — **connection requests are
weekly**, because that is how LinkedIn itself rations invitations, and a week's worth spent by
Wednesday is still spent on Thursday. Each meter on *Up Next* says which period it counts over.

Hitting a ceiling is not an error and nothing is lost: the remaining work simply carries on when
the allowance comes back — tomorrow for a daily one, Monday for connection requests. A queue
deeper than one allowance is a perfectly ordinary thing to have.

## When something is wrong

The panel tries to tell you plainly. The ones you are most likely to meet:

- **"Could not open LinkedIn"** — the tab did not get there, usually a sign-in wall. Nothing was
  started and nothing in METIS changed. Open LinkedIn in that tab yourself, sign in, and the
  waiting pass is offered again.
- **"Bring this LinkedIn tab to the front"** — LinkedIn will not draw a profile page in a
  background tab, so METIS waits rather than record a blank page as a blank profile.
- **People appearing as "not read"** — LinkedIn served a page that could not be used. A few
  scattered ones are ordinary (deleted accounts, hidden profiles). All of them, one after
  another, is a fault: the pass will stop itself, and the blocked rows on the list say why.
- **"Nothing waiting"** — genuinely nothing to start here. If you expected work, check
  **Outreach → Actions**; a pass that is stopped or needs attention shows on its list in METIS.
- **Disconnected** — the extension uses your METIS login in the same browser. Sign in to METIS
  there and reload.
- **An update warning on the settings gear** — a newer extension is available. METIS will refuse
  to hand work to an out-of-date one rather than let it act on rules it does not know.

## Things people ask

**Can I use the computer while it runs?** Yes — just not *that* window. Move it aside and work
in another window. Minimising it or switching to another tab in the same window pauses progress.

**What if I close the panel by accident?** The run stops. Nothing already read is lost, and the
rest is still queued.

**Can two of my windows run at once?** No — one queue run per account, deliberately. Two
windows pacing the same LinkedIn account is a rate nobody can see or control, so the second one
is refused and told which tab is holding it. A profile-reading pass works the same way: it
belongs to the browser that picked it up.

**Does anyone else see this work?** LinkedIn sees profile visits and connection requests as
yours, exactly as if you had clicked them. Colleagues in METIS see the lists, the queue, and
who ran what.

**Someone else queued the pass — can I run it?** Yes, if you can edit the list. It then counts
against *your* allowances, because it is your account opening the pages.

---

Related: [Using the Chrome Extension](using-the-extension.md) ·
[LinkedIn imports and Outreach campaigns](../metis_apps/outreach/linkedin-outreach.md)
