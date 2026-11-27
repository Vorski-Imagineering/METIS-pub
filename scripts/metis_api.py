#!/usr/bin/env python3
"""Local METIS API client shared by the startup report and Codex skill."""

import argparse
import json
import sys
from contextlib import contextmanager
from http.client import HTTPException
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import unquote
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parent.parent
METIS = "https://app.the-gathering.earth/api/v1"
# The default Python User-Agent receives an HTML 403 from the METIS gateway.
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
CREDENTIAL_KEYS = ("API_LOGIN_SECRET", "METIS_EMAIL", "METIS_PASSWORD")
REQUEST_ERRORS = (OSError, ValueError, HTTPException)


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Login secrets and bearer tokens are intended for the API origin only.
        return None


def read_credentials():
    try:
        lines = (ROOT / ".env").read_text(encoding="utf-8-sig").split("\n")
    except FileNotFoundError:
        return {}
    credentials = {}
    for line in lines:
        key, separator, value = line.partition("=")
        if separator and key.strip() in CREDENTIAL_KEYS:
            credentials[key.strip()] = value
    return credentials


def missing_credentials(credentials):
    return [key for key in CREDENTIAL_KEYS if not credentials.get(key, "").strip()]


def decode_json(raw):
    # METIS list responses can include invalid UTF-8 and raw control characters.
    return json.loads(raw.decode("utf-8", "replace"), strict=False)


def call(path, token=None, body=None, key=None):
    headers = {"User-Agent": UA, "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if key:
        headers["X-Metis-Api-Key"] = key
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = Request(METIS + path, data=data, headers=headers)
    with build_opener(NoRedirect()).open(request, timeout=6) as response:
        return decode_json(response.read())


@contextmanager
def session(credentials):
    login = call(
        "/auth/login",
        body={"email": credentials["METIS_EMAIL"], "password": credentials["METIS_PASSWORD"]},
        key=credentials["API_LOGIN_SECRET"],
    )
    token = login.get("token") if isinstance(login, dict) else None
    if not isinstance(token, str) or not token:
        raise ValueError("METIS login returned no session token")
    try:
        yield token, login.get("person") or {}
    finally:
        try:
            call("/auth/logout", token, body={})
        except REQUEST_ERRORS:
            pass


def api_path(value):
    path = value.partition("?")[0]
    parts = [unquote(segment) for segment in path.rstrip("/")[1:].split("/")]
    if (
        not path.startswith("/")
        or "#" in value
        or any(not "!" <= char <= "~" for char in value)
        or any(not part or part in (".", "..") or "/" in part or "\\" in part for part in parts)
    ):
        raise argparse.ArgumentTypeError("use an API-relative path such as /auth/whoami")
    if parts[0].lower() == "auth" and parts != ["auth", "whoami"]:
        raise argparse.ArgumentTypeError("the client handles authentication internally")
    return value


def request_api(args, credentials):
    body = None
    if args.method == "POST":
        try:
            body = json.load(sys.stdin)
        except ValueError:
            print("Pass a JSON object on stdin for POST.", file=sys.stderr)
            return 1
        if not isinstance(body, dict):
            print("Pass a JSON object on stdin for POST.", file=sys.stderr)
            return 1

    logged_in = False
    try:
        with session(credentials) as (token, _):
            logged_in = True
            result = call(args.path, token, body=body)
    except HTTPError as error:
        stage = "request" if logged_in else "login"
        with error:
            print(f"METIS {stage} failed (HTTP {error.code}).", file=sys.stderr)
            if logged_in:
                try:
                    print(json.dumps(decode_json(error.read())), file=sys.stderr)
                except REQUEST_ERRORS:
                    pass
        return 1
    except REQUEST_ERRORS as error:
        stage = "request" if logged_in else "login"
        print(f"METIS {stage} failed ({type(error).__name__}).", file=sys.stderr)
        return 1

    print(json.dumps(result))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("credentials", help="check for required keys in the local .env")
    request = commands.add_parser("request", help="authenticate and make one API call")
    request.add_argument("method", choices=("GET", "POST"))
    request.add_argument("path", type=api_path)
    args = parser.parse_args()

    try:
        credentials = read_credentials()
    except (OSError, UnicodeError):
        print("Could not read the repo-root .env file.", file=sys.stderr)
        return 1
    missing = missing_credentials(credentials)
    if args.command == "credentials":
        for key in CREDENTIAL_KEYS:
            print(f"{key}: {'missing' if key in missing else 'present'}")
        return int(bool(missing))
    if missing:
        print(f"Missing METIS keys in the repo-root .env: {', '.join(missing)}", file=sys.stderr)
        return 1
    return request_api(args, credentials)


if __name__ == "__main__":
    sys.exit(main())
