# Asks

An **ask** puts a question, or a few, to people and collects their answers. You write the
questions, may add a YouTube video of yourself asking them, and share a link. Anyone with
the link can answer, in text or on video, without signing in. Feedback after a gathering is the
first use.

## An ask is an event

An ask is a small event of its own, under the holon you make it on — a camp, a
gathering, an organisation. It is listed among that holon's **Events**, and search
finds it as an Event. It has its own page, where its answers are.

An ask never appears on the public site, whatever the holon it was made on shows.

## Making an ask

1. Open the holon's **Configuration** page. Its **Asks** section lists the asks made on
   it.
2. Under *New ask*, type a name and press *Create*. The ask's editor opens.
3. The editor has four screens, in the order the person answering sees them:
   - **Question** — the questions (at least one is needed; see
     [Several questions in one ask](#several-questions-in-one-ask)), a YouTube link (a
     Short works too) and whether the video is *Upright* or *Wide*. **Longest video
     answer** (*1 minute*, *2 minutes*, *3 minutes*, *5 minutes*, *10 minutes* or
     *15 minutes*) is how long a video answer may run once the answering screens are
     updated; until then, and when none is chosen, it is 2 minutes.
   - **Before you send** — the consent line the person must tick before sending. It starts
     as "I agree that *the holon* receives and keeps my answer."; change the words if
     you need to. An ask with no consent line is not ready to share.
     **Answers may be published** (*No* or *Yes*, *No* when unset) says whether answers
     to this ask can be sent on to publishing. Set it to *Yes* only with a consent line
     that says so: the line is where the person agrees.
   - **Sending** — nothing to set.
   - **Thank you** — the message shown once the answer has arrived.

   **Question** and **Thank you** also each have a **Sound**, played to the person as
   they reach that screen, and its **Sound volume**; see
   [Sounds](../coherence/room-editor.md#sounds).
   **Question** also has a **Background**: a picture or a YouTube link, to be shown
   behind every answering screen once those screens are updated. An ask that sets none uses its scene's background, else the
   background picture on its organisation's theme (set by staff on the theme), so
   every ask under the organisation gets it without anyone setting it. The editor
   marks an inherited one *From the organisation's theme*.

   The *Question* screen opens with a short **How an ask works**. **Next:** *the next screen's name* **→** at
   the foot of each screen takes you on to the next one. An ask has no *Reset all
   customisations*: its questions, consent line and thank-you are what it is, so set each
   setting back on its own. Once the ask is ready to share, the *Ready* panel has a
   **Share** box: the link, **Copy link**, **Open as a respondent**, and a **QR code**
   with **Download QR code**, for printing at a venue.
4. Copy the ask's link from the Share box, or from the Asks section, and share it. If the section says
   *No link yet*, the site you made the ask on has no Asks address: the link exists only
   for asks made under a holon of a site that has one. Make the ask under such a holon,
   or ask your administrator to give the site one.

## Where everything is

Each address below is on your METIS app's address, for example
`https://<your app address>/app/ask/`. `<id>` is a holon's or an ask's number, shown in
its page's address.

| What | Address | What you see there |
|---|---|---|
| The list of every ask you can see | `/app/ask/` | One row per ask. *New* there only says where asks are made. |
| A holon's Asks section, where asks are made | `/app/metis/holon/<holon id>/configuration/` | **Asks**: each ask with its answer count, its link with *Copy link*, *Edit*, *Answers* and *Archive*; then *New ask* and *Create*. |
| An ask's editor | `/app/ask/asks/<ask id>/editor/` | The four screens, each with its settings and a preview. |
| An ask's own page, with its answers | `/app/metis/holon/<ask id>/#section-ask-answers` | The **Answers** section. |
| The holon's Publishing page | `/app/iris/holons/<holon id>/publishing/` | The YouTube and LinkedIn connections publishing uses. |
| The link people answer on | `https://<your Asks address>/<the ask's address>` | Shown in the Asks section; copy it from there rather than typing it. |

## Trying your ask

Try every ask once yourself before sharing it. Allow ten minutes for a video answer.

1. **Check it is ready.** An ask needs at least one question and a consent line
   (see [Making an ask](#making-an-ask)). The editor shows whether both are there.
2. **Preview each screen.** In the editor, pick each of the four screens in turn. The
   preview shows it as the person answering will see it, updating as you type; it says
   *Not saved yet* until you save. The preview plays no sound.
3. **Open the link as a stranger.** In the Asks section, press *Copy link*. Open it in a
   private browser window, or send it to your phone. You see the ask's first screen,
   with your video if you added one. A page saying the link doesn't lead to an ask means
   the link was copied wrong or the ask is archived.
4. **Answer in text.** Press *Answer in text*, type an answer to each question and press
   *Continue*. On *Before you send*, type a name and an email (made up is fine), tick the
   consent line and send. The *Thank you* message
   shows.
5. **See the answer.** In the Asks section, press *Answers* (or open the ask's own page).
   The answer is there at once, with the question, the text, the name and email typed,
   and *Person: not linked*. The Asks section's count goes up by one.
6. **Answer on video** (on a phone, if people will use phones). Open the link again,
   press *Answer with video*, allow the camera and microphone, record (*Re-record* starts
   again), press *Use this*, fill in *Before you send* and send. On the Answers
   section the answer shows at once with *Video on its way*. Reload after a few minutes:
   the video plays, with its **Transcript** under it. If it says the video or the
   transcript *could not be brought in*, the reason is under it.
7. **Clean up.** Press *Delete* on each test answer. It removes the answer and its video,
   and cannot be undone. If a test answer was linked to a person, the person stays.

To stop an ask, press *Archive* in the Asks section: its link stops working, and its
answers are kept.

## Several questions in one ask

The **Questions** setting is a list. *Add question* adds a row; the arrows move a row up
or down; the cross removes it. An ask holds up to ten questions, each up to 1,000
characters. An ask made before questions became a list shows its one question as the
first row.

Each question may have a **time hint**, 5 to 120 seconds: a soft countdown shown with the
question. It stops nothing; the take's own time limit is the only hard stop.

Each question may also have a **prompt**, up to 300 characters: a line shown under the
question to guide the answer ("You could talk about a moment that stayed with you.").
An ask also has a **Description**, shown under the ask's name. In the editor it sits
under the ask's name at the top, like a subtitle (*No description yet* when there is
none): press *Edit name & description* to change the name and the description together,
with one *Save*. Once the answering screens are updated, people answering see the ask's
name, its description and the organisation's logo at the top, and each prompt under its
question.

An ask has one name. Renaming it in its editor, or with the *Name* field on its own
page, changes it everywhere: in the **Asks** list, on the ask's page and in its tab
title, in the editor, and for people answering. Its link stays the same.

Until the answering screens are updated, people answering see only the first question,
with no time hint (and in text, one box), and the editor says so on the *Question* screen of
an ask with more than one. Once they are updated, the person answering sees the
questions one after another, in the list's order. There is no going back and no
skipping:

- **On video**, all the questions are answered in one recording. The first shows over the
  camera with *1 of 3*; *Next question* moves on, after a few seconds.
- **In text**, there is one box per question, and each must be filled in.

With several questions, the setting **With several questions, show first** chooses what
the first screen shows, before the person picks video or text: *One at a time* (the
first question and how many there are) or *All listed up front*, so people can think
about each answer before they start. When the ask chooses neither, it follows the
organisation's setting, and with none there either it is one at a time. On video the
questions still come up one at a time either way.

Each answer keeps the questions as they were worded when it was given: editing the list
later does not change answers already in.

## Who sees the answers

Anyone who can edit the holon the ask was made on: the same people who can open its
Configuration page. Nobody else sees the Asks section, the answers or the editor.

Each answer shows the question as it was worded when the person answered, their text,
and the name and email they typed, if any. An answer to several questions shows them in
order, each question with the words typed for it. Typing a name never adds anyone to People.

## Video answers

A person can answer on video instead of in text, on a phone or a computer, held upright
or sideways. A take lasts up to two minutes, or, once the answering screens are
updated, up to the ask's **Longest video answer** (2 minutes when none is chosen). They
can record it again before sending, and only the take they send reaches METIS.

A video answer is listed at once, with its name, email and question, and the line
**Video on its way**. Within a few minutes the video arrives, playing in its shape
(tall for upright, wide for sideways), with a **Transcript** of the words spoken under
it. Only what was said during the take is kept. For an ask with several questions, the
transcript is split under the questions: each question as a heading, followed by what was
said while it was on screen. The split arrives a few minutes after the transcript; until
then the transcript shows as one block.

If the video cannot be brought in, the card says *The video could not be brought in.*,
with the reason under it. If the video arrived but its words could not be (someone who
said nothing, for instance), the video plays and the card says *The transcript could
not be brought in.* Nothing is retried on its own.

Answers are found only in the ask's **Answers** section: an answer adds no note to any
timeline and sends no message. They do not appear among Coherence's conversations.

## Saying who answered

Each answer says **Person:** — *not linked* until someone links one. Press *Link a
person* to choose someone already in People. If you can add people and the person typed
a name, *Create “name”* adds them to People with that name and email, and links them.
Once linked, the answer shows their name as a link to their page; *Change* links someone
else instead.

## Publishing answers

On an ask set to **Answers may be published: Yes**, each answer given while it was set
so has a **Send to publishing** button. Every answer keeps the setting and consent line
it was given under: switching an ask to *Yes* later does not make earlier answers
publishable, and switching it back to *No* does not take the button away from answers
given under *Yes*. A video answer can be sent once it has been brought in.

Sending starts the **Answer publishing** pipeline, shared by every ask. The card shows
each step as it runs. METIS writes a title, a YouTube description and a LinkedIn post
from the answer, makes a cover and an **Instagram card**, and uploads a video answer to
YouTube as unlisted. A text answer has no video, so the YouTube steps pass it straight
through. Then the card says **Waiting for your approval**, with what was written, the
cover, the Instagram card and the unlisted video link:

- **Publish** sends it out: the video is made public, the post goes on the holon's
  LinkedIn page, and the Telegram channels get the announcement. The card then says
  *Published*, with a link to each.
- **Don't publish** stops it, and nothing goes out.

The **Instagram card** is one tall image (4:5, 1080 × 1350 pixels): the question at the
top, the person's words, and the name they gave, with their photo when a person is linked
to the answer (initials otherwise). A short answer (up to about 40 words) goes on the card
whole; a longer one shows the striking sentence or two METIS picked from it. METIS does not
post it: press *Download* under it and post it on Instagram by hand. It stays on the card
once the answer is published, and goes when the answer is deleted.

The person who answered is not contacted again; the team decides. Answers never get a
public person page.

Where it goes, and with which accounts, comes from the **Publishing** page of the holon
the ask was made on (or the nearest holon above it with one): its YouTube channel,
LinkedIn page and Telegram settings. Connect them there before you send an answer. The
pipeline's steps can be changed in the journey editor, as any publishing pipeline.

## A gathering's contributor profile

A gathering can collect its contributors' profiles (what moves them, what they want to
do, what they can and cannot do) through an ask with its own questions:

1. Make an ask on the gathering and write its questions.
2. On the ask's question space, set **Contributor profile** to **Yes**.
3. On each question, choose **Private** or **Public**. Private is the default.
4. If public answers should show on contributors' public pages, set **Answers may be
   published** to **Yes** on the *Before you send* space.

Only answers from people who were signed in when they answered count: an answer without a
sign-in stays an answer to the ask and nothing more. Each person's newest answer to the
ask is their profile; older answers stay in the ask's **Answers** section.

**In METIS**, a person's page shows a **Contributor profiles** section, each ask under the
gathering's name, with every question and the person's answer. Public questions carry a
**Public** chip. A video answer shows as a link to the answer in the ask's Answers section.
Only someone who can read the ask's answers sees it.

**On the public site**, a person's public page shows **Contributor profile** with the
answers to Public questions, only when all four hold:

- the question is marked **Public** now, and is still worded as it was when the person
  answered (a question reworded since counts as private until they answer again);
- the ask allowed publishing when the person answered (changing **Answers may be
  published** later does not change answers already in);
- the gathering is published on the public site;
- the person already has a public page. Answering never gives anyone one.

Only text answers show publicly; video answers never do. Two asks on one gathering both set
as contributor profiles each show, under their own names. The open API's
`GET /api/v1/people/{person_id}/contributor-profiles` returns what the METIS section
shows ([API](../../api/v1-PLAYBOOK.md)).

## Keeping and deleting answers

Answers are kept until someone deletes them. *Delete* on an answer removes it and
everything METIS made from it, a video answer's video included; it cannot be undone. A person linked to the answer stays
in People. Posts already live outside METIS stay up: an answer that was published lists
them under *Still live: take these down by hand*, and you remove them on YouTube and
LinkedIn yourself.

*Archive* on an ask stops its link working. The ask and its answers stay.

*Delete this ask*, at the bottom of the ask's own page (staff only), deletes the ask
with all its answers, their transcripts and recordings, and the ask's room settings. The
warning before it says how many answers go, and that it cannot be undone. Posts already
published outside METIS stay where they are. The holon the ask was made under keeps a
line in its activity saying who deleted the ask and what went with it. An ask that keeps
a look of its own (one other rooms may wear) is not deleted, and the message names what is in the way.
