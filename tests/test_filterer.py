"""Unit tests for WindowFilterer, including dot-syntax and ranking."""

import unittest
from switcheroo.core.filterer import WindowFilterer
from switcheroo.core.window_model import AppWindow


class TestWindowFilterer(unittest.TestCase):
    def setUp(self):
        self.filterer = WindowFilterer()
        self.w1 = AppWindow(
            xid=1,
            wnck_window=None,
            title="Inbox - Thunderbird",
            process_title="Thunderbird",
            pid=100,
        )
        self.w2 = AppWindow(
            xid=2,
            wnck_window=None,
            title="GitHub: kvakulo/Switcheroo - Firefox",
            process_title="Firefox",
            pid=200,
        )
        self.w3 = AppWindow(
            xid=3,
            wnck_window=None,
            title="Python Documentation - Firefox",
            process_title="Firefox",
            pid=200,
        )
        self.w4 = AppWindow(
            xid=4,
            wnck_window=None,
            title="main.py - Visual Studio Code",
            process_title="Code",
            pid=300,
        )
        self.windows = [self.w1, self.w2, self.w3, self.w4]

    def test_empty_query_returns_all(self):
        results = self.filterer.filter(self.windows, "")
        self.assertEqual(len(results), 4)

    def test_title_search(self):
        results = self.filterer.filter(self.windows, "inbox")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].xid, self.w1.xid)
        self.assertIn("<b>Inbox</b>", results[0].formatted_title)

    def test_process_search(self):
        results = self.filterer.filter(self.windows, "firefox")
        self.assertEqual(len(results), 2)
        xids = {r.xid for r in results}
        self.assertEqual(xids, {self.w2.xid, self.w3.xid})

    def test_dot_syntax_proc_and_title(self):
        # Format: <proc>.<title>
        results = self.filterer.filter(self.windows, "fire.python")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].xid, self.w3.xid)

    def test_dot_syntax_leading_dot_pinned_to_foreground(self):
        # Format: .<title> should pin process to foreground window
        # When foreground is Code:
        results = self.filterer.filter(
            self.windows, ".main", foreground_process_title="Code"
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].xid, self.w4.xid)

        # When foreground is Thunderbird, searching for .main yields nothing
        results_empty = self.filterer.filter(
            self.windows, ".main", foreground_process_title="Thunderbird"
        )
        self.assertEqual(len(results_empty), 0)


    def test_equal_scores_keep_input_order(self):
        # Both Firefox windows match only on process, so they tie; the input order
        # (MRU order from WindowFinder) decides the ranking.
        results = self.filterer.filter([self.w3, self.w1, self.w2], "firefox")
        self.assertEqual([r.xid for r in results], [self.w3.xid, self.w2.xid])

        results = self.filterer.filter([self.w2, self.w1, self.w3], "firefox")
        self.assertEqual([r.xid for r in results], [self.w2.xid, self.w3.xid])

    def test_higher_score_outranks_input_order(self):
        # Both match "set": a prefix match on "Settings" outscores a contains match on
        # "Reset Notes", even though the weaker match comes first in MRU order.
        weaker = AppWindow(xid=5, wnck_window=None, title="Reset Notes", process_title="Editor", pid=500)
        stronger = AppWindow(xid=6, wnck_window=None, title="Settings", process_title="Editor", pid=600)
        results = self.filterer.filter([weaker, stronger], "set")
        self.assertEqual([r.xid for r in results], [stronger.xid, weaker.xid])

    def test_empty_query_keeps_input_order(self):
        ordered = [self.w4, self.w2, self.w1, self.w3]
        results = self.filterer.filter(ordered, "")
        self.assertEqual([r.xid for r in results], [w.xid for w in ordered])


class TestLiteralDotQueries(unittest.TestCase):
    """A dot query that matches nothing as <proc>.<title> falls back to a plain search."""

    def setUp(self):
        self.filterer = WindowFilterer()
        self.readme = AppWindow(
            xid=10, wnck_window=None, title="README.md - Visual Studio Code",
            process_title="Code", pid=1000,
        )
        self.notes = AppWindow(
            xid=11, wnck_window=None, title="Release notes v1.2 - Firefox",
            process_title="Firefox", pid=1100,
        )
        self.config = AppWindow(
            xid=12, wnck_window=None, title="config.json - Text Editor",
            process_title="gedit", pid=1200,
        )
        self.main_py = AppWindow(
            xid=13, wnck_window=None, title="main.py - Visual Studio Code",
            process_title="Code", pid=1300,
        )
        self.windows = [self.readme, self.notes, self.config, self.main_py]

    def xids(self, query, foreground=None):
        return [w.xid for w in self.filterer.filter(self.windows, query, foreground)]

    def test_filename_with_extension(self):
        self.assertEqual(self.xids("README.md"), [self.readme.xid])
        self.assertEqual(self.xids("config.json"), [self.config.xid])

    def test_version_number(self):
        self.assertEqual(self.xids("v1.2"), [self.notes.xid])

    def test_fallback_highlights_the_literal_text(self):
        result = self.filterer.filter(self.windows, "README.md")[0]
        self.assertIn("<b>README.md</b>", result.formatted_title)

    def test_dot_syntax_still_wins_when_it_matches(self):
        # "code" matches the process of both Code windows; "main" narrows to main.py.
        self.assertEqual(self.xids("code.main"), [self.main_py.xid])

    def test_dot_syntax_match_is_not_mixed_with_plain_results(self):
        # As dot syntax, "code.readme" matches only the README window; the fallback
        # is not consulted, so nothing else is added.
        self.assertEqual(self.xids("code.readme"), [self.readme.xid])

    def test_leading_dot_falls_back_when_foreground_app_has_no_match(self):
        # ".md" pinned to Firefox matches nothing; as plain text it finds README.md.
        self.assertEqual(self.xids(".md", foreground="Firefox"), [self.readme.xid])

    def test_leading_dot_pinned_to_foreground_when_it_matches(self):
        self.assertEqual(self.xids(".main", foreground="Code"), [self.main_py.xid])


if __name__ == "__main__":
    unittest.main()
