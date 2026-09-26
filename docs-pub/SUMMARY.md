<!--
  This file IS the nav for the published docs section (the "METIS Docs" tab on
  docs.the-gathering.earth). It lives here, beside the pages, because the pages are
  here: METIS-pub's root SUMMARY.md cross-links to this file with
  `- [METIS Docs](docs-pub/)` and owns only its own top level. Five docs deploys broke
  because the menu and the pages lived in two repos with nothing checking they agreed
  (METIS-pub#434).

  Every .md under docs/pub/ must appear here exactly once, and every link must resolve —
  deploy/check_docs_pub.py enforces both at merge, before the site build can break.

  Write paths relative to docs/pub/, as the files are named here. Links to README.md are
  rewritten to index.md on the site by METIS-pub's assemble_docs.py, so a README is
  written README.md.

  Order is meaningful: it sets the sidebar order and the prev/next footer links. The
  first entry must be README.md — mkdocs' navigation.indexes makes a section's first
  child its landing page only when that child is its index.md. Order IRIS step pages by
  pipeline position, not alphabetically.
-->

- [Overview](README.md)
- Start here
    - [Getting started — navigating METIS](web/app/getting-started.md)
    - [Focus: the holon scoping model](web/app/focus-and-scoping.md)
    - [Apps](web/app/apps.md)
    - [Concepts diagram](core/concepts-diagram.md)
- Core
    - [Working with people & orgs](metis_apps/metis/people-and-orgs.md)
    - [Holons and classes](metis_apps/metis/holons-and-classes.md)
    - [Additional fields](metis_apps/metis/info-fields.md)
    - [Journeys](core/JOURNEY.md)
    - [Access & permissions (user view)](core/access-and-permissions.md)
    - [Permissions and roles](core/PERMISSIONS.md)
    - [Publication: what the public site shows](core/PUBLICATION.md)
    - [Using the Chrome extension](extension/using-the-extension.md)
        - [Outreach with the extension, day to day](extension/outreach-in-your-day.md)
- Coherence
    - [Events & conversations](metis_apps/coherence/events-and-conversations.md)
    - [IRIS](metis_apps/coherence/iris/README.md)
        - [What IRIS does](metis_apps/coherence/iris/what-iris-does.md)
        - [How IRIS works](metis_apps/coherence/iris/how-iris-works.md)
        - [Using IRIS — walkthrough](metis_apps/coherence/iris/using-iris.md)
        - [Participant review guide](metis_apps/coherence/iris/participant-review.md)
        - [Troubleshooting](metis_apps/coherence/iris/troubleshooting.md)
        - [Step reference](metis_apps/coherence/iris/steps/README.md)
            - [1. Recording Downloader](metis_apps/coherence/iris/steps/realtimekit-downloader.md)
            - [2. Transcript Importer](metis_apps/coherence/iris/steps/transcript-importer.md)
            - [3. Google Transcribe](metis_apps/coherence/iris/steps/google-transcribe.md)
            - [4. Video Editor](metis_apps/coherence/iris/steps/video-editor.md)
            - [5. Content Generator](metis_apps/coherence/iris/steps/content-generator.md)
            - [5a. Content Generator — prompts](metis_apps/coherence/iris/writing-prompts.md)
            - [6. Cover Image Generator](metis_apps/coherence/iris/steps/cover-image-generator.md)
            - [7–9, 15. YouTube publishing](metis_apps/coherence/iris/steps/youtube-uploader.md)
            - [7a. YouTube — setup](metis_apps/coherence/iris/youtube-setup.md)
            - [7b. YouTube — accounts & access](metis_apps/coherence/iris/youtube-accounts.md)
            - [10. Cloud Storage Migrator](metis_apps/coherence/iris/steps/cloud-storage-migrator.md)
            - [11. Podcast Publisher](metis_apps/coherence/iris/steps/podcast-publisher.md)
            - [11a. Podcast RSS platform connection guide](metis_apps/coherence/iris/IRIS-podcast-RSS-platform-connection-guide.md)
            - [12–13. Publish Notifier & Waiter](metis_apps/coherence/iris/steps/publish-notifier.md)
            - [14. Approval Waiter (legacy)](metis_apps/coherence/iris/steps/approval-waiter.md)
            - [16. LinkedIn Page Publisher](metis_apps/coherence/iris/steps/linkedin-publisher.md)
            - [16a. LinkedIn Link Resolver](metis_apps/coherence/iris/steps/linkedin-link-resolver.md)
            - [17. LinkedIn Member Publisher](metis_apps/coherence/iris/steps/linkedin-member-publisher.md)
            - [18. Publish Live Notifier](metis_apps/coherence/iris/steps/publish-live-notifier.md)
            - [19. Telegram Distributor](metis_apps/coherence/iris/steps/telegram-distributor.md)
    - [CoCo agent](metis_apps/coherence/coco-agent.md)
- The Gathering
    - [Camps & local gatherings](metis_apps/gathering/camps-and-gatherings.md)
    - [Experiences (camp programme)](metis_apps/gathering/experiences.md)
    - [Experience configuration](metis_apps/gathering/experience-config.md)
    - [Experience images — how-to](metis_apps/gathering/experience-images-howto.md)
- Other apps
    - [Audax — quests & missions](metis_apps/audax/quests-and-missions.md)
    - [Outreach — LinkedIn](metis_apps/outreach/linkedin-outreach.md)
    - [Invite — signup](web/invite/signup.md)
- Brands
    - [Brand pages](web/view/brand-pages.md)
- [API reference](api/API.md)
    - [METIS API playbook — /api/v1/](api/v1-PLAYBOOK.md)
    - [Public API playbook — /public/](api/public-PLAYBOOK.md)
    - [App API playbook — /api/](api/PLAYBOOK.md)
    - [Coherence API playbook](api/coherence-PLAYBOOK.md)
    - [Outreach API playbook](api/outreach-PLAYBOOK.md)
