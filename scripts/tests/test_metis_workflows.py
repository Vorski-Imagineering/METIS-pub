import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import call, patch
from urllib.error import HTTPError, URLError

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import metis_api

spec = importlib.util.spec_from_file_location("session_start", SCRIPTS / "session-start.py")
session_start = importlib.util.module_from_spec(spec)
spec.loader.exec_module(session_start)

FIXTURE_CREDENTIALS = {
    "API_LOGIN_SECRET": "fake-gate",
    "METIS_EMAIL": "fixture@example.com",
    "METIS_PASSWORD": " password '$!=é' ",
}


class ApiTests(unittest.TestCase):
    def run_cli(self, *args, body=""):
        with patch.object(sys, "argv", ["metis_api.py", *args]), patch.object(sys, "stdin", io.StringIO(body)):
            with redirect_stdout(io.StringIO()) as stdout, redirect_stderr(io.StringIO()) as stderr:
                status = metis_api.main()
        return status, stdout.getvalue(), stderr.getvalue()

    def test_credentials_check_reads_only_keys_and_preserves_literal_values(self):
        with tempfile.TemporaryDirectory() as root, patch.object(metis_api, "ROOT", Path(root)):
            (Path(root) / ".env").write_text(
                "\ufeff" + "\n".join(f"{key}={value}" for key, value in FIXTURE_CREDENTIALS.items()),
                encoding="utf-8",
            )
            self.assertEqual(metis_api.read_credentials(), FIXTURE_CREDENTIALS)
            status, stdout, stderr = self.run_cli("credentials")
        self.assertEqual((status, stderr), (0, ""))
        self.assertEqual(stdout.splitlines(), [f"{key}: present" for key in FIXTURE_CREDENTIALS])

    def test_missing_credentials_block_api_requests(self):
        with patch.object(metis_api, "read_credentials", return_value={}), patch.object(metis_api, "call") as request:
            status, _, stderr = self.run_cli("request", "GET", "/holons")
            request.assert_not_called()
        self.assertEqual(status, 1)
        self.assertIn("METIS_PASSWORD", stderr)

    def test_login_failure_does_not_print_response_body(self):
        error = HTTPError("https://example.com/", 401, "Unauthorized", {}, io.BytesIO(b"fake-gate"))
        with patch.object(metis_api, "read_credentials", return_value=FIXTURE_CREDENTIALS), patch.object(metis_api, "call", side_effect=error):
            status, stdout, stderr = self.run_cli("request", "GET", "/holons")
        self.assertEqual((status, stdout), (1, ""))
        self.assertEqual(stderr, "METIS login failed (HTTP 401).\n")

    def test_failed_request_attempts_logout(self):
        with patch.object(metis_api, "read_credentials", return_value=FIXTURE_CREDENTIALS), patch.object(metis_api, "call") as request:
            request.side_effect = [{"token": "fixture-token"}, URLError("Offline"), {"revoked": True}]
            status, _, stderr = self.run_cli("request", "GET", "/holons")
        self.assertEqual(status, 1)
        self.assertIn("METIS request failed", stderr)
        self.assertEqual(request.call_args_list[1:], [
            call("/holons", "fixture-token", body=None),
            call("/auth/logout", "fixture-token", body={}),
        ])

    def test_post_passes_json_from_stdin_and_returns_only_request_result(self):
        endpoint = "/relationships/42/update"
        body = {"note": "Follow up next week"}
        with patch.object(metis_api, "read_credentials", return_value=FIXTURE_CREDENTIALS):
            with patch.object(metis_api, "call") as request:
                request.side_effect = [{"token": "fixture-token"}, {"updated": True}, {"revoked": True}]
                status, stdout, stderr = self.run_cli("request", "POST", endpoint, body=json.dumps(body))
        self.assertEqual((status, stderr), (0, ""))
        self.assertEqual(json.loads(stdout), {"updated": True})
        self.assertEqual(request.call_args_list[1], call(endpoint, "fixture-token", body=body))


class StartupTests(unittest.TestCase):
    def test_codex_hook_reports_incoming_commits_without_loading_worklist(self):
        with patch.object(session_start, "git", side_effect=["main", "", "0\t1", "abcdef Update"]):
            with patch.object(session_start, "load_worklist") as worklist, redirect_stdout(io.StringIO()) as stdout:
                with patch.object(sys, "argv", ["session-start.py", "--codex-hook"]):
                    session_start.main()
                worklist.assert_not_called()
        output = json.loads(stdout.getvalue())
        self.assertIn("Updates available", output["systemMessage"])
        self.assertIn("Wait for their answer.", output["hookSpecificOutput"]["additionalContext"])

    def test_failed_fetch_is_distinct_from_up_to_date(self):
        with patch.object(session_start, "git", side_effect=["main", None]):
            status, incoming = session_start.git_status()
        self.assertIn("fetch failed", status)
        self.assertEqual(incoming, "")

    def test_missing_person_id_cannot_query_an_unscoped_worklist(self):
        with patch.object(session_start, "read_credentials", return_value=FIXTURE_CREDENTIALS):
            with patch.object(metis_api, "call", side_effect=[{"token": "fixture-token"}, {"revoked": True}]) as request:
                with patch.object(session_start, "fetch") as fetch:
                    _, error = session_start.load_worklist()
                fetch.assert_not_called()
                request.assert_called_with("/auth/logout", "fixture-token", body={})
        self.assertIn("couldn't load your worklist", error)
