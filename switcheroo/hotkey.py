"""Global keyboard shortcut manager using libkeybinder."""

import logging
from typing import Callable, Optional

import gi
gi.require_version("Keybinder", "3.0")
from gi.repository import Keybinder

logger = logging.getLogger(__name__)


class HotkeyManager:
    """Manages global X11 hotkey registration with libkeybinder."""

    def __init__(self, callback: Callable[[], None]) -> None:
        self._callback = callback
        self._current_hotkey: Optional[str] = None
        self._initialized = False

    def init(self) -> None:
        if not self._initialized:
            try:
                Keybinder.init()
                self._initialized = True
            except Exception as e:
                logger.error("Failed to initialize Keybinder: %s", e)

    def register(self, keystring: str) -> bool:
        """Binds a global shortcut string (e.g. '<Alt>space')."""
        self.init()

        if self._current_hotkey:
            self.unregister()

        try:
            success = Keybinder.bind(keystring, self._on_activated, None)
            if success:
                self._current_hotkey = keystring
                logger.info("Registered hotkey: %s", keystring)
                return True
            else:
                logger.warning("Keybinder.bind returned False for %s", keystring)
                return False
        except Exception as e:
            logger.error("Error registering hotkey %s: %s", keystring, e)
            return False

    def unregister(self) -> None:
        if self._current_hotkey and self._initialized:
            try:
                Keybinder.unbind(self._current_hotkey)
                logger.info("Unbound hotkey: %s", self._current_hotkey)
            except Exception as e:
                logger.error("Error unbinding hotkey %s: %s", self._current_hotkey, e)
            self._current_hotkey = None

    def _on_activated(self, _keystring: str, _user_data: object) -> None:
        try:
            self._callback()
        except Exception as e:
            logger.error("Error in hotkey callback: %s", e)
