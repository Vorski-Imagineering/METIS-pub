import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import airtable_schedule as a  # noqa: E402

TBL = "tblThrqVH4XaFHHjS"


def response(rows, order=None):
    """Build a readForSharedPages response shaped like the real one (only the parts we read)."""
    columns = [
        {"id": "fName", "name": "Session Name", "type": "text"},
        {"id": "fStart", "name": "Start Time", "type": "date"},
        {"id": "fEnd", "name": "End Time", "type": "date"},
        {"id": "fLoc", "name": "Location/Area", "type": "select",
         "typeOptions": {"choices": {"selMain": {"id": "selMain", "name": "Main Stage"}}}},
        {"id": "fCamp", "name": "Camp Name", "type": "foreignKey"},
        {"id": "fDay", "name": "Day", "type": "select",
         "typeOptions": {"choices": {"selFri": {"id": "selFri", "name": "Friday 10/16"}}}},
        {"id": "fDesc", "name": "Program Description (150-word max)", "type": "multilineText"},
        {"id": "fCat", "name": "Category", "type": "select",
         "typeOptions": {"choices": {"selSpk": {"id": "selSpk", "name": "Speaker"}}}},
    ]
    return {"data": {
        "tableSchemas": [{"id": "tblCamps", "columns": []}, {"id": TBL, "columns": columns}],
        "preloadPageQueryResults": {
            "querySlices": [{"tableId": TBL, "rowIds": order or list(rows)}],
            "tableDataById": {TBL: {"partialRowById": {
                rid: {"id": rid, "cellValuesByColumnId": cells} for rid, cells in rows.items()}}},
        },
    }}


YOGA = {
    "fName": "Morning Yoga ", "fStart": "2026-10-16T08:00:00.000Z", "fEnd": "2026-10-16T09:00:00.000Z",
    "fLoc": "selMain", "fDay": "selFri", "fDesc": "Stretch.\n", "fCat": "selSpk",
    "fCamp": [{"foreignRowId": "recC", "foreignRowDisplayName": "Camp Regenaissance "}],
}


class ParseTest(unittest.TestCase):
    def test_resolves_selects_links_and_keeps_wall_clock_time(self):
        [s] = a.parse(response({"recA": YOGA}))
        self.assertEqual(s, {
            "id": "recA", "title": "Morning Yoga", "start": "2026-10-16T08:00", "end": "2026-10-16T09:00",
            "location": "Main Stage", "camps": ["Camp Regenaissance"], "day": "Friday 10/16",
            "description": "Stretch.", "category": "Speaker", "length": 60,
        })

    def test_missing_cells_are_none_and_no_camp_is_empty_list(self):
        [s] = a.parse(response({"recA": {"fName": "Dinner"}}))
        self.assertEqual(s["camps"], [])
        self.assertIsNone(s["start"])
        self.assertIsNone(s["length"])

    def test_sorted_by_start_then_title(self):
        late = dict(YOGA, fName="B", fStart="2026-10-16T10:00:00.000Z")
        early_b = dict(YOGA, fName="B")
        early_a = dict(YOGA, fName="A")
        got = a.parse(response({"r1": late, "r2": early_b, "r3": early_a}))
        self.assertEqual([s["id"] for s in got], ["r3", "r2", "r1"])

    def test_length_runs_past_midnight(self):
        self.assertEqual(a.minutes_between("2026-10-15T20:00", "2026-10-16T02:00"), 360)


class WarningsTest(unittest.TestCase):
    def test_flags_duplicates_zero_length_and_gaps(self):
        sessions = a.parse(response({
            "r1": YOGA,
            "r2": dict(YOGA, fCamp=[]),
            "r3": dict(YOGA, fName="Close", fEnd=YOGA["fStart"]),
            "r4": {"fName": "Dinner"},
        }))
        text = "\n".join(a.warnings(sessions))
        self.assertIn("same title, start and place", text)
        self.assertIn("starts and ends at the same time", text)
        self.assertIn("r4 'Dinner': no start", text)


if __name__ == "__main__":
    unittest.main()
