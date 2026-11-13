# Usage

How much your rooms were used: how many conversations and answers, and how many
participant-minutes. Every app that runs rooms is counted on the same page: Coherence and
Asks today. Each app's figures use its own words. Coherence counts **conversations** at
**events**, and Asks counts **answers** to **asks**.

## Opening it

1. Open your tenant's **Configuration** page. The tenant is the holon at the top of your
   organisation's tree.
2. Under **Usage**, press **Usage**.

You can open it if you can open the tenant's Configuration page. The page shows your
tenant's figures and no one else's.

## What it shows

Two tables, for the last three months:

- **By app**: one line per app and per day, week or month.
- **One by one**: one line per event or ask.

| Column | What it counts |
|---|---|
| Sessions | Conversations or answers that **started** in that period, including any still going. A text answer counts too. |
| Participant-minutes | Minutes reported by the video provider for sessions that have **ended**. They arrive about an hour after a session ends, and a text answer adds none. |
| Peak participants | The most people in one session at the same time. |
| In use | How many events or asks had at least one session in that period. |

Choose **Day**, **Week** or **Month** above the tables. The choice is kept in the page's
address, so a link you share shows the same view.

## Whose figures they are

A session counts for whoever owns its event or ask **now**. If an event moves, its past
sessions move with it.

## The timezone

Days, weeks and months are counted in your tenant's timezone. A session that starts just
before midnight is counted on the day it was in your timezone. To set the timezone, fill in
the tenant's **Timezone** field (for example `Europe/Lisbon`). When it is not set, Lisbon
time is used.
