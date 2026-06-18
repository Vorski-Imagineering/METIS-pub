---
description: Set up METIS API credentials — saves email, password, and API key to .env
allowed-tools: Bash, Read, Write, Edit
---

# METIS Setup

Walk the user through providing their METIS credentials and save them to the `.env` file in the project root.

## Steps

### 1. Check what's already saved

Read the current `.env` file (it may not exist yet):

```bash
cat .env 2>/dev/null || echo "(no .env file yet)"
```

Note which of the following are already present and non-empty:
- `API_LOGIN_SECRET=`
- `METIS_EMAIL=`
- `METIS_PASSWORD=`

### 2. Ask for missing values

For each credential that is missing or empty, ask the user to provide it. Ask all at once in a single message rather than one at a time. Explain briefly what each is for:

- **API_LOGIN_SECRET** — the shared instance secret (ask your METIS admin if you don't have it)
- **METIS_EMAIL** — the email address of your METIS account
- **METIS_PASSWORD** — your METIS account password

Do **not** ask for values that are already present. Tell the user which ones you found and which you need.

### 3. Save to .env

Once you have all three values, write them to `.env`. Preserve any other lines already in the file.

For each credential, either update the existing line or append it:

```bash
# Update or append API_LOGIN_SECRET
if grep -q '^API_LOGIN_SECRET=' .env 2>/dev/null; then
  sed -i '' "s|^API_LOGIN_SECRET=.*|API_LOGIN_SECRET=VALUE|" .env
else
  echo "API_LOGIN_SECRET=VALUE" >> .env
fi

# Update or append METIS_EMAIL
if grep -q '^METIS_EMAIL=' .env 2>/dev/null; then
  sed -i '' "s|^METIS_EMAIL=.*|METIS_EMAIL=VALUE|" .env
else
  echo "METIS_EMAIL=VALUE" >> .env
fi

# Update or append METIS_PASSWORD
if grep -q '^METIS_PASSWORD=' .env 2>/dev/null; then
  sed -i '' "s|^METIS_PASSWORD=.*|METIS_PASSWORD=VALUE|" .env
else
  echo "METIS_PASSWORD=VALUE" >> .env
fi
```

Replace `VALUE` with the actual values before running.

### 4. Verify

Read back `.env` and confirm all three values are present. Report success to the user:

> "METIS credentials saved to `.env`. You're ready to use `/metis`."

If `.env` is not gitignored, warn the user and suggest they check their `.gitignore`.
