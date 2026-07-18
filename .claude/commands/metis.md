# METIS Read API — connection skill

You are about to query the METIS Read API (`/api/v1/`). This is the AI-client endpoint.
It uses a two-step Bearer token auth flow. Full API reference is in `docs-pub/api/PLAYBOOK.md` —
read it now before making any calls.

---

## Required environment

```
METIS_URL=https://app.the-gathering.earth
```

`METIS_API_KEY` is the shared login gate secret. Read it from the project `.env` file:

```bash
METIS_API_KEY=$(grep '^API_LOGIN_SECRET=' .env | cut -d= -f2-)
```

You also need `METIS_EMAIL` and `METIS_PASSWORD`:
- Try to read them from `.env` first (`METIS_EMAIL=` and `METIS_PASSWORD=` lines)
- If missing, ask the user
- After a **successful** login, write any credentials that were missing back to `.env` (append or update the relevant lines) so they are available next time

---

## Step 1 — Load credentials and log in

```bash
METIS_URL="https://app.the-gathering.earth"
METIS_API_KEY=$(grep '^API_LOGIN_SECRET=' .env | cut -d= -f2-)
METIS_EMAIL=$(grep '^METIS_EMAIL=' .env | cut -d= -f2-)
METIS_PASSWORD=$(grep '^METIS_PASSWORD=' .env | cut -d= -f2-)
```

If either `METIS_EMAIL` or `METIS_PASSWORD` is empty after the above, ask the user for the missing value(s) before proceeding.

After a successful login, persist any credential that was not already in `.env`:
```bash
# Only run for values that were missing — append to .env
echo "METIS_EMAIL=the-email" >> .env
echo "METIS_PASSWORD=the-password" >> .env
```

```bash
curl -s -X POST "${METIS_URL}/api/v1/auth/login" \
  -H "X-Metis-Api-Key: ${METIS_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"email": "'"${METIS_EMAIL}"'", "password": "'"${METIS_PASSWORD}"'"}'
```

**Success (200):** returns `token` (valid 24 hours), `token_type`, `expires_at`, `person`.

Store the `token` value:
```bash
METIS_TOKEN="metis_agentic_..."
```

**Error codes:**
- `401` — wrong password or missing/invalid `X-Metis-Api-Key`
- `403` — account exists but has no linked METIS Person

---

## Step 2 — Make authenticated calls

All subsequent requests use:
```
Authorization: Bearer <token>
```

For full endpoint reference — available endpoints, parameters, response shapes, error codes,
access model, and field projections — read `docs-pub/api/PLAYBOOK.md`.
