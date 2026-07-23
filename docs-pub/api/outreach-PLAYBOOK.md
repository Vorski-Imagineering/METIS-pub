# Outreach API playbook

This playbook covers searching a user's private Outreach network and managing
its human/agent-driven campaign Memberships. LinkedIn export uploads are
web-only; this API never calls LinkedIn and does not send messages or connection
requests directly. It can create and manage work in the same Outreach action
queue used by the browser extension.

The live schema at `/api/v1/openapi.json` and Swagger UI at `/api/v1/docs` are
authoritative.

## Authentication and access

Use the standard `/api/v1/` 24-hour bearer token described in [API.md](API.md).
Browser session cookies and the static service token do not authenticate this
surface.

An Outreach network is visible only to a global editor or a user with direct
team-active edit access to that Holon. Inaccessible networks return `404`, and
their Memberships are removed from Person membership and responsible-worklist
responses. Imported People themselves remain part of the shared METIS Person
directory.

The examples assume:

```sh
export METIS_URL="https://your-metis.example"
export METIS_TOKEN="your-24-hour-token"
export NETWORK_ID="123"
```

## Discover the network

```sh
curl -sS "$METIS_URL/api/v1/holons?class=outreach-network&limit=100" \
  -H "Authorization: Bearer $METIS_TOKEN"
```

The importing actor normally sees one Outreach network. Use the returned Holon
`id` for subsequent calls.

## Search imported connections

The importer represents a connection as a Membership using the Journey slug
`outreach-linkedin-network`.

```sh
curl -sS \
  "$METIS_URL/api/v1/holons/$NETWORK_ID/memberships?journey=outreach-linkedin-network&q=climate&sort=name&limit=50&offset=0" \
  -H "Authorization: Bearer $METIS_TOKEN"
```

Supported filters are:

| Parameter | Meaning |
| --- | --- |
| `q` | Case-insensitive Person name, description, contact channel, LinkedIn headline/about/location, or current title/company substring. |
| `journey` | Exact Membership Journey slug. |
| `step_slug` | Exact current step slug. |
| `responsible_person_id` | Exact responsible Person ID. |
| `follow_up` | `overdue`, `today`, `future`, or `none`. |
| `sort` | `name`, `-name`, `follow_up_after`, or `-follow_up_after`. |
| `limit` | Page size, from 1 to 200. |
| `offset` | Zero-based page offset. |

`count` is the number of items in the current page, not a total. Continue with
`offset + limit` while `has_more` is `true`. Each item includes stable
`journey_slug` and `step_slug` fields.

## Find People for a campaign

Search the shared Person directory independently of network Memberships:

```sh
curl -sS "$METIS_URL/api/v1/people?q=Ada&limit=100&offset=0" \
  -H "Authorization: Bearer $METIS_TOKEN"
```

This permits adding People who were not in the LinkedIn export.

## Bulk-add campaign Memberships

Add between 1 and 500 People to the seeded `outreach-prospecting` Journey:

```sh
curl -sS -X POST \
  "$METIS_URL/api/v1/holons/$NETWORK_ID/memberships:bulk-add" \
  -H "Authorization: Bearer $METIS_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "journey": "outreach-prospecting",
    "items": [
      {
        "person_id": 501,
        "step_slug": "candidate",
        "responsible_person_id": 42,
        "follow_up_after": "2026-08-01",
        "note": "Strong fit for the research cohort"
      },
      {
        "person_id": 502,
        "step_slug": "researching"
      }
    ]
  }'
```

The response reports `created`, `already_present`, and `errors`, plus one result
per input item. Invalid Person IDs, steps, responsible People, or dates are
item-level errors; other valid items still run.

Outreach uses `(person, holon, journey)` as the logical identity. A request made
after the first one has completed returns `already_present` and does not mutate
the existing step, responsible person, follow-up date, or notes. METIS does not
currently provide a database-level uniqueness guarantee for simultaneous
generic Membership writes, so clients should not issue overlapping bulk-add
requests for the same Holon.

The infrastructure Journeys `outreach-network-owner` and
`outreach-linkedin-network` reject generic bulk addition.

## Review a campaign

```sh
curl -sS \
  "$METIS_URL/api/v1/holons/$NETWORK_ID/memberships?journey=outreach-prospecting&step_slug=researching&sort=follow_up_after&limit=100" \
  -H "Authorization: Bearer $METIS_TOKEN"
```

The seeded step slugs are `candidate`, `researching`, `ready-to-connect`,
`connection-requested`, `connected`, `paused`, and `do-not-contact`.

## Update one campaign Membership

A note is required on each state-changing update so the action has human-readable
context. Fields omitted from the request remain unchanged; an explicit `null`
clears `follow_up_after` or `responsible_person_id`.

```sh
curl -sS -X POST \
  "$METIS_URL/api/v1/memberships/987/update" \
  -H "Authorization: Bearer $METIS_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "note": "Research complete; ready for a human to connect",
    "step_slug": "ready-to-connect",
    "follow_up_after": "2026-08-05",
    "responsible_person_id": 42
  }'
```

Use `advance_step: true` instead of `step_slug` to move to the next active step.
Do not send both controls in one request.

## Read and enrich a LinkedIn profile

An external agent can attach an observed LinkedIn profile to any Person who has
a Membership on the caller's Outreach network:

```sh
curl -sS -X POST \
  "$METIS_URL/api/v1/outreach/people/123/linkedin/update?network_id=$NETWORK_ID" \
  -H "Authorization: Bearer $METIS_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "email": "profile-email@example.com",
    "headline": "Building better coordination systems",
    "about": "Profile biography…",
    "location": "Lisbon, Portugal",
    "current_position": {
      "title": "Founder",
      "company": "Example Labs"
    },
    "education": [
      {"school": "Example University", "degree": "MSc"}
    ],
    "connection_count": 500,
    "connected_on": "2026-07-19",
    "observed_at": "2026-07-22T10:00:00Z"
  }'
```

The update accepts only the documented LinkedIn fields; it does not accept an
arbitrary `Person.infos` object. Non-empty observations refresh their prior
source values, while omitted or blank values leave prior observations alone.
`email` is the source-observed LinkedIn email and does not replace the canonical
Person contact email. `connected_on` updates the caller's LinkedIn Network
Membership and is rejected when that Membership does not exist.

LinkedIn enrichment never changes the Person's canonical name, description,
contact details, or photo. Responses return both `description` and
`display_description`: the latter falls back to LinkedIn `about`, then
`headline`, only when the canonical description is blank. Responses also
return the LinkedIn `network_membership_id` and `connected_on` date when
present.

Only contacts without a linked METIS login account can be enriched. The update
route returns `403` when `Person.user_id` is set; the read route remains
available and does not change the Person.

Read the current source observation without changing it:

```sh
curl -sS \
  "$METIS_URL/api/v1/outreach/people/123/linkedin?network_id=$NETWORK_ID" \
  -H "Authorization: Bearer $METIS_TOKEN"
```

Both routes require Outreach app access and standard edit access to the selected
network. The `network_id` parameter may name the caller's own network or a
network shared through an ordinary team-active Membership. It defaults to the
caller's owned network for compatibility, or to their only accessible network
when they do not own one. The routes return `404` unless the network is
accessible and the Person has any Membership on it.

## Create message actions

An action is a queued unit of Outreach work. For a LinkedIn message, use the
campaign Membership as the target identity. METIS derives the target Person and
network from it, then applies standard Holon edit permission to that network.

```sh
curl -sS -X POST \
  "$METIS_URL/api/v1/outreach/actions:bulk-create" \
  -H "Authorization: Bearer $METIS_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "items": [
      {
        "action_type": "send_message",
        "membership_id": 987,
        "message_body": "Hello Ada — I enjoyed your recent work on…",
        "scheduled_for": "2026-08-06T10:00:00Z",
        "batch_id": "climate-founders-2026-08"
      }
    ]
  }'
```

Requests accept 1–500 items and return `created`, `already_present`, and
`errors`, plus an outcome for every item. A sequential retry reuses the same
active logical action. METIS does not claim database-level uniqueness for
overlapping requests.

`request_connection`, `send_message`, and `check_connection_state` require an
`outreach-prospecting` Membership on any Outreach network the caller may edit.
`download_profile` and `publish_post` may instead use `target_person_id`.

## Search and read actions

```sh
curl -sS \
  "$METIS_URL/api/v1/outreach/actions?action_type=send_message&status=pending&journey=outreach-prospecting&limit=50&offset=0" \
  -H "Authorization: Bearer $METIS_TOKEN"
```

The list supports `q`, `status`, `action_type`, `membership_id`, `journey`,
`step_slug`, `batch_id`, `scheduled_after`, `scheduled_before`, `sort`, `limit`,
and `offset`. `q` searches the target name and message draft. Page until
`has_more` is false.

Read one action, including its full draft, with:

```sh
curl -sS "$METIS_URL/api/v1/outreach/actions/456" \
  -H "Authorization: Bearer $METIS_TOKEN"
```

Actions are actor-scoped. Another actor's action returns `404`.

## Edit an action

Pending, failed, blocked, and rate-limited actions allow draft, scheduling, and
batch edits. Omitted fields remain unchanged; explicit `null` clears the
schedule or batch.

```sh
curl -sS -X POST \
  "$METIS_URL/api/v1/outreach/actions/456/update" \
  -H "Authorization: Bearer $METIS_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "message_body": "Revised personal message",
    "scheduled_for": null
  }'
```

## Transition an action

```sh
curl -sS -X POST \
  "$METIS_URL/api/v1/outreach/actions/456/transition" \
  -H "Authorization: Bearer $METIS_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "status": "done",
    "result_summary": "Sent in LinkedIn"
  }'
```

Supported transitions follow the queue lifecycle:

- `pending` → `running`, `done`, `blocked`, or `cancelled`;
- `running` → `done`, `failed`, `blocked`, `cancelled`, or `rate_limited`;
- `failed`, `blocked`, or `rate_limited` can return to `pending` or be
  cancelled; blocked actions may also be completed;
- `done` and `cancelled` are terminal.

A `send_message` action needs a non-empty message body before it can become
`done`. The transition endpoint records action state only: it does not change a
Membership step or create follow-up actions automatically.

## Client rules

- Treat `400` and `422` as non-retryable input errors.
- Refresh the token after `401`; do not retry blindly after `403` or `404`.
- Page until `has_more` is false.
- Use Journey and step slugs for workflow logic; display names are for humans.
- Inspect every bulk item outcome even when the HTTP status is `200`.
- Treat action `done` as a reported outcome; METIS does not independently verify
  that LinkedIn accepted a message or connection request.
- Do not infer LinkedIn state from a METIS step. Steps contain facts supplied by
  users or authorized external clients.
