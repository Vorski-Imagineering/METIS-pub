# Outreach API playbook

This playbook covers searching a user's private Outreach network and managing
its human/agent-driven campaign Memberships. LinkedIn export uploads are
web-only; this API never calls LinkedIn and does not send messages or connection
requests.

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
| `q` | Case-insensitive Person name, description, or contact-channel substring. |
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

## Client rules

- Treat `400` and `422` as non-retryable input errors.
- Refresh the token after `401`; do not retry blindly after `403` or `404`.
- Page until `has_more` is false.
- Use Journey and step slugs for workflow logic; display names are for humans.
- Inspect every bulk item outcome even when the HTTP status is `200`.
- Do not infer LinkedIn state from a METIS step. Steps contain facts supplied by
  users or authorized external clients.
