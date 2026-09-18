"""Window model representation."""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class AppWindow:
    """Represents an open desktop window with metadata and underlying Wnck handle."""
    xid: int
    wnck_window: Any
    title: str
    process_title: str
    pid: int
    icon_pixbuf: Optional[Any] = None
    formatted_title: str = ""
    formatted_process_title: str = ""
    is_being_closed: bool = False

    def close(self, timestamp: int = 0) -> None:
        """Requests graceful closure of the window."""
        self.is_being_closed = True
        if self.wnck_window:
            self.wnck_window.close(timestamp)

    def switch_to(self, timestamp: int = 0) -> None:
        """Brings the window to the foreground and focuses it."""
        if self.wnck_window:
            self.wnck_window.activate(timestamp)
