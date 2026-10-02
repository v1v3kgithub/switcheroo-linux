"""Unit tests for WindowFinder ordering, using a fake Wnck screen."""

import unittest
from typing import Any, Callable, Dict, List, Optional

import gi
gi.require_version("Wnck", "3.0")
from gi.repository import Wnck

from switcheroo.core.window_finder import WindowFinder


class FakeWnckWindow:
    def __init__(self, xid: int, title: str = "", pid: int = 0) -> None:
        self._xid = xid
        self._title = title or f"Window {xid}"
        self._pid = pid or xid

    def get_xid(self) -> int:
        return self._xid

    def get_name(self) -> str:
        return self._title

    def get_pid(self) -> int:
        return self._pid

    def is_skip_tasklist(self) -> bool:
        return False

    def get_window_type(self) -> Wnck.WindowType:
        return Wnck.WindowType.NORMAL

    def get_class_instance_name(self) -> str:
        return "app"

    def get_class_group_name(self) -> str:
        return "App"

    def get_application(self) -> None:
        return None

    def get_icon(self) -> None:
        return None

    def get_mini_icon(self) -> None:
        return None


class FakeWnckScreen:
    """Windows are held in opening order; `stacked` is bottom-to-top, like Wnck."""

    def __init__(self, windows: List[FakeWnckWindow]) -> None:
        self.windows = list(windows)
        self.stacked = list(windows)
        self.active: Optional[FakeWnckWindow] = None
        self._handlers: Dict[str, Callable[..., Any]] = {}

    def connect(self, signal: str, handler: Callable[..., Any]) -> int:
        self._handlers[signal] = handler
        return len(self._handlers)

    def force_update(self) -> None:
        pass

    def get_windows(self) -> List[FakeWnckWindow]:
        return list(self.windows)

    def get_windows_stacked(self) -> List[FakeWnckWindow]:
        return list(self.stacked)

    def get_active_window(self) -> Optional[FakeWnckWindow]:
        return self.active

    def activate(self, window: FakeWnckWindow) -> None:
        previous = self.active
        self.active = window
        self.stacked.remove(window)
        self.stacked.append(window)
        self._handlers["active-window-changed"](self, previous)

    def close(self, window: FakeWnckWindow) -> None:
        self.windows.remove(window)
        self.stacked.remove(window)
        if self.active is window:
            self.active = None
        self._handlers["window-closed"](self, window)


class TestWindowFinderOrdering(unittest.TestCase):
    def setUp(self):
        self.w1, self.w2, self.w3, self.w4 = (FakeWnckWindow(x) for x in (1, 2, 3, 4))
        self.screen = FakeWnckScreen([self.w1, self.w2, self.w3, self.w4])
        self.finder = WindowFinder(screen=self.screen)

    def xids(self) -> List[int]:
        windows, _active = self.finder.get_windows()
        return [w.xid for w in windows]

    def test_without_activations_order_follows_stacking(self):
        # Topmost first; stacking differs from opening order.
        self.screen.stacked = [self.w2, self.w4, self.w1, self.w3]
        self.assertEqual(self.xids(), [3, 1, 4, 2])

    def test_orders_by_most_recent_activation_not_opening_order(self):
        for w in (self.w3, self.w1, self.w4, self.w2):
            self.screen.activate(w)
        # w2 is active, so it goes last; w4 was used before it and comes first.
        self.assertEqual(self.xids(), [4, 1, 3, 2])

    def test_previous_window_is_first_for_hotkey_enter_flow(self):
        self.screen.activate(self.w1)
        self.screen.activate(self.w4)
        windows, active = self.finder.get_windows()
        self.assertEqual(active.xid, 4)
        self.assertEqual(windows[0].xid, 1)
        self.assertEqual(windows[-1].xid, 4)

    def test_history_persists_between_invocations(self):
        self.screen.activate(self.w2)
        self.screen.activate(self.w3)
        self.assertEqual(self.xids()[0], 2)

        # Switch back to w2 via the switcher; w3 should now be offered first.
        self.screen.activate(self.w2)
        self.assertEqual(self.xids()[0], 3)

    def test_closed_window_is_forgotten(self):
        self.screen.activate(self.w3)
        self.screen.activate(self.w1)
        self.screen.close(self.w3)
        self.assertNotIn(3, self.finder.mru.xids)
        self.assertNotIn(3, self.xids())

    def test_active_window_seen_without_signal_is_still_last(self):
        # Activation that happened before the signal subscription took effect.
        self.screen.active = self.w2
        windows, active = self.finder.get_windows()
        self.assertEqual(active.xid, 2)
        self.assertEqual(windows[-1].xid, 2)

    def test_no_active_window(self):
        self.screen.stacked = [self.w1, self.w2, self.w3, self.w4]
        windows, active = self.finder.get_windows()
        self.assertIsNone(active)
        self.assertEqual([w.xid for w in windows], [4, 3, 2, 1])


if __name__ == "__main__":
    unittest.main()
