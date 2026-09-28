import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import sola_scan as s  # noqa: E402


def rsc_page(*chunks):
    """Build a page shaped like sola.day's: RSC text pushed as JSON string literals."""
    scripts = "".join(
        f'<script>((self[Symbol.for("vinext.navigationRuntime")]??={{rsc:[]}}).rsc.push({json.dumps(c)})</script>'
        for c in chunks
    )
    return f"<html><head><title>x | Social Layer</title></head><body>{scripts}</body></html>"


EVENT = {
    "id": "3s2y2qz7en3zn",
    "title": "Test Workshop",
    "start_time": "2024-09-13T12:00:00Z",
    "end_time": "2024-09-13T13:30:00Z",
    "timezone": "Europe/Lisbon",
    "owner": {"id": "o1", "name": "ownername", "nickname": None},
    "event_roles": [
        {"id": "r1", "display_name": "Ana Silva", "item_type": "User", "role": "speaker"},
    ],
}


class ParseEvent(unittest.TestCase):
    def test_event_split_across_chunks(self):
        body = json.dumps({"event": EVENT})
        cut = len(body) // 2
        html = rsc_page('3:"$Sreact.suspense"\n', "7:" + body[:cut], body[cut:] + "\n", '8:I["x",[],"Y",1]\n')
        ev = s.parse_event(html)
        self.assertEqual(ev["title"], "Test Workshop")
        self.assertEqual(ev["start_time"], "2024-09-13T12:00:00Z")
        self.assertEqual(ev["event_roles"][0]["display_name"], "Ana Silva")

    def test_escaped_content_survives(self):
        ev = dict(EVENT, content='He said "hi" \\ bye\n & more')
        ev2 = s.parse_event(rsc_page("7:" + json.dumps({"event": ev}) + "\n"))
        self.assertEqual(ev2["content"], ev["content"])

    def test_page_without_event(self):
        self.assertIsNone(s.parse_event(rsc_page('0:{"notFound":true}\n')))
        self.assertIsNone(s.parse_event("<html></html>"))


class NormalizeUrl(unittest.TestCase):
    def test_app_subdomain_rewritten(self):
        self.assertEqual(
            s.normalize_url("https://app.sola.day/event/detail/9372"), "https://sola.day/event/detail/9372"
        )

    def test_other_urls_untouched(self):
        self.assertEqual(s.normalize_url("https://sola.day/event/detail/1"), "https://sola.day/event/detail/1")


class LocalFields(unittest.TestCase):
    def test_converts_utc_to_event_timezone(self):
        self.assertEqual(
            s.local_fields(EVENT),
            {"start_date": "2024-09-13", "start_time": "13:00", "end_date": "2024-09-13", "end_time": "14:30",
             "length": 90},
        )

    def test_crossing_midnight(self):
        ev = dict(EVENT, start_time="2024-09-13T22:30:00Z", end_time="2024-09-13T23:30:00Z")
        self.assertEqual(
            s.local_fields(ev),
            {"start_date": "2024-09-13", "start_time": "23:30", "end_date": "2024-09-14", "end_time": "00:30",
             "length": 60},
        )

    def test_length_is_clock_time_across_dst_change(self):
        # Lisbon falls back 02:00 WEST -> 01:00 WET at 01:00Z on 2024-10-27: 120 min elapsed, 60 on the clock.
        ev = dict(EVENT, start_time="2024-10-27T00:00:00Z", end_time="2024-10-27T02:00:00Z")
        f = s.local_fields(ev)
        self.assertEqual((f["start_time"], f["end_time"], f["length"]), ("01:00", "02:00", 60))

    def test_no_length_when_end_not_after_start(self):
        self.assertNotIn("length", s.local_fields(dict(EVENT, end_time=EVENT["start_time"])))

    def test_missing_timezone_uses_default(self):
        ev = dict(EVENT, timezone=None)
        self.assertEqual(s.local_fields(ev)["start_time"], "13:00")

    def test_missing_end_time(self):
        f = s.local_fields(dict(EVENT, end_time=None))
        self.assertEqual(f, {"start_date": "2024-09-13", "start_time": "13:00"})


class PeopleCandidates(unittest.TestCase):
    def test_roles_deduped_and_blank_skipped(self):
        ev = dict(EVENT, event_roles=[
            {"display_name": "Ana Silva", "role": "speaker"},
            {"display_name": "ana silva ", "role": "co_host"},
            {"display_name": "", "role": "speaker"},
            {"display_name": "Rui Costa", "role": "co_host"},
        ])
        self.assertEqual(s.people_candidates(ev), [("speaker", "Ana Silva"), ("co_host", "Rui Costa")])

    def test_owner_only_when_no_roles(self):
        self.assertEqual(s.people_candidates(dict(EVENT, event_roles=[])), [("owner", "ownername")])
        ev = dict(EVENT, event_roles=[], owner={"name": "u1", "nickname": "Nick Name"})
        self.assertEqual(s.people_candidates(ev), [("owner", "Nick Name")])

    def test_nothing(self):
        self.assertEqual(s.people_candidates(dict(EVENT, event_roles=[], owner=None)), [])


class PickMatch(unittest.TestCase):
    def test_single_exact_case_insensitive(self):
        people = [{"id": 1, "name": "Ana Silva"}, {"id": 2, "name": "Ana Silvana"}]
        self.assertEqual(s.pick_match("ana silva", people)["id"], 1)

    def test_ambiguous_or_substring_is_no_match(self):
        self.assertIsNone(s.pick_match("Ana Silva", [{"id": 1, "name": "Ana Silva"}, {"id": 2, "name": "ana silva"}]))
        self.assertIsNone(s.pick_match("Ana", [{"id": 1, "name": "Ana Silva"}]))


class PlanInfoFields(unittest.TestCase):
    DECLARED = {"start_date", "start_time", "end_date", "tags", "source_url"}
    EXISTING = {"start_date": "2024-09-13", "end_date": "2024-09-13", "source_url": "u", "tags": ["Research"]}

    def test_keeps_existing_and_skips_undeclared(self):
        new = {"start_date": "2024-09-13", "start_time": "13:00", "end_date": "2024-09-13", "end_time": "14:30"}
        payload, skipped = s.plan_info_fields(self.EXISTING, new, self.DECLARED)
        self.assertEqual(payload, dict(self.EXISTING, start_time="13:00"))
        self.assertEqual(skipped, ["end_time"])

    def test_no_change_returns_none(self):
        payload, skipped = s.plan_info_fields(dict(self.EXISTING, start_time="13:00"),
                                              {"start_date": "2024-09-13", "start_time": "13:00"}, self.DECLARED)
        self.assertIsNone(payload)
        self.assertEqual(skipped, [])

    def test_drops_existing_undeclared_keys(self):
        payload, _ = s.plan_info_fields(dict(self.EXISTING, legacy="x"), {"start_time": "13:00"}, self.DECLARED)
        self.assertNotIn("legacy", payload)


class StatusAndVenue(unittest.TestCase):
    def test_only_published_is_writable(self):
        self.assertTrue(s.is_writable(dict(EVENT, status="published")))
        self.assertFalse(s.is_writable(dict(EVENT, status="cancel")))
        self.assertFalse(s.is_writable(dict(EVENT, status=None)))

    def test_venue_text_prefers_venue_then_place(self):
        self.assertEqual(s.venue_text(dict(EVENT, venue={"name": "Camp A"}, place={"name": "Field"})), "Camp A")
        self.assertEqual(s.venue_text(dict(EVENT, venue=None, place={"name": "Field"})), "Field")
        self.assertEqual(s.venue_text(dict(EVENT, venue=None, place=None)), "")


class ExportRow(unittest.TestCase):
    def test_row_fields(self):
        h = {"id": 7, "name": "Test Workshop", "parent_id": 3}
        ev = dict(EVENT, status="published", venue={"name": "Camp A"})
        row = s.export_row(h, "https://sola.day/event/detail/1", ev, "updated",
                           matched=[("speaker", "Ana Silva", {"id": 5, "name": "Ana Silva"})],
                           unmatched=[("owner", "ownername")])
        self.assertEqual(row, {
            "holon_id": 7, "name": "Test Workshop", "parent_id": 3,
            "sola_url": "https://sola.day/event/detail/1", "sola_status": "published",
            "start_date": "2024-09-13", "start_time": "13:00", "end_date": "2024-09-13", "end_time": "14:30",
            "length": 90, "venue": "Camp A", "people_matched": "speaker: Ana Silva (#5)", "people_unmatched": "owner: ownername",
            "result": "updated",
        })

    def test_row_without_event(self):
        row = s.export_row({"id": 7, "name": "X", "parent_id": 3}, "u", None, "no event on page", [], [])
        self.assertEqual(row["sola_status"], "")
        self.assertEqual(row["venue"], "")
        self.assertEqual(row["result"], "no event on page")
        self.assertEqual(list(row), s.EXPORT_COLUMNS)


class IsOutage(unittest.TestCase):
    def test_server_errors_and_network_failures_are_outages(self):
        import urllib.error
        self.assertTrue(s.is_outage(urllib.error.HTTPError("u", 502, "Bad Gateway", None, None)))
        self.assertTrue(s.is_outage(urllib.error.URLError("connection refused")))
        self.assertTrue(s.is_outage(TimeoutError()))

    def test_client_errors_are_not(self):
        import urllib.error
        self.assertFalse(s.is_outage(urllib.error.HTTPError("u", 400, "Bad Request", None, None)))
        self.assertFalse(s.is_outage(urllib.error.HTTPError("u", 403, "Forbidden", None, None)))


class HumanDelay(unittest.TestCase):
    def test_bounds(self):
        for _ in range(2000):
            d = s.human_delay(4000, 1500, 30000)
            self.assertGreaterEqual(d, 1500)
            self.assertLessEqual(d, 30000)


if __name__ == "__main__":
    unittest.main()
