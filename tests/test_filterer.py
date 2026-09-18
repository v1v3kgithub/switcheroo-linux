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


if __name__ == "__main__":
    unittest.main()
