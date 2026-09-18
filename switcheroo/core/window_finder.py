"""Window discovery and enumeration using libwnck."""

from typing import List, Optional, Tuple
import gi
gi.require_version("Wnck", "3.0")
from gi.repository import Wnck

from switcheroo.core.window_model import AppWindow


class WindowFinder:
    """Discovers and filters top-level desktop windows via libwnck."""

    def __init__(self) -> None:
        self.screen = Wnck.Screen.get_default()

    def get_windows(self) -> Tuple[List[AppWindow], Optional[AppWindow]]:
        """Returns a list of taskbar windows and the currently active foreground window."""
        self.screen.force_update()
        active_wnck = self.screen.get_active_window()
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

        # Reorder: if the active window is at the top of the list, move it to the bottom.
        # This mirrors Switcheroo's MRU behavior so the previously focused window is selected first.
        if window_list and active_app_window:
            if window_list[0].xid == active_app_window.xid or (
                window_list[0].pid == active_app_window.pid and window_list[0].pid > 0
            ):
                first = window_list.pop(0)
                window_list.append(first)

        return window_list, active_app_window
