"""Unit tests for MruTracker."""

import unittest
from switcheroo.core.mru import MruTracker
from switcheroo.core.window_model import AppWindow


def make_window(xid: int) -> AppWindow:
    return AppWindow(
        xid=xid,
        wnck_window=None,
        title=f"Window {xid}",
        process_title="App",
        pid=xid,
    )


class TestMruTracker(unittest.TestCase):
    def setUp(self):
        self.mru = MruTracker()

    def test_touch_moves_to_front(self):
        self.mru.touch(1)
        self.mru.touch(2)
        self.mru.touch(3)
        self.assertEqual(self.mru.xids, [3, 2, 1])

        self.mru.touch(1)
        self.assertEqual(self.mru.xids, [1, 3, 2])

    def test_touch_same_window_twice_is_idempotent(self):
        self.mru.touch(1)
        self.mru.touch(1)
        self.assertEqual(self.mru.xids, [1])

    def test_forget_removes_window(self):
        self.mru.touch(1)
        self.mru.touch(2)
        self.mru.forget(1)
        self.assertEqual(self.mru.xids, [2])

    def test_forget_unknown_window_is_noop(self):
        self.mru.touch(1)
        self.mru.forget(99)
        self.assertEqual(self.mru.xids, [1])

    def test_seed_appends_behind_observed_activations(self):
        self.mru.touch(5)
        self.mru.seed([1, 5, 2])
        self.assertEqual(self.mru.xids, [5, 1, 2])

    def test_sort_orders_by_recency(self):
        windows = [make_window(1), make_window(2), make_window(3)]
        self.mru.touch(1)
        self.mru.touch(3)
        self.mru.touch(2)
        self.assertEqual([w.xid for w in self.mru.sort(windows)], [2, 3, 1])

    def test_sort_appends_untracked_in_given_order(self):
        windows = [make_window(4), make_window(1), make_window(5), make_window(2)]
        self.mru.touch(1)
        self.mru.touch(2)
        self.assertEqual([w.xid for w in self.mru.sort(windows)], [2, 1, 4, 5])

    def test_sort_ignores_tracked_xids_without_a_window(self):
        windows = [make_window(1), make_window(2)]
        self.mru.touch(1)
        self.mru.touch(99)
        self.mru.touch(2)
        self.assertEqual([w.xid for w in self.mru.sort(windows)], [2, 1])

    def test_sort_does_not_mutate_input(self):
        windows = [make_window(1), make_window(2)]
        self.mru.touch(2)
        self.mru.sort(windows)
        self.assertEqual([w.xid for w in windows], [1, 2])


if __name__ == "__main__":
    unittest.main()
