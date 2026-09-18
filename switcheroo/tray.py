"""System tray notification area indicator for Linux Mint."""

import logging
from typing import Callable, Optional

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from switcheroo.autostart import AutoStartManager
from switcheroo.config import Config

logger = logging.getLogger(__name__)

# Try importing AyatanaAppIndicator3, fallback to AppIndicator3, or None
AppIndicator = None
try:
    gi.require_version("AyatanaAppIndicator3", "0.1")
    from gi.repository import AyatanaAppIndicator3 as AppIndicator
except Exception:
    try:
        gi.require_version("AppIndicator3", "0.1")
        from gi.repository import AppIndicator3 as AppIndicator
    except Exception:
        pass


class TrayIndicator:
    """System tray icon and context menu."""

    def __init__(
        self,
        config: Config,
        on_toggle: Callable[[], None],
        on_quit: Callable[[], None],
    ) -> None:
        self.config = config
        self.on_toggle = on_toggle
        self.on_quit = on_quit
        self.indicator: Optional[object] = None
        self._setup_tray()

    def _setup_tray(self) -> None:
        menu = self._create_menu()

        if AppIndicator:
            try:
                self.indicator = AppIndicator.Indicator.new(
                    "switcheroo-indicator",
                    "preferences-system-windows",
                    AppIndicator.IndicatorCategory.APPLICATION_STATUS,
                )
                self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)
                self.indicator.set_menu(menu)
                logger.info("Initialized AyatanaAppIndicator tray icon.")
                return
            except Exception as e:
                logger.warning("Failed to initialize AyatanaAppIndicator: %s", e)

        # Fallback to Gtk.StatusIcon
        try:
            self.status_icon = Gtk.StatusIcon()
            self.status_icon.set_from_icon_name("preferences-system-windows")
            self.status_icon.set_tooltip_text("Switcheroo")
            self.status_icon.connect("activate", lambda *args: self.on_toggle())
            self.status_icon.connect(
                "popup-menu",
                lambda icon, button, time: menu.popup(
                    None, None, Gtk.StatusIcon.position_menu, icon, button, time
                ),
            )
            logger.info("Initialized Gtk.StatusIcon tray fallback.")
        except Exception as e:
            logger.error("Failed to initialize system tray: %s", e)

    def _create_menu(self) -> Gtk.Menu:
        menu = Gtk.Menu()

        # Show / Hide item
        item_show = Gtk.MenuItem(label=f"Show Switcheroo ({self.config.hotkey})")
        item_show.connect("activate", lambda *args: self.on_toggle())
        menu.append(item_show)

        menu.append(Gtk.SeparatorMenuItem())

        # Autostart checkbox item
        item_autostart = Gtk.CheckMenuItem(label="Run on Startup")
        item_autostart.set_active(AutoStartManager.is_enabled())
        item_autostart.connect("toggled", self._on_autostart_toggled)
        menu.append(item_autostart)

        # About item
        item_about = Gtk.MenuItem(label="About Switcheroo")
        item_about.connect("activate", self._show_about_dialog)
        menu.append(item_about)

        menu.append(Gtk.SeparatorMenuItem())

        # Exit item
        item_quit = Gtk.MenuItem(label="Quit")
        item_quit.connect("activate", lambda *args: self.on_quit())
        menu.append(item_quit)

        menu.show_all()
        return menu

    def _on_autostart_toggled(self, widget: Gtk.CheckMenuItem) -> None:
        enabled = widget.get_active()
        AutoStartManager.set_enabled(enabled)
        self.config.autostart = enabled
        self.config.save()

    def _show_about_dialog(self, _widget: Gtk.MenuItem) -> None:
        about = Gtk.AboutDialog()
        about.set_program_name("Switcheroo for Linux")
        about.set_version("1.0.0")
        about.set_comments(
            "The incremental-search task switcher for Linux Mint.\n"
            "Quickly switch to any open window by typing its title or process name."
        )
        about.set_logo_icon_name("preferences-system-windows")
        about.set_authors([
            "Ported for Linux Mint by the Open Source Community",
            "Original Windows Switcheroo by James Sulak & Regin Larsen",
        ])
        about.set_license_type(Gtk.License.GPL_3_0)
        about.set_website("https://github.com/v1v3kgithub/switcheroo-linux")
        about.connect("response", lambda dialog, response: dialog.destroy())
        about.show()
