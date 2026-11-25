#!/bin/bash
# Minimal METIS /api/v1 client for the gathering-camp skill.
#   bash metis_api.sh GET  /holons/224
#   bash metis_api.sh POST /camps '{"parent_id":224,...}'
# Reads credentials from the repo's .env, caches the 24h token, uses a browser
# User-Agent (Cloudflare blocks default client UAs with a 403 "error code: 1010").
set -euo pipefail
ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
ENV="$ROOT/.env"
BASE="https://app.the-gathering.earth/api/v1"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
CACHE="${TMPDIR:-/tmp}/metis_token_$(id -u)"

envval() { grep "^$1=" "$ENV" | cut -d= -f2-; }

login() {
  local body
  body=$(python3 -c 'import json,sys;print(json.dumps({"email":sys.argv[1],"password":sys.argv[2]}))' \
    "$(envval METIS_EMAIL)" "$(envval METIS_PASSWORD)")
  curl -s -A "$UA" -X POST "$BASE/auth/login" -H "X-Metis-Api-Key: $(envval API_LOGIN_SECRET)" \
    -H "Content-Type: application/json" -d "$body" |
    python3 -c 'import json,sys;print(json.load(sys.stdin)["token"])' > "$CACHE"
  chmod 600 "$CACHE"
}

[ -s "$CACHE" ] && [ -z "$(find "$CACHE" -mmin +1380)" ] || login
call() {
  if [ "$1" = GET ]; then
    curl -s -w '\n%{http_code}' -A "$UA" -H "Authorization: Bearer $(cat "$CACHE")" "$BASE$2"
  else
    curl -s -w '\n%{http_code}' -A "$UA" -H "Authorization: Bearer $(cat "$CACHE")" \
      -H "Content-Type: application/json" -X POST "$BASE$2" -d "$3"
  fi
}
out=$(call "$@")
if [ "$(tail -n1 <<<"$out")" = 401 ]; then login; out=$(call "$@"); fi
code=$(tail -n1 <<<"$out")
sed '$d' <<<"$out"
[ "${code:0:1}" = 2 ] || { echo "HTTP $code" >&2; exit 1; }
