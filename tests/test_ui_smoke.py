"""Headless UI smoke test using Streamlit's AppTest. Run from project root:

    python -m unittest tests.test_ui_smoke -v
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from streamlit.testing.v1 import AppTest

PAGES = ["🏠 Home", "📄 Paging Simulator", "🧩 Segmentation Simulator",
         "💾 Virtual Memory Simulator", "⏩ FIFO Page Replacement",
         "🕒 LRU Page Replacement", "📊 Algorithm Comparison"]


def open_page(name: str) -> AppTest:
    at = AppTest.from_file(os.path.join(ROOT, "app.py"), default_timeout=30).run()
    at.sidebar.radio[0].set_value(name).run()
    return at


class TestUI(unittest.TestCase):
    def test_every_page_renders_without_exception(self):
        for name in PAGES:
            at = open_page(name)
            self.assertFalse(at.exception, f"{name}: {[e.value for e in at.exception]}")

    def test_paging_defaults_and_errors(self):
        at = open_page("📄 Paging Simulator")
        self.assertTrue(any("loaded successfully" in s.value for s in at.success))
        at.number_input[0].set_value(999999).run()          # process far larger than memory
        self.assertFalse(at.exception)
        self.assertTrue(at.error)

    def test_segmentation_overflow_message(self):
        at = open_page("🧩 Segmentation Simulator")
        self.assertTrue(any("fit" in s.value for s in at.success))
        at.number_input[0].set_value(1000).run()            # memory < 2500 bytes of segments
        self.assertTrue(any("overflow" in e.value.lower() for e in at.error))

    def test_replacement_pages_bad_input(self):
        for name in ("⏩ FIFO Page Replacement", "🕒 LRU Page Replacement",
                     "💾 Virtual Memory Simulator", "📊 Algorithm Comparison"):
            at = open_page(name)
            at.text_input[0].set_value("1 2 abc").run()
            self.assertFalse(at.exception, name)
            self.assertTrue(at.error, name)
            at.text_input[0].set_value("").run()
            self.assertTrue(at.error, name)

    def test_fifo_and_lru_results_on_screen(self):
        at = open_page("⏩ FIFO Page Replacement")
        self.assertTrue(any("15 page faults" in s.value for s in at.success))
        at = open_page("🕒 LRU Page Replacement")
        self.assertTrue(any("12 page faults" in s.value for s in at.success))

    def test_comparison_winner(self):
        at = open_page("📊 Algorithm Comparison")
        self.assertTrue(any("LRU wins" in s.value for s in at.success))


if __name__ == "__main__":
    unittest.main()
