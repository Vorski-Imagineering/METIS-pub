# LinkedIn imports and Outreach campaigns

METIS Outreach turns a LinkedIn connections export into searchable METIS
People and a human-managed outreach workflow. It does not scrape LinkedIn,
send connection requests, send messages, or check whether a connection has
changed.

## What an import creates

The first import creates one private **LinkedIn Network** Holon for your METIS
Person. Later imports reuse it.

Each valid connection row:

1. matches an existing METIS Person by normalized LinkedIn profile URL, or
   creates a shared METIS Person with the exported name and LinkedIn URL; and
2. gives that Person a **LinkedIn Network** Membership on your network Holon.

Imported People join the shared METIS directory. Other API users can find their
name and LinkedIn URL through ordinary Person search, but the API does not
return who is in your network or your campaign workflow unless the caller has
been given edit access to your network Holon.

METIS deliberately does not store exported company, position, connection date,
or email. Those values are included in the import report so you can see what
was omitted. LinkedIn exports do not always contain email addresses, and METIS
does not use email for matching.

## Download your LinkedIn data

Follow LinkedIn's current
[data export instructions](https://www.linkedin.com/help/linkedin/answer/a566336/export-connections-from-linkedin?lang=en)
and request your connections data. LinkedIn may provide `Connections.csv`
directly or place it inside a larger ZIP archive. You can upload either form.

Do not edit the header row. METIS accepts LinkedIn's explanatory lines before
the header.

## Import connections

1. Open **Outreach → LinkedIn Imports**.
2. Select `Connections.csv`, or the LinkedIn ZIP containing exactly one file
   named `Connections.csv`.
3. Choose **Upload and preview**. Uploading and previewing do not change People
   or Memberships.
4. Review the totals and row outcomes:
   - `created` means a new Person will be made;
   - `matched` means the exact LinkedIn URL found one existing Person;
   - `already_present` means the exact network Membership already exists;
   - an error means that row will be skipped.
5. Choose **Commit import**. Valid rows are committed even if other rows fail.
6. Download the CSV report from the result page. Reports expire after seven
   days.

The result page links to your network Holon. Re-importing the same export after
the prior import completes reuses the Person and the exact Membership. METIS
blocks a second import from committing while one is already running for that
network.

### Matching rules

METIS normalizes ordinary LinkedIn person URLs such as
`https://linkedin.com/in/example?trk=...` to
`https://www.linkedin.com/in/example/`.

- One exact match in your network is reused first.
- Otherwise, one exact match in the shared Person directory is reused.
- More than one matching Person is ambiguous, so the row is skipped.
- A row with no valid `/in/` URL is skipped.
- A new Person also requires a name.
- An existing Person's name and other fields are never overwritten by this
  importer.

The report is the authoritative row-by-row record of what happened. It contains
the source values, matched or created IDs, warnings, errors, and a
`not_imported_fields` column.

## Set up an Outreach campaign

A campaign is not a separate list object. It is the **Outreach Prospecting**
Journey on the same network Holon. This lets one Person have both a LinkedIn
Network Membership and an independent campaign Membership.

The fastest route from the web interface is:

1. Open **Outreach → LinkedIn Contacts**.
2. Search by name or LinkedIn profile URL and choose the campaign Journey.
3. Filter to **Not yet added**, select contacts individually or select the
   current page, and choose their starting step.
4. Choose **Add selected**. The new Memberships are assigned to you.

The page shows 50 contacts at a time and can select the current page in one
click. Existing Memberships in the selected Journey are shown but are not
changed.

You can also add one Person at a time from the network Holon:

1. Open the network Holon from an import result.
2. In **People**, choose **Add Existing**.
3. Find the Person, select **Outreach Prospecting**, choose the starting step,
   and optionally set the responsible person, follow-up date, and note.
4. Add the Membership. Repeat for the People in the campaign.
5. Open a person's Membership card to change its step, responsibility,
   follow-up date, or notes as work progresses.

People do not need to have appeared in your LinkedIn export to join the
Prospecting Journey.

The initial workflow is:

| Step | Use it when |
| --- | --- |
| Candidate | The Person may fit the campaign. |
| Researching | You are gathering context before contact. |
| Ready to Connect | Research is complete and a human can act. |
| Connection Requested | A human or an external tool reports that a request was sent. |
| Connected | A human or external tool reports that the connection is active. |
| Paused | No action should be taken for now. |
| Do Not Contact | The Person must not be contacted in this campaign. |

These are workflow facts recorded in METIS. METIS does not verify them against
LinkedIn.

## Use Claude or another API client

The Outreach backend uses the standard token-authenticated METIS API. There is
no `/outreach/contacts` endpoint and no import endpoint. Uploads remain in the
web interface.

The usual API flow is:

1. discover your network with
   `GET /api/v1/holons?class=outreach-network`;
2. search its Memberships with
   `GET /api/v1/holons/{holon_id}/memberships`;
3. find additional People with `GET /api/v1/people?q=...`;
4. add up to 500 People to `outreach-prospecting` with
   `POST /api/v1/holons/{holon_id}/memberships:bulk-add`; and
5. update individual Memberships with
   `POST /api/v1/memberships/{membership_id}/update`.

See the [Outreach API playbook](../../api/outreach-PLAYBOOK.md) for requests,
filters, retry behavior, and examples. The live OpenAPI document at
`/api/v1/openapi.json` is authoritative for request and response shapes.

## Troubleshooting

- **The ZIP is rejected:** upload the LinkedIn ZIP unchanged. Nested archives,
  encrypted archives, unsafe paths, and archives with zero or multiple
  `Connections.csv` files are rejected.
- **A row says `ambiguous_linkedin_url`:** more than one METIS Person currently
  has the same normalized LinkedIn URL. Resolve the duplicate People before
  importing that row again.
- **A source name differs:** METIS matched by URL and kept the existing Person's
  canonical name. The report records a warning.
- **The report is unavailable:** reports are temporary and normally expire
  after seven days. The imported People and Memberships remain in METIS.
