# METIS Public API playbook

This playbook covers `/public/` — a fully open, unauthenticated, read-only JSON
projection of exactly the data already public on the site's `/view/*` pages. It
exists so external frontends (React apps, embeds, dashboards) can build their own
views over that data instead of scraping or iframing the HTML pages.

The live schema at `/public/openapi.json` and Swagger UI at `/public/docs` are
authoritative — this page is narrative and conventions, not a contract restatement.

## Where it lives

The same `/public/` paths are served from two hosts, and the responses are identical:

- the **view host**, alongside the public pages this API mirrors — that host serves
  those pages and this API and nothing else;
- the **app host**, alongside the rest of METIS.

Prefer the view host if you are building against the public data alone: it is the
smallest surface, and the one whose URL shape follows the public pages.

## Authentication

None. Every endpoint is open — there is no token, key, or cookie to send.

## What "public" means here

Nothing is decided by a boolean flag on a record. Visibility is journey/step/field
config driven, the same rule the `/view/*` pages use:

- A Membership or Holon relationship is publishable when `public-visible` is set on
  the step it currently rests on, or on its whole journey.
- A team membership publishes by the same rule, and only that rule. It used to ride on
  `team-active`, the flag that granted edit permission on the website; publication is now
  an explicit setting rather than a side effect of access.
- An info or link field is included only when its class configuration marks it
  `public_visible: true`.

This surface and `/view/*` share the exact same filtering functions
(`metis_apps/gathering/public_org_links.py`, `metis_apps/metis/public_holon_presentation.py`)
so they cannot silently drift on what counts as public. If something is missing here
that you can see on the website, it's a bug in this API, not a different rule.

## CORS

`Access-Control-Allow-Origin: *` — any origin may call this from browser JS. Only
`GET` and `OPTIONS` are allowed, and no credentials/cookies are ever sent or
accepted, so the wildcard is safe.

## Endpoints

| Endpoint | What it returns |
|---|---|
| `GET /public/domain/` | The domain/site home: the domain holon, its team, and every local gathering with its camps |
| `GET /public/orgs/{org_slug}/` | An organisation's public info/links, team, and publicly-linked camps/gatherings |
| `GET /public/gatherings/{lg_slug}/` | A local gathering: camps, team, publicly-linked orgs, and a programme teaser |
| `GET /public/gatherings/{lg_slug}/camps/{camp_slug}/` | A camp: team, related orgs grouped by journey, public info fields, programme preview |
| `GET /public/gatherings/{lg_slug}/programme/` | Aggregate public programme across a gathering and its camps (`q`, `owner` filters) |
| `GET /public/gatherings/{lg_slug}/camps/{camp_slug}/programme/` | Full public programme for one camp |
| `GET /public/gatherings/{lg_slug}/experiences/{experience_slug}/` | A gathering-owned Experience's detail page |
| `GET /public/gatherings/{lg_slug}/camps/{camp_slug}/experiences/{experience_slug}/` | A camp-owned Experience's detail page |
| `GET /public/people/{person_id}/` | A person's public page, for someone with a public role or in a public conversation video: publishable memberships only, plus their public-video conversations |

A 404 on a person/org/gathering/camp/experience endpoint means "no public record at
that address" — it does not distinguish "doesn't exist" from "exists but nothing on
it is public," matching `/view/*`'s behavior.

### `GET /public/domain/` returns the front page's own order

`local_gatherings` comes back in **roadmap order** — past to future by start date, with
an undated gathering placed at the year in its name and after any dated one in that same
year. It used to be alphabetical. The field list is unchanged, so nothing breaks; if you
relied on the order, it is now chronological.

Alongside it: `today` (the date the statuses were worked out against),
`next_gathering_slug` (the one happening now, else the next upcoming one),
`featured_gathering_slugs` (what the front page features: the one happening now and every
upcoming gathering in the current year, in date order), `faces` and `infos`.

An `infos` item's `title` is a short headline — "Tickets are open", "Three camps
joined" — and the gathering it is about is `gathering_slug` / `gathering_label`, not
part of the text. Camps that joined one gathering in the same month come as **one**
`camp_joined` item whose `camp_slugs` lists them all, so count camps from
`camp_slugs`, not from the number of items. Each gathering gains `status`, `start_date`, `end_date`, `place`, `tagline`,
`tickets_url`, `experience_count` and `photos`; each camp gains `video`. Dates are null
until a local team fills them in, and `status` falls back to the year in the gathering's
name — so an undated future gathering still reads `upcoming` rather than disappearing.

`team` on a gathering and on a camp is now the **current** team, the same rule the
gathering's own page uses. It previously included people on any step of the team journey,
which listed Retired and Signed Up people as current.

`team_memberships` — the *domain* holon's own team — is unchanged and still returned. Note
that the front page no longer draws it: its people band is built from gathering and camp
teams, so someone whose only publishable membership is on the domain holon appears in this
field but not on `/view/`.

### `GET /public/people/{person_id}/` answers what the page shows

Every list on this response comes from the same place as the person's page on `/view/`,
so the two cannot differ. Two fields are new; nothing existing was renamed or removed:

- `experience_holons` — the experiences this person holds a public role on (a
  facilitator, say), in the same shape as `camp_holons`.
- `conversations` — the conversations they took part in whose YouTube video is **public**,
  newest first. A video that has been uploaded but not yet made public is left out. Each
  carries `title`, `date`, `youtube_url`, `embed_url` (the privacy-enhanced
  `youtube-nocookie.com` embed) and `thumbnail_url`.

`org_holons` now includes organisations of a more specific kind of organisation (they
were missing before, though their own page was live). An empty list comes back as `[]`,
never omitted.

`camp_holons` now omits a camp that has no public page of its own (a camp with no
gathering above it), as the person's page on `/view/` always did.

The exact field types are in the live schema at `/public/openapi.json`.

## Not exposed here

- **Share-hash person pages and their vCard**
  (`/view/share/<id>/<hash>/`, `/view/share/<id>/<hash>/vcard/`) — these use a
  distinct, capability-URL access model (an HMAC-gated link, not "already public by
  default") and are intentionally not mirrored here. The vCard carries the full
  contact card, so it lives behind the same hash as the page offering it; there is
  no unhashed `/view/person/<id>/vcard/`.

## Rate limiting

None for now. This is fully open with zero authentication, so it is more exposed to
abuse than the other surfaces — but per this project's architecture posture, no new
infrastructure (Redis, a gateway, etc.) is added without a measured problem. If abuse
is observed, the reverse-proxy layer is the first lever, not application code.
