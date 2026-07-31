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
        - [IRIS](docs-pub/metis_apps/coherence/iris/index.md)
            - [What IRIS does](docs-pub/metis_apps/coherence/iris/what-iris-does.md)
            - [How IRIS works](docs-pub/metis_apps/coherence/iris/how-iris-works.md)
            - [Using IRIS — walkthrough](docs-pub/metis_apps/coherence/iris/using-iris.md)
            - [Participant review guide](docs-pub/metis_apps/coherence/iris/participant-review.md)
            - [Troubleshooting](docs-pub/metis_apps/coherence/iris/troubleshooting.md)
            - [Step reference](docs-pub/metis_apps/coherence/iris/steps/index.md)
                - [1. Recording Downloader](docs-pub/metis_apps/coherence/iris/steps/realtimekit-downloader.md)
                - [2. Transcript Importer](docs-pub/metis_apps/coherence/iris/steps/transcript-importer.md)
                - [3. Google Transcribe](docs-pub/metis_apps/coherence/iris/steps/google-transcribe.md)
                - [4. Video Editor](docs-pub/metis_apps/coherence/iris/steps/video-editor.md)
                - [5. Content Generator](docs-pub/metis_apps/coherence/iris/steps/content-generator.md)
                - [5a. Content Generator — prompts](docs-pub/metis_apps/coherence/iris/writing-prompts.md)
                - [6. Cover Image Generator](docs-pub/metis_apps/coherence/iris/steps/cover-image-generator.md)
                - [7–9, 15. YouTube publishing](docs-pub/metis_apps/coherence/iris/steps/youtube-uploader.md)
                - [7a. YouTube — setup](docs-pub/metis_apps/coherence/iris/youtube-setup.md)
                - [7b. YouTube — accounts & access](docs-pub/metis_apps/coherence/iris/youtube-accounts.md)
                - [10. Cloud Storage Migrator](docs-pub/metis_apps/coherence/iris/steps/cloud-storage-migrator.md)
                - [11. Podcast Uploader](docs-pub/metis_apps/coherence/iris/steps/podcast-uploader.md)
                - [12–13. Publish Notifier & Waiter](docs-pub/metis_apps/coherence/iris/steps/publish-notifier.md)
                - [14. Approval Waiter (legacy)](docs-pub/metis_apps/coherence/iris/steps/approval-waiter.md)
                - [16. LinkedIn Page Publisher](docs-pub/metis_apps/coherence/iris/steps/linkedin-publisher.md)
                - [17. LinkedIn Member Publisher](docs-pub/metis_apps/coherence/iris/steps/linkedin-member-publisher.md)
                - [18. Publish Live Notifier](docs-pub/metis_apps/coherence/iris/steps/publish-live-notifier.md)
                - [19. Telegram Distributor](docs-pub/metis_apps/coherence/iris/steps/telegram-distributor.md)
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
        - [METIS API playbook — /api/v1/](docs-pub/api/v1-PLAYBOOK.md)
        - [Public API playbook — /public/](docs-pub/api/public-PLAYBOOK.md)
        - [App API playbook — /api/](docs-pub/api/PLAYBOOK.md)
        - [Coherence API playbook](docs-pub/api/coherence-PLAYBOOK.md)
        - [Outreach API playbook](docs-pub/api/outreach-PLAYBOOK.md)
- [Automation](automation/index.md)
    - [LinkedIn automation](automation/linkedin-automation/index.md)
    - [METIS API](automation/metis/index.md)
    - [Google Sheets](automation/google-sheets/index.md)
- [Tags](tags.md)
- Project
    - [Contributing](CONTRIBUTING.md)
    - [Docs conventions](DOCS-CONVENTIONS.md)
