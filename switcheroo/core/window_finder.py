"""Window discovery and enumeration using libwnck."""

from typing import Any, List, Optional, Tuple
import gi
gi.require_version("Wnck", "3.0")
from gi.repository import Wnck

from switcheroo.core.mru import MruTracker
from switcheroo.core.window_model import AppWindow


class WindowFinder:
    """Discovers and filters top-level desktop windows via libwnck."""

    def __init__(self, screen: Optional[Any] = None) -> None:
        self.screen = screen or Wnck.Screen.get_default()
        self.mru = MruTracker()

        # Long-lived subscriptions: the finder lives as long as the daemon, so focus
        # history accumulates between switcher invocations.
        self.screen.connect("active-window-changed", self._on_active_window_changed)
        self.screen.connect("window-closed", self._on_window_closed)

    def _on_active_window_changed(self, screen: Any, _previous: Any) -> None:
        active = screen.get_active_window()
        if active:
            self.mru.touch(active.get_xid())

    def _on_window_closed(self, _screen: Any, window: Any) -> None:
        self.mru.forget(window.get_xid())

    def get_windows(self) -> Tuple[List[AppWindow], Optional[AppWindow]]:
        """Returns taskbar windows in MRU order, and the currently active foreground window."""
        self.screen.force_update()

        # Windows not yet seen activated take their order from the stacking order,
        # topmost (most recently raised) first.
        self.mru.seed(w.get_xid() for w in reversed(self.screen.get_windows_stacked()))

        active_wnck = self.screen.get_active_window()
        if active_wnck:
            self.mru.touch(active_wnck.get_xid())
        active_app_window: Optional[AppWindow] = None

        all_windows = self.screen.get_windows()
        window_list: List[AppWindow] = []

        for w in all_windows:
            # Skip hidden, tasklist-ignored, or non-normal windows (panels, docks, desktop)
            if w.is_skip_tasklist():
                continue

            if w.get_window_type() != Wnck.WindowType.NORMAL:
                continue

            title = w.get_name()
            if not title or not title.strip():
                continue

            # Skip desktop surface icons (nemo-desktop)
            class_instance = w.get_class_instance_name() or ""
            if class_instance == "nemo-desktop":
                continue

            app = w.get_application()
            if app and app.get_name():
                proc_name = app.get_name()
            else:
                proc_name = (
                    w.get_class_group_name()
                    or class_instance
                    or "Application"
                )

            icon = w.get_icon() or w.get_mini_icon()

            app_win = AppWindow(
                xid=w.get_xid(),
                wnck_window=w,
                title=title.strip(),
                process_title=proc_name.strip(),
                pid=w.get_pid(),
                icon_pixbuf=icon,
            )

            if active_wnck and w.get_xid() == active_wnck.get_xid():
                active_app_window = app_win

            window_list.append(app_win)

        window_list = self.mru.sort(window_list)

        # The active window is the one being switched away from, so list it last and the
        # previously used window is selected first, as in the original Switcheroo.
        if active_app_window:
            window_list = [w for w in window_list if w is not active_app_window]
            window_list.append(active_app_window)

        return window_list, active_app_window
