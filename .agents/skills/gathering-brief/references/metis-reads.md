# METIS reads for gathering briefs

Follow `.agents/skills/metis/SKILL.md` for local sign-in, the API playbook, live-schema
checks and the existing client. Use `scripts/metis_api.py` from the repo root and
keep only the fields needed for the brief. The paths below are relative to `/api/v1`.

## Resolve the edition and team

- `GET /holons/{id}` or `GET /holons/by-slug/{slug}` for a known record. Search a name
  using `GET /holons?q=<encoded-name>`. For editions, `class=local_gathering` includes
  subclasses. The record's `info_fields` can carry `start_date`, `end_date`, `place`,
  and `timezone`. The `lifecycle` may describe publication. Use the recorded dates
  to tell whether the event itself is upcoming or has passed.
- For the caller, use `GET /auth/whoami` and `GET /people/{id}/memberships`. For a
  roster, use `GET /holons/{id}/memberships`. A current membership counts as a team
  role when its step has `{key: "team-member", value: true}` in `config_flags` on
  `GET /journeys/{slug}`. Check by journey and step slug. Team access can also inherit
  from an ancestor, so a direct roster answers who is on the gathering's own team.

## Activity and dated work

- `GET /holons/{id}/notes?limit=100` returns recent `items` and `moves`. Use the latest
  notes and actual step moves as evidence of dated change. Moves have `at`, `key`,
  `to_step`, `moved_by_label` and `count`. Deduplicate by `key` and use `count` for
  a grouped move. It is a capped feed. With a requested window extending beyond the
  returned feed, qualify activity counts. Keep raw signup fields and contact details
  out of the brief.
  Use `rollup=true` on a relevant Audax quest or mission to include descendant activity
  and identify it by `holon_id`. The organisation's own feed will miss some of this.
- `GET /holons/{id}/memberships` is the people pipeline. `GET /holons/{id}/relationships`
  adds linked organisations and other holons. Either end of a relationship can be the
  target gathering. Use the opposite end as the linked record. Check both sources
  for dated follow-ups. To find the caller's work on the gathering, filter membership
  reads by `responsible_person_id` or compare the `responsible_person.id` on each row.
  Compare `follow_up_after` to the report date and distinguish overdue, due today,
  upcoming, and undated. Group pipeline rows by journey and step slug. Each row is one
  membership or relationship, so unique people counts require deduplication by person ID.
- For work tracked in Audax, discover direct child quests with
  `GET /holons?class=quest&parent={id}` and check `GET /quests?held_by={id}` when it has
  quests. Quests come back under `items`. Read current actions with
  `GET /actions?within_id={quest_id}&group=mission&responsible=any`. That response has
  `groups`, each with `items`. `within_id` includes the quest's visible missions.
  Open actions are the default.
  Use `follow_up_after`, `step_title`, `responsible_person_id` and the returned `url`.
  Resolve unfamiliar owner IDs with `GET /people/{id}`. Check `truncated` before
  quoting totals. Use `/app/metis/holon/{id}/` or `/holon/{id}/` for holons and
  `/person/{id}/` for people on `https://app.the-gathering.earth`.

## Local readiness and coverage

- `GET /holons?class=camp&parent={id}` lists camps under the gathering. The same query
  with `class=experience` lists experiences attached directly to it. Experiences can
  also sit under camps, so state the scope or include those children for a full programme
  count. Use `GET /holons/{camp_id}/info-progress` for recorded chapter completion.
  Use the lifecycle steps for recorded publication or cancellation and the experience
  `info_fields` for programme dates. A filled chapter measures completion of METIS fields.
- For paged lists, advance `offset` until `has_more` is false. Holon search allows up
  to 100 per page and membership or relationship reads allow up to 200. For a short
  status answer, prefer filtered reads for the work being described. Give full totals
  only when the result covers the whole scope. Keep the recent activity, pipeline and
  programme counts tied to the record or child records they actually describe.
