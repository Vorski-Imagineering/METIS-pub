# IRIS Podcast RSS Platform Connection Guide

**Platforms:** Spotify, Apple Podcasts, YouTube / YouTube Music, Amazon Music / Audible, iHeartRadio, Pocket Casts, and Castbox  
**Last verified:** 2 August 2026  
**Audience:** IRIS product, editorial, and operations teams  
**Scope:** Connecting an existing IRIS-hosted public podcast RSS feed to major listening platforms. This document does not cover implementation of the RSS feed itself.

---

## 1. Operating model

IRIS remains the canonical publisher.

For each podcast show, IRIS serves:

- one permanent public HTTPS RSS feed;
- one or more durable public audio files;
- durable show and episode artwork;
- approved show and episode metadata.

Each external platform is connected to the show once. After connection, the platform periodically reads the RSS feed and discovers new episodes and metadata changes.

Do not create a separate episode-upload workflow for each audio directory. YouTube is the partial exception because it converts RSS audio episodes into YouTube videos, but the connection is still feed-driven.

A show should not be submitted anywhere until the feed is production-ready. Platform approval is not a substitute for IRIS validation.

---

## 2. Shared preflight checklist

Complete this checklist once for each show before starting any platform connection.

### 2.1 Feed readiness

Confirm that:

- the RSS feed is available over public HTTPS;
- the feed URL is permanent and does not require authentication, cookies, query tokens, or signed URLs;
- the feed returns valid RSS XML;
- the feed contains the expected podcast namespaces and required podcast metadata;
- the show has at least one published episode;
- the show has square artwork that meets Apple’s requirements;
- each episode has one valid audio enclosure;
- enclosure URLs are permanent public HTTPS URLs;
- audio endpoints support `GET`, `HEAD`, and byte-range requests;
- each episode has an immutable GUID;
- publication dates, duration, MIME type, and enclosure byte length are correct;
- no future scheduled episode is exposed prematurely;
- the feed does not contain `<itunes:block>Yes</itunes:block>` unless the show is intentionally private;
- the feed is reachable from outside the IRIS network.

### 2.2 Ownership email

The feed should expose a monitored organisational email address that the team can access during onboarding.

Spotify, YouTube, iHeartRadio, and Castbox use or may use the email address in the RSS feed to verify ownership. Although Apple no longer relies on the old RSS owner-email mechanism in the same way, keeping a controlled feed email remains necessary for the wider distribution workflow.

Use a dedicated address such as:

- `podcasts@...`
- `publishing@...`
- another long-lived organisational mailbox

Do not use a developer’s personal address. The mailbox may be publicly visible in the RSS XML.

### 2.3 Account ownership

For every platform that requires an account:

- use an organisation-controlled account;
- enable two-factor authentication where available;
- record the recovery method in the organisation’s password manager;
- avoid tying the show solely to one person’s private account;
- add at least one second administrator after successful setup where the platform allows team access.

### 2.4 Material to have ready

Prepare:

- canonical RSS feed URL;
- show title exactly as it appears in the feed;
- show description;
- show artwork;
- public show website URL;
- feed ownership email;
- publishing organisation name;
- content-rights confirmation;
- explicit-content classification;
- primary category and language;
- intended launch countries or regions;
- the IRIS staff member responsible for the connection.

### 2.5 Connection record in IRIS

For each platform, IRIS operations should record at least:

- platform name;
- connection status;
- account or channel owner;
- submission date;
- submitted-by staff member;
- verification email used;
- external show identifier, where available;
- public platform show URL;
- approval or verification date;
- last manual check date;
- exceptions or support-case references.

Suggested operational statuses:

- Not started
- Submitted
- Verification pending
- Review pending
- Connected
- Needs attention
- Rejected
- Retired

This is an operational requirement, not authorisation for a particular Django schema.

---

# 3. Spotify

## 3.1 What the connection does

The show remains hosted by IRIS. Spotify reads the IRIS RSS feed, lists the show in Spotify, and provides Spotify-specific analytics and audience tools through Spotify for Creators.

Do not select Spotify hosting. The correct route is to find or submit a show hosted “somewhere else.”

## 3.2 Prerequisites

Before starting:

- the RSS feed must be publicly accessible;
- the feed must expose an email address the team can access;
- the show should contain at least one published episode;
- create or select the organisation-controlled Spotify account that will administer the show.

## 3.3 Initial connection steps

1. Open Spotify for Creators and sign in with the organisation-controlled Spotify account.
2. If this is the first show under the account, select **Find an existing show**.
3. Select **Somewhere else** to indicate that IRIS, not Spotify, hosts the show.
4. Enter either:
   - the canonical IRIS RSS feed URL; or
   - the Spotify show URL, if Spotify has already discovered the show.
5. Review the show Spotify identifies. Confirm that the title and artwork match the intended IRIS show.
6. Request ownership verification.
7. Spotify sends an eight-digit verification code to the email address published in the RSS feed.
8. Retrieve the code from the organisational mailbox.
9. Enter the code in Spotify for Creators and complete verification.
10. Confirm that the show now appears under the correct Spotify for Creators account.
11. Add any required team members and assign the minimum access each person needs.

If the account already manages another show:

1. Sign in to Spotify for Creators.
2. Open the account menu.
3. Select **Add a new show**.
4. Select **Find an existing show** and then **Somewhere else**.
5. Continue with the RSS and verification steps above.

## 3.4 Definition of done

Spotify is connected when:

- the show appears in Spotify search or has a working Spotify show page;
- the correct Spotify for Creators account has administrative access;
- ownership verification is complete;
- the public Spotify show URL and Spotify identifier are recorded in IRIS;
- at least one episode plays successfully;
- a subsequent RSS metadata change is observed by Spotify or the feed relationship is visible in Spotify for Creators.

## 3.5 Ongoing publishing

After connection:

- publish episodes only through IRIS;
- keep episode GUIDs stable;
- let Spotify ingest new episodes from the RSS feed;
- use Spotify for Creators for Spotify analytics, comments, polls, and Spotify-only presentation features;
- treat the IRIS feed as authoritative for shared episode metadata.

Do not manually recreate RSS episodes inside Spotify. That creates two publication paths and will eventually produce identity confusion.

## 3.6 Updating the feed URL

Changing the canonical RSS URL is a migration, not a routine edit.

If IRIS ever moves the feed:

1. keep the old feed live;
2. return a permanent redirect from the old feed to the new feed;
3. update the RSS URL in Spotify for Creators under the show settings;
4. preserve all episode GUIDs;
5. verify that Spotify reads the new feed before retiring any old infrastructure.

## 3.7 Troubleshooting

### Verification email does not arrive

Check:

- that the address in the public RSS feed is correct;
- that the mailbox is accessible;
- spam and quarantine folders;
- whether the feed was recently changed and Spotify may still have cached the old version;
- whether the submitted URL is the exact canonical feed URL.

Do not repeatedly change the ownership email during an active verification attempt. Correct the feed, wait for it to be publicly visible, and then request a fresh code.

### Spotify finds the wrong show

Possible causes:

- a duplicate feed exists;
- a previous host submitted the show;
- the same title is used by another show;
- the RSS URL redirects unexpectedly.

Stop and reconcile the existing listing. Do not knowingly create a second Spotify show for the same podcast.

### New episode is missing

Check, in order:

1. the episode is present in the public RSS XML;
2. its GUID is unique;
3. the enclosure is publicly reachable;
4. the publication date is not in the future;
5. the feed returns successfully without authentication;
6. the audio MIME type and file length are correct.

A platform refresh delay is normal. An invalid or unreachable feed is not.

## 3.8 Official references

- Spotify: Adding a new show to Spotify for Creators  
  https://support.spotify.com/us/creators/article/adding-a-new-show-to-your-spotify-for-creators-account/
- Spotify: Claiming a podcast hosted elsewhere  
  https://support.spotify.com/us/creators/article/claiming-your-podcast-on-spotify-for-creators/
- Spotify: Updating an RSS feed link or hosting provider  
  https://support.spotify.com/us/creators/article/updating-an-rss-feed-link-or-hosting-provider/

---

# 4. Apple Podcasts

## 4.1 What the connection does

Apple Podcasts Connect validates the IRIS RSS feed, reviews the show, and publishes it in the Apple Podcasts catalogue. IRIS continues to host the feed and audio.

Apple submission is more formal than most directories. Technical validation and editorial review are separate. Passing feed validation does not guarantee approval.

## 4.2 Prerequisites

Before starting:

- create an Apple Podcasts Connect account using an organisation-controlled Apple ID;
- complete any account agreements and contact information requested by Apple;
- ensure the RSS feed meets Apple’s technical requirements;
- include at least one published episode;
- include compliant show artwork;
- confirm the organisation has rights to all third-party material in the show;
- decide the intended country and region availability;
- decide whether the feed should be publicly available through Apple’s catalogue API;
- decide whether IRIS will provide transcripts through RSS or Apple may generate them.

## 4.3 Initial connection steps

1. Sign in to Apple Podcasts Connect.
2. Click the **Add (+)** button.
3. Select **New Show**.
4. Choose **Add a show with an RSS feed**.
5. Enter the canonical IRIS RSS feed URL.
6. Choose whether access to the show inside Apple Podcasts Connect should be restricted to selected account users.
7. Click **Add**.
8. Review the imported show information carefully:
   - title;
   - author or artist;
   - description;
   - artwork;
   - category;
   - language;
   - explicit classification;
   - show type;
   - website and copyright information.
9. Set **Content Rights** and confirm that the publisher has rights to any third-party content.
10. Provide Apple with a show contact who can respond if there is an operational or content issue.
11. Open **Availability**.
12. Configure:
   - countries and regions;
   - whether the RSS feed may be publicly available in the Apple Podcasts Catalog API;
   - transcript handling;
   - immediate release or a scheduled Apple release date;
   - whether show claiming should be allowed.
13. Save the show.
14. Resolve every blocking feed validation warning.
15. Publish the show for Apple review.

## 4.4 Validation and review

Apple validates the feed before submission. IRIS operations should distinguish:

- **validation failure:** a technical problem with the feed, artwork, metadata, or media;
- **review pending:** Apple has accepted the submission technically but has not yet approved it;
- **approved:** the show is available in Apple Podcasts;
- **rejected or needs attention:** Apple requires a correction or clarification.

Do not alter multiple feed fields blindly while Apple review is pending. Fix the specific reported issue and keep the rest stable.

## 4.5 Definition of done

Apple Podcasts is connected when:

- the show is approved and publicly available in the intended regions;
- the correct Apple Podcasts Connect account controls it;
- the Apple show URL and Apple show identifier are recorded in IRIS;
- at least one episode plays successfully;
- the show’s Availability settings match the publishing decision;
- the team contact and account access are recorded.

## 4.6 Ongoing publishing

After approval:

- publish episodes through IRIS;
- allow Apple to poll the RSS feed;
- correct shared metadata in IRIS rather than separately in Apple;
- use Apple Podcasts Connect for Apple-specific availability, transcript policy, analytics, and catalogue controls;
- expect feed changes to take time to propagate.

The metadata in the RSS feed is authoritative for RSS-based show information and may override metadata entered manually in Apple Podcasts Connect.

## 4.7 Transcripts

Apple allows the publisher to choose whether:

- transcripts are supplied through the RSS feed; or
- Apple generates transcripts where supported.

For IRIS v1, select one deliberate policy per show. Do not simultaneously create an uncertain mix of IRIS transcripts and Apple-generated transcripts without knowing which source should prevail.

## 4.8 Updating the feed URL

If the feed moves:

1. maintain the old URL;
2. configure a permanent redirect to the new feed;
3. use Apple Podcasts Connect to update or validate the new RSS URL where required;
4. preserve all episode GUIDs;
5. leave old media URLs available during migration;
6. confirm that the Apple listing continues to show the same show and episodes.

Never submit the new feed as a second new show unless the intention is genuinely to create a different podcast.

## 4.9 Troubleshooting

### Feed fails validation

Check Apple’s exact validation message, then verify:

- required tags;
- artwork format, dimensions, and public reachability;
- at least one episode;
- enclosure URL, MIME type, and byte length;
- `HEAD` and range-request support;
- valid dates;
- XML escaping;
- absence of authentication or temporary URLs.

### Artwork does not update

Use a new versioned image URL rather than overwriting a cached object at the same URL. Update the feed to reference the new URL.

### Show is published in Connect but not available

Confirm:

- at least one RSS episode is published;
- review is complete;
- country and region availability includes the intended market;
- there is no unresolved rights or content issue.

## 4.10 Official references

- Apple: Submit a new show  
  https://podcasters.apple.com/support/897-submit-a-show
- Apple: Podcast RSS feed requirements  
  https://podcasters.apple.com/support/823-podcast-requirements
- Apple: Validate your podcast RSS feed  
  https://podcasters.apple.com/support/829-validate-your-podcast
- Apple: Create an Apple Podcasts Connect account  
  https://podcasters.apple.com/support/827-create-an-account
- Apple: Change the RSS feed URL  
  https://podcasters.apple.com/support/837-change-the-rss-feed-url

---

# 5. YouTube and YouTube Music

## 5.1 What the connection does

YouTube ingests audio episodes from the RSS feed and creates YouTube videos, normally using the podcast artwork as the visual. The resulting podcast can appear on YouTube and YouTube Music.

This is not ordinary directory streaming. YouTube creates its own platform copies and requires an explicit publishing step after initial ingestion.

## 5.2 Prerequisites

Before starting:

- use an organisation-controlled YouTube channel;
- ensure the channel owner’s country or region supports RSS delivery;
- confirm that the channel has access to advanced features, or complete identity verification when prompted;
- ensure the RSS feed exposes a monitored verification email;
- decide whether to import:
  - all existing episodes;
  - episodes published from a chosen date;
  - only future episodes;
- decide the default YouTube visibility;
- decide whether most episodes contain paid promotion.

Portugal is currently listed as an eligible country for YouTube podcast RSS delivery, based on the Channel Owner’s location.

## 5.3 Initial connection steps

1. Sign in to YouTube Studio using the intended organisation channel.
2. Click **Create**.
3. Select **New podcast**.
4. Select **Submit RSS feed**.
5. If YouTube says advanced-feature access is missing, complete the required identity or channel verification before continuing.
6. Read and accept the RSS Ingestion Tool Terms of Service.
7. Review the on-screen explanation and continue.
8. Enter the canonical IRIS RSS feed URL.
9. Ask YouTube to send a verification code.
10. Retrieve the code from the email address published in the RSS feed.
11. Enter the code and complete verification.
12. Choose the episode-import scope:
    - all existing episodes;
    - episodes published since a chosen date;
    - future episodes only.
13. Declare whether most episodes in the feed contain paid promotion, where applicable.
14. Review and set visibility for the imported videos.
15. Save the RSS connection.
16. Wait for YouTube to ingest the selected episodes. This may take several days for a larger back catalogue.
17. Wait for YouTube’s notification that the podcast is ready.
18. In YouTube Studio, open **Content → Podcasts**.
19. Under the video count for the RSS podcast, select **Publish** when the control becomes available.
20. Verify that the show and episodes are public at the intended visibility.

## 5.4 Existing YouTube podcast

If the channel already has a YouTube podcast and the team wants to connect RSS delivery to it:

1. Open YouTube Studio.
2. Go to **Content → Podcasts**.
3. Open the existing podcast’s details.
4. Under **RSS settings**, select **Connect to RSS feed**.
5. Continue with verification and import-scope selection.

Before doing this, decide how existing manually uploaded videos relate to RSS episodes. Do not create duplicate public episodes merely because both paths exist.

## 5.5 Definition of done

YouTube is connected when:

- the RSS feed is verified;
- the intended historical episode range has ingested;
- the podcast has been explicitly published in YouTube Studio;
- the podcast is visible on the intended YouTube channel;
- the show appears as a podcast and is eligible for YouTube Music presentation;
- the YouTube podcast URL and playlist or podcast identifier are recorded in IRIS;
- at least one generated episode video plays correctly.

## 5.6 Ongoing publishing

After connection:

- publish new audio episodes through IRIS;
- YouTube should ingest future episodes according to the connected feed;
- monitor YouTube Studio for ingestion errors;
- keep the RSS feed connected;
- treat YouTube visibility as a platform-specific publishing control.

### Important metadata rule

If staff manually edit an episode’s details in YouTube Studio, YouTube may stop applying later RSS metadata edits to that episode.

Therefore:

- correct shared title and description metadata in IRIS wherever possible;
- reserve YouTube-local edits for intentional YouTube-specific differences;
- document any episode that has diverged from RSS control.

## 5.7 Replacing audio

Updating the audio enclosure in the RSS feed does not necessarily replace the already-created YouTube video automatically.

For a corrected episode:

1. publish the corrected enclosure through IRIS;
2. confirm the RSS item retains the same GUID;
3. open the podcast’s videos in YouTube Studio;
4. open the menu for the affected episode;
5. select **Re-upload from RSS feed**;
6. verify the regenerated YouTube video before considering the correction complete.

## 5.8 Disconnecting the feed

Disconnecting the feed stops future RSS episode ingestion.

To disconnect:

1. open YouTube Studio;
2. go to **Content → Podcasts**;
3. open the podcast details;
4. find the RSS feed connection;
5. select **Disconnect**;
6. confirm the change.

Do not disconnect as a troubleshooting reflex. It can interrupt the ongoing publication path and may create additional reconciliation work.

## 5.9 Troubleshooting

### RSS submission option is missing

Check:

- channel owner country or region;
- advanced-feature eligibility;
- whether the correct YouTube channel is active;
- whether the account is a channel manager rather than the required owner for a restricted action.

### Verification code does not arrive

Check:

- the feed email shown in the public RSS XML;
- spam and quarantine;
- whether YouTube has cached an older feed version;
- whether the submitted URL redirects to a different feed.

### Episode is ingested but not public

The initial import does not automatically mean the podcast is published. Check **Content → Podcasts** for the separate **Publish** action and confirm the intended visibility.

## 5.10 Official references

- YouTube: Deliver podcasts using an RSS feed  
  https://support.google.com/youtube/answer/13525207?hl=en
- YouTube: Publish or disconnect episodes from an RSS feed  
  https://support.google.com/youtube/answer/13973017?hl=en
- YouTube: RSS feed delivery available locations  
  https://support.google.com/youtube/answer/14106258?hl=en
- YouTube: Create a podcast in YouTube Studio  
  https://support.google.com/youtube/answer/12751636?hl=en

---

# 6. Amazon Music and Audible

## 6.1 What the connection does

Amazon Music for Podcasters accepts one RSS feed per podcast series. After ownership confirmation, the show may be distributed through Amazon Music and Audible, subject to Amazon’s availability and content terms.

IRIS remains the host. Amazon’s current terms state that content is delivered through RSS and that Amazon does not re-host the audio under this arrangement.

## 6.2 Prerequisites

Before starting:

- use an organisation-controlled Amazon account;
- ensure the feed is public and valid;
- ensure the feed exposes a monitored ownership email;
- confirm that only one canonical feed exists for the series;
- be ready to accept Amazon’s content licence agreement;
- decide the show’s primary country or audience market where requested.

## 6.3 Initial connection steps

1. Open Amazon Music for Podcasters.
2. Sign in with the organisation-controlled Amazon account.
3. Select **Add or Claim Your Podcast**.
4. Enter the canonical IRIS RSS feed URL.
5. Confirm that Amazon has identified the correct show.
6. Provide the primary country or market if requested.
7. Accept the applicable content licence agreement.
8. Request ownership confirmation.
9. Retrieve the confirmation message sent to the address associated with the feed or verification flow.
10. Complete ownership confirmation using the supplied link or code.
11. Return to Amazon Music for Podcasters and confirm that the show appears under the account.
12. Record the Amazon Music and Audible public links when they become available.

Submit one feed URL per series. Do not submit individual episode feeds or multiple equivalent feed URLs for the same show.

## 6.4 Definition of done

Amazon is connected when:

- ownership is confirmed;
- the show appears in the Amazon Music for Podcasters account;
- the show is searchable or has a working public Amazon Music page;
- the Audible presence is confirmed where applicable;
- at least one episode plays;
- public platform URLs and identifiers are recorded in IRIS.

## 6.5 Ongoing publishing

After connection:

- publish episodes through IRIS;
- allow Amazon to poll the RSS feed;
- use Amazon Music for Podcasters for Amazon-specific analytics and account management;
- do not upload duplicate episodes separately;
- keep the feed URL and episode GUIDs stable.

## 6.6 Updating the feed URL

If the feed moves:

1. keep the old feed online and redirect it permanently;
2. preserve all GUIDs;
3. use the Amazon Music for Podcasters account or support flow to update the RSS URL;
4. verify that both Amazon Music and Audible continue to reference the same show;
5. avoid submitting the replacement URL as a separate new show.

## 6.7 Troubleshooting

### Show already exists

Use the claim path rather than creating another listing. Verify ownership through the canonical feed.

### Confirmation email does not arrive

Check:

- feed ownership email;
- spam and quarantine;
- whether the account submitted the exact canonical feed;
- whether the feed currently exposes the email expected by Amazon.

### Amazon and Audible differ

Allow for catalogue propagation delay. Confirm that the Amazon account owns the show before raising a support case. Record each platform URL separately because availability and presentation may not update simultaneously.

## 6.8 Official references

- Amazon Music for Podcasters: Add your podcast  
  https://podcasters.amazon.com/submit-rss
- Amazon Music for Podcasters: Frequently asked questions  
  https://podcasters.amazon.com/frequently-asked-questions
- Amazon Music for Podcasters  
  https://podcasters.amazon.com/
- Amazon Music for Podcasters: Terms and conditions  
  https://podcasters.amazon.com/terms-of-service

---

# 7. iHeartRadio

## 7.1 Important regional limitation

iHeart’s self-service podcaster portal is currently available only to people located in:

- United States;
- Canada;
- Mexico;
- Australia;
- New Zealand.

IRIS is operating from Portugal, so the normal self-service portal is not the dependable primary path.

Do not spoof the account location. That creates an avoidable terms and support problem.

For a publisher outside the supported regions, iHeart instructs creators whose hosting provider cannot submit on their behalf to use iHeart’s **Contact Us** route.

## 7.2 Recommended Portugal workflow

1. Ensure the RSS feed is public, valid, and exposes the organisational verification email.
2. Open iHeart’s podcaster help section.
3. Use **Contact Us** for a podcast-submission request from an unsupported self-service region.
4. Provide:
   - show title;
   - canonical RSS feed URL;
   - feed ownership email;
   - publishing organisation;
   - country of operation;
   - confirmation that IRIS is the podcast host;
   - public website URL;
   - a concise request to add the show to iHeartRadio.
5. Accept the iHeartRadio Destination / Content License Agreement when requested.
6. Complete any ownership verification sent to the feed email.
7. Retain the support case number in IRIS.
8. Confirm the public iHeartRadio show page after approval.

Because this is a support-assisted path, the exact form and response sequence may change. The durable requirements are the canonical feed, matching ownership email, rights confirmation, and support record.

## 7.3 Self-service steps for an eligible account

Use this path only when the responsible publisher is genuinely located in a supported region.

1. Open the iHeart podcaster portal.
2. Start a new podcast submission.
3. Enter the canonical IRIS RSS feed URL.
4. Use the same email address that appears in the RSS feed.
5. Review the identified show.
6. Accept the applicable terms and content licence agreement.
7. Request verification.
8. Complete the verification sent by email.
9. Confirm the show appears in the podcaster dashboard.
10. Record the public show URL and submission details in IRIS.

## 7.4 Definition of done

iHeartRadio is connected when:

- the show has been accepted;
- the public iHeart show page works;
- at least one episode plays;
- the support case or portal account is recorded;
- the public URL is stored in IRIS;
- the team knows whether future account changes must go through the portal or support.

## 7.5 Ongoing publishing

After connection:

- publish through the IRIS RSS feed;
- keep the feed email accessible;
- allow iHeart to poll the feed;
- retain the original support case if the connection was established manually;
- use the podcaster portal where available for supported management actions.

## 7.6 Updating the feed URL

For portal-managed shows, iHeart documents an **Update RSS Feed URL** action under **Manage Podcast**.

A safe migration should:

1. preserve the old feed with a permanent redirect;
2. preserve all episode GUIDs;
3. enter and verify the new feed in the portal, or request the change through support;
4. accept any updated terms prompt;
5. verify the public listing before retiring the old feed.

## 7.7 Troubleshooting

### Verification email does not arrive

iHeart recommends:

- checking spam;
- verifying that the submission email matches the email in the RSS feed;
- adding `podcasts@iheartradio.com` to contacts.

### Email mismatch

Update the public feed email first, confirm the changed RSS XML is live, and then resubmit. Do not use a different personal email merely to get past the form.

### Portal inaccessible from Portugal

Use the official Contact Us path. Do not build browser automation or a proxy workaround for a one-time directory submission.

## 7.8 Official references

- iHeartRadio: Submitting a podcast  
  https://help.iheart.com/hc/en-us/articles/228920687-Submitting-a-podcast-to-iHeartRadio
- iHeartRadio podcaster portal  
  https://podcasters.iheart.com/
- iHeartRadio: Email does not match RSS feed  
  https://help.iheart.com/hc/en-us/articles/5200314191245-What-do-I-do-if-the-email-I-am-using-to-submit-does-not-match-the-one-in-my-RSS-feed
- iHeartRadio: Submission and verification troubleshooting  
  https://help.iheart.com/hc/en-us/articles/5200215088269-I-am-having-trouble-submitting-verifying-my-podcast
- iHeartRadio: Updating the RSS feed URL  
  https://help.iheart.com/hc/en-us/articles/13406420908557-Updating-RSS-Feed-in-Podcaster-Portal

---

# 8. Pocket Casts

## 8.1 What the connection does

Pocket Casts indexes and periodically parses the IRIS RSS feed. It does not provide a conventional creator dashboard for managing a public show. The feed remains the management interface.

This is simpler than Spotify or Apple: submit the feed, then keep the feed valid.

## 8.2 Prerequisites

Before starting:

- ensure the feed is valid and public;
- ensure the show is intended to be public;
- ensure the feed does not contain `<itunes:block>Yes</itunes:block>`;
- have either the RSS feed URL or an Apple Podcasts link available.

Use the canonical RSS URL rather than the Apple link when IRIS is establishing the original source relationship.

## 8.3 Initial connection steps

Option A, preferred:

1. Open the Pocket Casts podcast submission form.
2. Paste the canonical IRIS RSS feed URL.
3. Submit the feed.
4. Review any parser error shown by the submission form.
5. Correct the IRIS feed if necessary and resubmit.
6. Wait for the show to appear in Pocket Casts search.
7. Open the listing and verify the show and episode metadata.

Option B:

1. Open Pocket Casts in an app.
2. Paste the RSS feed URL into the podcast search field.
3. Search for the feed.
4. This can cause Pocket Casts to submit and parse a feed that is not already indexed.

Option C:

- submit the Apple Podcasts show link instead of the RSS feed.

Use Option C only if the canonical RSS form is failing for a platform-specific reason. The feed itself should still be fixed rather than Apple being used as permanent masking tape.

## 8.4 Definition of done

Pocket Casts is connected when:

- the show appears in Pocket Casts search;
- the public listing opens;
- at least one episode plays;
- title, artwork, and description match the IRIS feed;
- the Pocket Casts share URL is recorded in IRIS.

There is no creator account to claim in the same sense as Spotify or Castbox.

## 8.5 Ongoing publishing

Pocket Casts periodically downloads the RSS feed to:

- discover new episodes;
- update show and episode metadata;
- update artwork;
- verify feed availability.

All ordinary corrections should be made in IRIS.

## 8.6 Updating the feed URL

Pocket Casts recommends redirecting the old feed to the new feed so its parser can update the listing automatically.

If the old feed is unavailable, contact Pocket Casts support with:

- current listing or share link;
- old feed URL;
- new canonical feed URL;
- evidence that the publisher controls the show.

## 8.7 Troubleshooting

### Submission form rejects the feed

Use the error message to identify the exact feed problem. Pocket Casts also recommends external feed validators, but the IRIS publication validator should remain the first line of defence.

### Show does not appear in public search

Check whether the feed contains `<itunes:block>Yes</itunes:block>`. Pocket Casts treats this as a private-feed signal.

### Metadata or artwork is stale

Pocket Casts updates automatically but not instantly. Verify the current RSS first. For artwork, use a new versioned image URL rather than overwriting the old object.

## 8.8 Official references

- Pocket Casts: Submitting podcasts  
  https://support.pocketcasts.com/knowledge-base/submitting-podcasts/
- Pocket Casts submission form  
  https://pocketcasts.com/submit
- Pocket Casts: Podcast search and automatic submission  
  https://support.pocketcasts.com/knowledge-base/podcast-search/
- Pocket Casts: Feed parser  
  https://support.pocketcasts.com/knowledge-base/about-pocket-casts-feed-parser/
- Pocket Casts: Updating a podcast for authors  
  https://support.pocketcasts.com/knowledge-base/how-to-update-a-podcast-for-authors/

---

# 9. Castbox

## 9.1 What the connection does

Castbox accepts the RSS feed and allows the publisher to claim ownership of the resulting channel in Castbox Creator Studio. Claiming does not change IRIS hosting or syndication.

## 9.2 Prerequisites

Before starting:

- search Castbox to check whether the show already exists;
- use an organisation-controlled Castbox login;
- ensure the RSS feed exposes a monitored ownership email;
- ensure the feed is public and valid.

Do not create a duplicate if Castbox has already indexed the feed. Claim the existing channel.

## 9.3 Initial connection steps

1. Open the Castbox desktop site.
2. Sign in using the organisation-controlled account. Castbox supports several identity providers, including Apple and Google.
3. Open **Creator Studio**.
4. Go to the **Channels** tab.
5. Select **Claim Ownership**.
6. Paste the canonical IRIS RSS feed URL into the claim form.
7. Enter the same email address displayed in the RSS feed.
8. Submit the claim.
9. Check the organisational mailbox for the Castbox ownership email.
10. Check spam if it is not visible.
11. Open the link in the Castbox email.
12. Review the show information and applicable licence agreement.
13. Select **Confirm**.
14. Return to Creator Studio and verify that the show appears as a claimed channel.
15. Optionally associate the intended social profiles.
16. Record the public Castbox channel URL and account details in IRIS.

## 9.4 Definition of done

Castbox is connected when:

- the channel is claimed in Creator Studio;
- it appears in the public Castbox directory;
- at least one episode plays;
- the public URL is recorded in IRIS;
- the organisation-controlled account has access.

## 9.5 Ongoing publishing

After connection:

- publish through IRIS;
- Castbox reads the RSS feed for new episodes and updates;
- manage Castbox-specific channel options in Creator Studio;
- retain the feed ownership email for future account recovery or migration.

## 9.6 Updating the feed URL

For an externally hosted show, use a controlled feed migration:

1. maintain a permanent redirect from the old feed;
2. preserve episode GUIDs;
3. update Apple Podcasts Connect where relevant;
4. include the standard new-feed indication in the RSS migration where appropriate;
5. allow Castbox time to recognise the replacement feed;
6. verify that subscribers and play history remain attached to the published channel.

Castbox states that it can follow an updated Apple feed URL or the appropriate feed migration tag and may create a new channel internally while unpublishing the old one and syncing subscribers and plays.

## 9.7 Troubleshooting

### Email does not match

Open the public RSS feed and check the email value actually exposed in the XML. Correct it in IRIS, publish the feed, and retry after the new value is publicly visible.

### Show already exists but is unclaimed

Use **Claim Ownership** with the existing show or feed. Do not submit a second equivalent channel.

### Claim email does not arrive

Check spam, confirm the feed email, and allow for feed-cache delay after changing the address.

## 9.8 Official references

- Castbox: Submit and claim a podcast  
  https://helpcenter.castbox.fm/portal/en/kb/articles/submit-my-podcast
- Castbox: Claim ownership  
  https://helpcenter.castbox.fm/portal/en/kb/articles/claim-your-podcast
- Castbox: Update an RSS feed  
  https://helpcenter.castbox.fm/portal/en/kb/articles/update-my-rss-feed-on-castbox
- Castbox: Find the RSS URL  
  https://helpcenter.castbox.fm/portal/en/kb/articles/find-my-rss-url

---

# 10. Recommended launch order

For each IRIS show, connect platforms in this order:

1. **Spotify**  
   Fast ownership verification and an important discovery platform.

2. **Apple Podcasts**  
   The most demanding validation pass. Fixing Apple issues early improves the feed for many other clients.

3. **YouTube / YouTube Music**  
   Requires a separate ingestion and publish cycle, so start it before launch day.

4. **Amazon Music / Audible**  
   Straightforward RSS claim and ownership confirmation.

5. **Pocket Casts**  
   Simple feed submission with no creator-dashboard dependency.

6. **Castbox**  
   Feed submission plus ownership claim.

7. **iHeartRadio**  
   Valuable for North American reach, but the Portugal-based operation requires the support-assisted route and may take more human handling.

This order is operational, not a ranking of global audience size.

---

# 11. Master connection checklist

Use this once per show.

## Feed

- [ ] Canonical RSS URL is final.
- [ ] Feed validates.
- [ ] At least one episode is published.
- [ ] Artwork is compliant.
- [ ] Audio supports `GET`, `HEAD`, and range requests.
- [ ] Ownership email is public and monitored.
- [ ] Episode GUIDs are immutable.
- [ ] No unintended private or blocking tag is present.

## Spotify

- [ ] Show submitted or found as hosted somewhere else.
- [ ] Eight-digit email verification completed.
- [ ] Show claimed in Spotify for Creators.
- [ ] Team access configured.
- [ ] Public URL recorded.

## Apple Podcasts

- [ ] Apple Podcasts Connect account ready.
- [ ] RSS show added.
- [ ] Content rights confirmed.
- [ ] Contact supplied.
- [ ] Availability configured.
- [ ] Feed validation passed.
- [ ] Review approved.
- [ ] Public URL and identifier recorded.

## YouTube

- [ ] Correct organisation channel selected.
- [ ] Advanced-feature access confirmed.
- [ ] RSS terms accepted.
- [ ] Email verification completed.
- [ ] Historical import scope selected.
- [ ] Visibility chosen.
- [ ] Episodes ingested.
- [ ] Podcast explicitly published.
- [ ] Public URL recorded.

## Amazon Music / Audible

- [ ] Canonical feed submitted.
- [ ] Correct show confirmed.
- [ ] Terms accepted.
- [ ] Ownership confirmed.
- [ ] Amazon Music URL recorded.
- [ ] Audible presence checked and recorded.

## iHeartRadio

- [ ] Portugal support-assisted submission opened.
- [ ] Case number recorded.
- [ ] Verification completed.
- [ ] Show accepted.
- [ ] Public URL recorded.

## Pocket Casts

- [ ] Feed submitted.
- [ ] Listing appears in search.
- [ ] Playback tested.
- [ ] Share URL recorded.

## Castbox

- [ ] Existing listing checked.
- [ ] Ownership claim submitted.
- [ ] Email verification completed.
- [ ] Channel claimed.
- [ ] Public URL recorded.

---

# 12. Feed migration protocol for all platforms

A feed URL migration is the highest-risk routine operation in podcast distribution. Handle it as a controlled release.

## Before migration

- freeze unrelated feed metadata changes;
- export the current feed and platform connection records;
- confirm all published GUIDs;
- keep all existing enclosure URLs alive;
- prepare the new feed with identical show and episode identity;
- validate the new feed independently.

## Migration

1. Publish the new feed.
2. Configure a permanent redirect from the old feed to the new feed.
3. Preserve every existing episode GUID.
4. Preserve publication dates unless intentionally correcting them.
5. Update platform dashboards that expose a feed-update control.
6. Retain the old URL and media infrastructure during propagation.
7. Check Spotify, Apple, YouTube, Amazon, iHeart, Pocket Casts, and Castbox separately.

## After migration

- verify that no platform created a duplicate show;
- verify that existing followers remain attached;
- verify that old episodes are still present;
- publish one controlled test update;
- monitor old-feed requests before considering retirement;
- retain redirects indefinitely where practical.

Do not solve a feed migration by deleting the old show and submitting a new one. That discards accumulated audience continuity to save a little operational patience, a famously bad exchange rate.

---

# 13. Operational ownership

Assign three explicit responsibilities per show:

### Editorial owner

Responsible for:

- title, description, artwork, rights, and publication approval;
- explicit-content classification;
- public corrections and withdrawals.

### Technical owner

Responsible for:

- feed and media availability;
- validation;
- redirects;
- enclosure integrity;
- incident response.

### Distribution owner

Responsible for:

- platform accounts;
- initial submissions;
- verification emails;
- approval tracking;
- platform URLs;
- support cases.

One person may hold more than one role in a small team, but the responsibilities should not dissolve into “someone probably did it.”

---

# 14. Platform connection completion rule for IRIS

A directory connection should be marked **Connected** only when:

1. the platform has accepted or indexed the show;
2. the public show page works;
3. at least one episode plays;
4. the correct organisation account or support case controls the relationship where applicable;
5. the external URL and identifier are recorded;
6. the canonical RSS feed remains the source of future episodes;
7. a named IRIS staff owner is responsible for the connection.

A submitted form is not a completed connection. It is merely a hopeful envelope sliding under a large company’s door.

---

# 15. Source note

These instructions were verified against official platform documentation available on 2 August 2026. Platform interfaces and eligibility rules can change. Before onboarding the first production show, the operator should open the linked official instructions and confirm that the visible interface still matches this guide.
