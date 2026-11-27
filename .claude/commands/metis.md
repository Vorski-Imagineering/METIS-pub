# METIS Read API

For ordinary METIS lookups and updates, follow the API workflow in
`.agents/skills/metis/SKILL.md`. The shared local client handles login, requests, and logout
without exposing credentials or the token. Read `docs-pub/api/v1-PLAYBOOK.md` for `/api/v1/`
endpoints and use `/metis-setup` if credentials are missing.

## Step 1 — Login for existing multi-step Claude workflows

Coherence and the existing outreach commands use session variables across multiple API calls.
If one of those workflows references this step, run the following in the same shell as its
authenticated calls. Read `automation/metis/README.md` for local credential setup.

```bash
METIS_URL="https://app.the-gathering.earth"
METIS_API_KEY=$(grep '^API_LOGIN_SECRET=' .env | cut -d= -f2-)
METIS_EMAIL=$(grep '^METIS_EMAIL=' .env | cut -d= -f2-)
METIS_PASSWORD=$(grep '^METIS_PASSWORD=' .env | cut -d= -f2-)
METIS_PYTHON=$(command -v py || command -v python3 || command -v python)

METIS_LOGIN=$(METIS_EMAIL="$METIS_EMAIL" METIS_PASSWORD="$METIS_PASSWORD" "$METIS_PYTHON" -c \
  'import json, os; print(json.dumps({"email": os.environ["METIS_EMAIL"], "password": os.environ["METIS_PASSWORD"]}))' \
  | curl -fsS -X POST "${METIS_URL}/api/v1/auth/login" \
      -H "X-Metis-Api-Key: ${METIS_API_KEY}" -H "Content-Type: application/json" -d @-) || exit 1
METIS_TOKEN=$(printf '%s' "$METIS_LOGIN" | "$METIS_PYTHON" -c 'import json, sys; print(json.load(sys.stdin)["token"])') || exit 1
```

Read `person.id` and `person.name` from `METIS_LOGIN` in that shell when the workflow needs
them. Keep `METIS_LOGIN` and `METIS_TOKEN` out of output and files. Use
`Authorization: Bearer ${METIS_TOKEN}` for the authenticated calls. The token is valid for
24 hours unless revoked.
