<!--
  This file IS the site navigation (mkdocs-literate-nav reads it in place of a `nav:`
  block in mkdocs.yml). It lives in site-overlay/ rather than in docs-pub/ because
  docs-pub/ is overwritten wholesale on every sync from the METIS source repo.

  Every published page must appear here exactly once — .github/scripts/check_nav_coverage.py
  fails the build otherwise. Order is meaningful: it sets the sidebar order and the
  prev/next footer links. Order IRIS job pages by pipeline position, not alphabetically.
-->

- [Home](index.md)
- [METIS Docs](docs-pub/index.md)
    - Start here
        - [Getting started — navigating METIS](docs-pub/web/app/getting-started.md)
        - [Focus: the holon scoping model](docs-pub/web/app/focus-and-scoping.md)
        - [Apps](docs-pub/web/app/apps.md)
        - [Concepts diagram](docs-pub/core/concepts-diagram.md)
    - Core
        - [Working with people & orgs](docs-pub/metis_apps/metis/people-and-orgs.md)
        - [Holons and classes](docs-pub/metis_apps/metis/holons-and-classes.md)
        - [Additional fields](docs-pub/metis_apps/metis/info-fields.md)
        - [Journeys](docs-pub/core/JOURNEY.md)
        - [Access & permissions (user view)](docs-pub/core/access-and-permissions.md)
        - [Permissions and roles](docs-pub/core/PERMISSIONS.md)
        - [Using the Chrome extension](docs-pub/extension/using-the-extension.md)
    - Coherence
        - [Events & conversations](docs-pub/metis_apps/coherence/events-and-conversations.md)
        - [IRIS](docs-pub/metis_apps/coherence/iris/user-benefit-iris.md)
            - [Using IRIS — walkthrough](docs-pub/metis_apps/coherence/iris/using-iris.md)
            - [Participant review guide](docs-pub/metis_apps/coherence/iris/participant-approval.md)
            - [Job reference](docs-pub/metis_apps/coherence/iris/jobs/index.md)
                - [1. Recording Downloader](docs-pub/metis_apps/coherence/iris/jobs/realtimekit-downloader.md)
                - [2. Transcript Importer](docs-pub/metis_apps/coherence/iris/jobs/transcript-importer.md)
                - [3. Google Transcribe](docs-pub/metis_apps/coherence/iris/jobs/google-transcribe.md)
                - [4. Video Editor](docs-pub/metis_apps/coherence/iris/jobs/video-editor.md)
                - [5. Content Generator](docs-pub/metis_apps/coherence/iris/jobs/content-generator.md)
                - [5a. Content Generator — prompts](docs-pub/metis_apps/coherence/iris/jobs/content-generator-prompts.md)
                - [6. Cover Image Generator](docs-pub/metis_apps/coherence/iris/jobs/cover-image-generator.md)
                - [7–9, 15. YouTube publishing](docs-pub/metis_apps/coherence/iris/jobs/youtube-uploader.md)
                - [7a. YouTube — setup](docs-pub/metis_apps/coherence/iris/jobs/youtube-uploader-setup.md)
                - [10. Cloud Storage Migrator](docs-pub/metis_apps/coherence/iris/jobs/cloud-storage-migrator.md)
                - [11. Podcast Uploader](docs-pub/metis_apps/coherence/iris/jobs/podcast-uploader.md)
                - [12–13. Publish Notifier & Waiter](docs-pub/metis_apps/coherence/iris/jobs/publish-notifier.md)
                - [14. Approval Waiter (legacy)](docs-pub/metis_apps/coherence/iris/jobs/approval-waiter.md)
                - [16. LinkedIn Page Publisher](docs-pub/metis_apps/coherence/iris/jobs/linkedin-publisher.md)
                - [17. LinkedIn Member Publisher](docs-pub/metis_apps/coherence/iris/jobs/linkedin-member-publisher.md)
                - [18. Publish Live Notifier](docs-pub/metis_apps/coherence/iris/jobs/publish-live-notifier.md)
                - [19. Telegram Distributor](docs-pub/metis_apps/coherence/iris/jobs/telegram-distributor.md)
        - [CoCo agent](docs-pub/metis_apps/coherence/coco-agent.md)
    - The Gathering
        - [Camps & local gatherings](docs-pub/metis_apps/gathering/camps-and-gatherings.md)
        - [Experiences (camp programme)](docs-pub/metis_apps/gathering/experiences.md)
        - [Experience configuration](docs-pub/metis_apps/gathering/experience-config.md)
        - [Experience images — how-to](docs-pub/metis_apps/gathering/experience-images-howto.md)
    - Other apps
        - [Audax — quests & missions](docs-pub/metis_apps/audax/quests-and-missions.md)
        - [Outreach — LinkedIn](docs-pub/metis_apps/outreach/linkedin-outreach.md)
        - [Invite — signup](docs-pub/web/invite/signup.md)
    - [API reference](docs-pub/api/API.md)
        - [App API playbook — /api/](docs-pub/api/PLAYBOOK.md)
        - [Coherence API playbook](docs-pub/api/coherence-PLAYBOOK.md)
        - [Outreach API playbook](docs-pub/api/outreach-PLAYBOOK.md)
        - [Conversation JSON fields](docs-pub/api/CONVERSATION_JSON_FIELDS.md)
- [Automation](automation/index.md)
    - [LinkedIn automation](automation/linkedin-automation/index.md)
    - [METIS API](automation/metis/index.md)
    - [Google Sheets](automation/google-sheets/index.md)
- [Tags](tags.md)
- Project
    - [Contributing](CONTRIBUTING.md)
    - [Docs conventions](DOCS-CONVENTIONS.md)
