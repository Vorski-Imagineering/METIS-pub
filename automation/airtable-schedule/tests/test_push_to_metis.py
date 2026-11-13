import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import push_to_metis as p  # noqa: E402

SHARE = "https://airtable.com/app/shr"
OWNERS = {"gathering": 226, "camps": {"RegenWorld": 226, "Camp A": 1, "Camp B": 2, "NERA Camp": None},
          "places": {"Main Stage": "abc123"}, "skip": {"recSkip": "duplicate"}}
FIELDS = {"start_date", "start_time", "length", "where"}


def session(rid="rec1", camps=("Camp A",), **kw):
    return {"id": rid, "title": "Talk", "start": "2026-10-16T08:00", "end": "2026-10-16T09:30",
            "length": 90, "location": "Main Stage", "camps": list(camps), "category": "Speaker", "description": "One.\n\nTwo\nlines", **kw}


def existing(rid="rec1", parent=1, step="Published", **kw):
    s = session(rid)
    exp = {"id": 900, "parent_id": parent, "name": s["title"], "step": step,
           "description": p.description_html(s, []), "info_fields": p.info_fields(s, FIELDS, OWNERS["places"])}
    exp.update(kw)
    return {p.source_url(SHARE, rid): exp}


class OwnerTest(unittest.TestCase):
    def test_first_real_camp_owns_and_the_rest_are_named(self):
        self.assertEqual(p.owner_of(session(camps=("RegenWorld", "Camp B", "NERA Camp")), OWNERS),
                         (2, ["RegenWorld", "NERA Camp"]))

    def test_no_camp_or_regenworld_goes_to_the_gathering(self):
        self.assertEqual(p.owner_of(session(camps=()), OWNERS), (226, []))
        self.assertEqual(p.owner_of(session(camps=("RegenWorld",)), OWNERS), (226, []))

    def test_unknown_camp_is_reported(self):
        self.assertEqual(p.owner_of(session(camps=("Camp Z",)), OWNERS), (None, ["Camp Z"]))


class FieldsTest(unittest.TestCase):
    def test_description_paragraphs_line_breaks_and_escaping(self):
        s = session(description="A & B\n\nline1\nline2")
        self.assertEqual(p.description_html(s, ["Camp B"]),
                         "<p>With Camp B.</p><p>A &amp; B</p><p>line1<br>line2</p>")

    def test_zero_length_is_left_out_and_tags_only_when_the_class_has_them(self):
        f = p.info_fields(session(length=0), FIELDS)
        self.assertEqual(f, {"start_date": "2026-10-16", "start_time": "08:00"})
        self.assertEqual(p.info_fields(session(), FIELDS | {"tags"})["tags"], ["Speaker"])

    def test_where_is_the_place_id(self):
        self.assertEqual(p.info_fields(session(), FIELDS, OWNERS["places"])["where"], "abc123")
        self.assertNotIn("where", p.info_fields(session(location="Nowhere"), FIELDS, OWNERS["places"]))


class PlanTest(unittest.TestCase):
    def test_new_session_is_created_with_its_source(self):
        [a], w = p.plan([session()], {}, OWNERS, SHARE, FIELDS)
        self.assertEqual((a["op"], a["parent_id"], a["source"]), ("create", 1, f"{SHARE}#rec1"))
        self.assertEqual(w, [])

    def test_unchanged_published_session_needs_nothing(self):
        self.assertEqual(p.plan([session()], existing(), OWNERS, SHARE, FIELDS), ([], []))

    def test_changed_time_is_updated_and_unpublished_is_published(self):
        actions, _ = p.plan([session(start="2026-10-16T10:00")], existing(step="Idea"), OWNERS, SHARE, FIELDS)
        self.assertEqual([a["op"] for a in actions], ["update", "publish"])
        self.assertEqual(actions[0]["info_fields"], {"start_time": "10:00"})

    def test_removed_or_skipped_session_is_unpublished(self):
        actions, _ = p.plan([], existing(), OWNERS, SHARE, FIELDS)
        self.assertEqual([a["op"] for a in actions], ["unpublish"])
        actions, _ = p.plan([session("recSkip")], existing("recSkip"), OWNERS, SHARE, FIELDS)
        self.assertEqual([a["op"] for a in actions], ["unpublish"])

    def test_unknown_place_is_warned_and_left_out(self):
        [a], w = p.plan([session(location="Nowhere")], {}, OWNERS, SHARE, FIELDS)
        self.assertNotIn("where", a["info_fields"])
        self.assertIn("place 'Nowhere' not in owners.json", w[0])

    def test_owner_change_is_warned_not_moved(self):
        _, w = p.plan([session(camps=("Camp B",))], existing(), OWNERS, SHARE, FIELDS)
        self.assertIn("move it in the web app", w[0])


if __name__ == "__main__":
    unittest.main()
