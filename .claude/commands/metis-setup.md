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

Save each value as soon as the user gives it — they often send the values one per message, and
sometimes without saying which credential a value is. If a value is unlabelled, infer it from its
shape (a long random string is almost certainly `API_LOGIN_SECRET`; an email is `METIS_EMAIL`), say
which key you saved it under, and invite a correction.

Values are stored raw and unquoted — `/metis` reads them with `grep '^KEY=' .env | cut -d= -f2-`, so
quotes would become part of the value. Passwords routinely contain `$`, `!`, `*`, `@` and `|`, so
**never** interpolate a value inside double quotes or a `sed` replacement: `"…$X9…"` silently expands
`$X9` to nothing, and `sed -i ''` is macOS-only (on Linux it fails). Use this portable
remove-then-append, with the value in **single quotes** (escape any `'` in it as `'\''`):

```bash
set_env() {  # set_env KEY 'value' — replaces any existing KEY line, preserves all others
  touch .env && chmod 600 .env
  grep -v "^$1=" .env > .env.tmp || true
  printf '%s=%s\n' "$1" "$2" >> .env.tmp && mv .env.tmp .env && chmod 600 .env
}
set_env METIS_PASSWORD 'the-value-verbatim'
```

### 4. Verify

Confirm the stored value round-trips exactly (do this for the password at least):

```bash
grep '^METIS_PASSWORD=' .env | cut -d= -f2- | grep -qxF 'the-value-verbatim' && echo ok
```

Then test a real login, building the JSON with `jq` so special characters can't break it. Don't
echo the response raw — it contains the session token; print only the status and the person's name:

```bash
K=$(grep '^API_LOGIN_SECRET=' .env | cut -d= -f2-)
E=$(grep '^METIS_EMAIL=' .env | cut -d= -f2-)
P=$(grep '^METIS_PASSWORD=' .env | cut -d= -f2-)
jq -n --arg e "$E" --arg p "$P" '{email:$e,password:$p}' \
  | curl -s -o /tmp/metis-login.json -w '%{http_code}\n' -X POST \
      https://app.the-gathering.earth/api/v1/auth/login \
      -H "X-Metis-Api-Key: $K" -H "Content-Type: application/json" -d @-
jq -r '.person.name // .' /tmp/metis-login.json; rm -f /tmp/metis-login.json
```

`200` → report: "METIS credentials saved to `.env` and login works as <name>. You're ready to use
`/metis`." `401` → wrong password or secret (ask which to re-enter); `403` → account has no linked
METIS Person (tell them to ask their METIS admin).

If `.env` is not gitignored (`git check-ignore .env` prints nothing), warn the user and suggest they
check their `.gitignore`.
