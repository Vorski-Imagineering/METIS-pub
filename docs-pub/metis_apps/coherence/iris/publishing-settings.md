# Publishing settings

A holon's **Publishing** page holds where and how the conversations under it
publish: which YouTube visibility and playlist, which LinkedIn Page, which
Telegram bot, who is blind-copied on the notification emails, the copy of
those emails, and every other setting of a publishing step. Set them once on a
holon and every pipeline that runs under it uses them, as does everything
below it in the holon tree.

## Opening it

On a holon's page, the icons hanging from the top right lead to its other
views: the gear is **Configuration**, the paper plane is **Publishing**. The
paper plane shows on holons that hold conversations (Coherence events, for
example) and on any holon that already has publishing settings. Anyone who
can open a holon's Configuration can open and change its Publishing page.

The page lists each kind of publishing step (YouTube upload, LinkedIn post,
cover images, notifications, and so on) with its settings. **Edit** opens one
step's settings; **Save** keeps only the values you changed.

## Where a value comes from

Every value says where it comes from:

- **default**: neither this holon nor any above it sets it, so each
  pipeline uses its own step's setting. The value shown is the step's
  built-in default; a pipeline's step may have been given another;
- **from *a holon above***: the nearest holon above this one that sets it;
  the name links to that holon's Publishing page;
- **set here**: this holon sets it, for itself and everything below.

The nearest holon wins, one setting at a time: an organisation can set the
notification bcc while one of its events sets its own reply-to address, and
the event gets both.

Each setting in the form has a choice beside it: **Use inherited** or
**Custom**. Custom keeps the value you see here, even one equal to the
default; Use inherited removes this holon's value, so it takes the one from
above again. Changing a value counts as choosing Custom. Settings you do not
touch keep their choice, so saving one setting changes nothing else.

If a value would break one of the step's own rules (a LinkedIn template with
no `{post}`, an unknown cover-image pack), Save refuses it and says why. A rule
that compares two settings (no more than the maximum number of speakers) is
checked at Save only when every setting that step requires is known here.
When a pipeline runs, its step's settings with every holon's values laid
over them are checked once more, as a step's settings always were; if they
do not fit together, the step reports it as it would any other settings
problem. For the notification steps and the LinkedIn publishers that means
the step is **blocked for the whole journey**, not just for one
conversation. Fixing the value here does not lift the block by itself: after
fixing it, open the journey's step and press **Retry now** on its block
banner (or save the step's settings again).

## Setting something for everything under a holon

At the foot of a holon's Publishing page, *Set these for everything under:*
lists the holons above it that you can change. Open one to set a value for
every holon below it, including ones that do not hold conversations
themselves. Once a holon has settings, its own page shows the paper plane too.

## Connecting YouTube and LinkedIn

The **Connections** block at the top of the Publishing page holds the holon's
logins: the YouTube channel videos are uploaded to, and the LinkedIn account
posts are made with. Connect each **once per brand**, on the highest holon
that publishes as that brand; every pipeline under it uses that login, and so
does everything below it unless a holon below connects its own.

For each of YouTube and LinkedIn the block says one of three things:

- **connected here**, with the channel's name and picture (or the LinkedIn
  Pages the login can post as): this holon holds the login. **Reconnect**
  replaces it, for example to pick a different channel or to renew a LinkedIn
  login before it expires;
- **connected via *a holon above***: a holon above holds the login, and the
  name links to its Publishing page, where it is changed;
- **not connected**, with **Connect**.

**Connect** takes you to Google's or LinkedIn's own screens; choose the right
channel or Page there, and you come back to this page. Anyone who can open
the holon's Configuration can connect it; no other permission is needed.

A step in the journey editor, and a conversation's step, no longer has a
connect button. It says where its login comes from: *YouTube login: from
**Coherence Conversations***, or *No YouTube login: connect one on
Publishing*, with a link. A conversation whose event finds no login simply
waits at that step, and goes on by itself once a login is connected.

### When YouTube or LinkedIn rejects a login

A login can stop working: access was revoked, a password changed, or a
LinkedIn login reached its expiry (about 60 days). The holon that holds the
login then shows **Rejected since *date***, with the reason, and its team gets
a note saying so. Only the conversations under that holon wait; nothing else
stops. Reconnect on that holon's Publishing page, or, if the fault is fixed
some other way, press **Retry now**.

No page ever shows a login's secret, only its name.

## What it does not hold yet

The Telegram bot a step sends through is still chosen on each pipeline's
step.

A pipeline's step settings remain the defaults: changing a step in the
journey editor changes every holon that does not set that value itself.
