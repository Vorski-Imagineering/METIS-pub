import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import regenworld_sync as r  # noqa: E402

HIDDEN = "elementor-hidden-desktop elementor-hidden-tablet elementor-hidden-mobile"


def camp_block(widget_id, logo, about_html, hidden=False, schedule="Coming Soon"):
    """One camp as regenworld.net's Elementor renders it: a container around a nested-tabs widget."""
    return f"""
<div class="elementor-element e-con e-parent {HIDDEN if hidden else ''}" data-element_type="container">
 <div class="e-con-inner">
  <div class="elementor-element e-n-tabs-none elementor-widget elementor-widget-n-tabs" data-id="{widget_id}"
       data-widget_type="nested-tabs.default">
   <div class="e-n-tabs"><div class="e-n-tabs-heading" role="tablist">
     <button class="e-n-tab-title" role="tab"><span class="e-n-tab-title-text"> ABOUT </span></button>
     <button class="e-n-tab-title" role="tab"><span class="e-n-tab-title-text"> SCHEDULE </span></button>
     <button class="e-n-tab-title" role="tab"><span class="e-n-tab-title-text"> PARTNERS </span></button>
   </div><div class="e-n-tabs-content">
     <div role="tabpanel" class="e-con e-child">
       <img src="https://regenworld.net/wp-content/uploads/2026/07/{logo}" alt="" />
       <div class="elementor-widget-container">{about_html}</div>
     </div>
     <div role="tabpanel"><p>X SCHEDULE</p><p>{schedule}</p></div>
     <div role="tabpanel"><p>X PARTNERS</p><p>Coming Soon</p></div>
   </div></div>
  </div>
 </div>
</div>"""


PAGE = "<html><body><h1>Camps</h1>" + camp_block(
    "aaa1111", "kaizen-1024x839.png",
    '<div><iframe src="https://www.youtube.com/embed/abc123?rel=0"></iframe></div>'
    "Deep within the ancient redwoods &amp; more.<br />Second line") + camp_block(
    "bbb2222", "nera.jpg", "<h3>What You’ll Experience</h3><p>Alliance weaving.</p><button>Read More ▼</button>",
    hidden=True) + "</body></html>"


class ParseCamps(unittest.TestCase):
    def setUp(self):
        self.camps = r.parse_camps(PAGE)

    def test_one_entry_per_tabs_widget(self):
        self.assertEqual([c["widget_id"] for c in self.camps], ["aaa1111", "bbb2222"])

    def test_hidden_everywhere_container_is_flagged(self):
        self.assertEqual([c["hidden"] for c in self.camps], [False, True])

    def test_logo_is_full_size_upload(self):
        self.assertEqual(self.camps[0]["logo"], "https://regenworld.net/wp-content/uploads/2026/07/kaizen.png")

    def test_youtube_embed_becomes_watch_url(self):
        self.assertEqual(self.camps[0]["video"], "https://www.youtube.com/watch?v=abc123")
        self.assertIsNone(self.camps[1]["video"])

    def test_description_is_escaped_paragraphs_without_buttons(self):
        self.assertEqual(self.camps[0]["description"],
                         "<p>Deep within the ancient redwoods &amp; more.</p><p>Second line</p>")
        self.assertEqual(self.camps[1]["description"], "<p>What You’ll Experience</p><p>Alliance weaving.</p>")

    def test_glued_sentences_get_a_space_so_metis_does_not_autolink_them(self):
        page = camp_block("ccc3333", "c.png", "a connected world.In a world of noise. Version 2.0 stays.")
        self.assertEqual(r.parse_camps(page)[0]["description"],
                         "<p>a connected world. In a world of noise. Version 2.0 stays.</p>")

    def test_schedule_text_is_captured(self):
        self.assertEqual(self.camps[0]["schedule_text"], ["X SCHEDULE", "Coming Soon"])


class ParseGathering(unittest.TestCase):
    def test_same_month_range(self):
        g = r.parse_gathering("<p>OCT 15 – 18, 2026</p><p>CAMP NAVARRO, CA</p>")
        self.assertEqual((g["start_date"], g["end_date"]), ("2026-10-15", "2026-10-18"))

    def test_cross_month_range(self):
        g = r.parse_gathering("<p>OCT 30 – NOV 2, 2026</p>")
        self.assertEqual((g["start_date"], g["end_date"]), ("2026-10-30", "2026-11-02"))

    def test_missing_range_raises(self):
        with self.assertRaises(ValueError):
            r.parse_gathering("<p>Coming soon</p>")


SITE_G = {"start_date": "2026-10-15", "end_date": "2026-10-18", "tickets": "https://regenworld.net/gather/"}
METIS_G = {"id": 226, "info_fields": dict(SITE_G)}
KAIZEN = {"widget_id": "k", "hidden": False, "logo": "https://x/k.png", "video": None,
          "description": "<p>Kaizen</p>", "schedule_text": ["Coming Soon"]}
MAPPING = {"k": {"name": "Camp Kaizen", "key": "camp-kaizen"},
           "a": {"name": "Camp Audax - USA 2026", "key": "camp-audax", "metis_id": 1708}}
SRC_K = "https://regenworld.net/camps/#camp-kaizen"


def ops(actions):
    return [(a["op"], a.get("id"), a.get("step")) for a in actions]


class Plan(unittest.TestCase):
    def test_new_camp_is_created_with_source_link(self):
        actions, _ = r.plan([KAIZEN], SITE_G, METIS_G, {}, {}, MAPPING)
        self.assertEqual(ops(actions), [("create_camp", None, None)])
        self.assertEqual(actions[0]["links"], {"source": SRC_K})
        self.assertEqual(actions[0]["name"], "Camp Kaizen")

    def test_in_sync_camp_plans_nothing(self):
        h = {"id": 5, "name": "Camp Kaizen", "description": "<p>Kaizen</p>",
             "links": {"source": SRC_K, "logo_source": "https://x/k.png"}}
        actions, warnings = r.plan([KAIZEN], SITE_G, METIS_G, {5: h}, {5: "Selling"}, MAPPING)
        self.assertEqual((actions, warnings), ([], []))

    def test_markup_metis_adds_itself_is_not_a_change(self):
        h = {"id": 5, "name": "Camp Kaizen", "description": '<p><a href="http://x.io">Kaizen</a></p>',
             "links": {"source": SRC_K, "logo_source": "https://x/k.png"}}
        actions, _ = r.plan([KAIZEN], SITE_G, METIS_G, {5: h}, {5: "Selling"}, MAPPING)
        self.assertEqual(actions, [])

    def test_existing_camp_is_claimed_by_metis_id_and_keeps_human_links(self):
        audax = dict(KAIZEN, widget_id="a", description="<p>Audax</p>")
        h = {"id": 1708, "name": "Camp Audax - USA 2026", "description": "old", "links": {"website": "https://w"}}
        actions, _ = r.plan([audax], SITE_G, METIS_G, {1708: h}, {1708: "Selling"}, MAPPING)
        self.assertEqual(ops(actions), [("set_logo", 1708, None), ("update_camp", 1708, None)])
        self.assertEqual(actions[1]["set"]["links"],
                         {"website": "https://w", "source": "https://regenworld.net/camps/#camp-audax"})
        self.assertNotIn("name", actions[1]["set"])

    def test_camp_gone_from_site_is_cancelled(self):
        h = {"id": 5, "name": "Camp Kaizen", "description": "", "links": {"source": SRC_K}}
        actions, _ = r.plan([], SITE_G, METIS_G, {5: h}, {5: "Selling"}, MAPPING)
        self.assertEqual(ops(actions), [("set_step", 5, "cancelled")])

    def test_hidden_camp_counts_as_gone(self):
        h = {"id": 5, "name": "Camp Kaizen", "description": "", "links": {"source": SRC_K}}
        actions, warnings = r.plan([dict(KAIZEN, hidden=True)], SITE_G, METIS_G, {5: h}, {5: "Selling"}, MAPPING)
        self.assertEqual(ops(actions), [("set_step", 5, "cancelled")])
        self.assertIn("hidden", warnings[0])

    def test_unmapped_camp_blocks_cancellations(self):
        h = {"id": 5, "name": "Camp Kaizen", "description": "", "links": {"source": SRC_K}}
        stranger = dict(KAIZEN, widget_id="zzz")
        actions, warnings = r.plan([stranger], SITE_G, METIS_G, {5: h}, {5: "Selling"}, MAPPING)
        self.assertEqual(actions, [])
        self.assertTrue(any("UNMAPPED" in w for w in warnings))
        self.assertTrue(any("not cancelling" in w for w in warnings))

    def test_cancelled_camp_back_on_site_is_restored(self):
        h = {"id": 5, "name": "Camp Kaizen", "description": "<p>Kaizen</p>",
             "links": {"source": SRC_K, "logo_source": "https://x/k.png"}}
        actions, _ = r.plan([KAIZEN], SITE_G, METIS_G, {5: h}, {5: "Cancelled"}, MAPPING)
        self.assertEqual(ops(actions), [("set_step", 5, "selling")])

    def test_already_cancelled_camp_is_not_moved_again(self):
        h = {"id": 5, "name": "Camp Kaizen", "description": "", "links": {"source": SRC_K}}
        actions, _ = r.plan([], SITE_G, METIS_G, {5: h}, {5: "Cancelled"}, MAPPING)
        self.assertEqual(actions, [])

    def test_excepted_camp_is_never_touched(self):
        audax = dict(KAIZEN, widget_id="a", description="<p>site text</p>")
        h = {"id": 1708, "name": "Camp Audax - USA 2026", "description": "ours", "links": {}}
        actions, warnings = r.plan([audax], SITE_G, METIS_G, {1708: h}, {1708: "Selling"}, MAPPING,
                                   exceptions={"camp-audax": "METIS-owned"})
        self.assertEqual(actions, [])
        self.assertEqual(warnings, [])

    def test_excepted_camp_missing_from_site_is_not_cancelled(self):
        h = {"id": 5, "name": "Camp Kaizen", "description": "", "links": {"source": SRC_K}}
        actions, _ = r.plan([], SITE_G, METIS_G, {5: h}, {5: "Selling"}, MAPPING,
                            exceptions={"camp-kaizen": "handled by hand"})
        self.assertEqual(actions, [])

    def test_excepted_camp_is_not_created(self):
        actions, _ = r.plan([KAIZEN], SITE_G, METIS_G, {}, {}, MAPPING, exceptions={"camp-kaizen": "no"})
        self.assertEqual(actions, [])

    def test_gathering_dates_are_overwritten(self):
        g = {"id": 226, "info_fields": dict(SITE_G, end_date="2026-10-19")}
        actions, _ = r.plan([], SITE_G, g, {}, {}, MAPPING)
        self.assertEqual(actions[0]["op"], "update_gathering")
        self.assertEqual(actions[0]["info_fields"], {"end_date": "2026-10-18"})


if __name__ == "__main__":
    unittest.main()
