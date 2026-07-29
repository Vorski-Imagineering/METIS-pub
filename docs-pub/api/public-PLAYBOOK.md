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
- A team membership counts when it sits at a step flagged `team-active` — that flag
  grants edit permission on the website and is reused here as "an actual working
  member," never as a publishing rule of its own.
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
| `GET /public/people/{person_id}/` | A person's public page: publishable memberships only |

A 404 on a person/org/gathering/camp/experience endpoint means "no public record at
that address" — it does not distinguish "doesn't exist" from "exists but nothing on
it is public," matching `/view/*`'s behavior.

## Not exposed here

- **vCard download** (`/view/person/<id>/vcard/`) — a binary/text download, not JSON;
  out of scope for a JSON API.
- **Share-hash person pages** (`/view/share/<id>/<hash>/`) — these use a distinct,
  capability-URL access model (an HMAC-gated link, not "already public by default")
  and are intentionally not mirrored here.

## Rate limiting

None for now. This is fully open with zero authentication, so it is more exposed to
abuse than the other surfaces — but per this project's architecture posture, no new
infrastructure (Redis, a gateway, etc.) is added without a measured problem. If abuse
is observed, the reverse-proxy layer is the first lever, not application code.
