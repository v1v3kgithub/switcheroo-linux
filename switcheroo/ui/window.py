"""Main GTK3 overlay window for Switcheroo."""

import os
from pathlib import Path
from typing import List, Optional

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import Gdk, GdkPixbuf, GLib, Gtk

from switcheroo.config import Config
from switcheroo.core.filterer import WindowFilterer
from switcheroo.core.window_finder import WindowFinder
from switcheroo.core.window_model import AppWindow


class WindowRow(Gtk.ListBoxRow):
    """Custom ListBox row displaying an application window item."""

    def __init__(self, app_window: AppWindow) -> None:
        super().__init__()
        self.app_window = app_window
        self.get_style_context().add_class("window-row")

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_margin_top(4)
        box.set_margin_bottom(4)
        box.set_margin_start(6)
        box.set_margin_end(6)

        # Application icon
        self.image = Gtk.Image()
        if app_window.icon_pixbuf:
            try:
                scaled = app_window.icon_pixbuf.scale_simple(
                    22, 22, GdkPixbuf.InterpType.BILINEAR
                )
                self.image.set_from_pixbuf(scaled)
            except Exception:
                self.image.set_from_icon_name("application-x-executable", Gtk.IconSize.LARGE_TOOLBAR)
        else:
            self.image.set_from_icon_name("application-x-executable", Gtk.IconSize.LARGE_TOOLBAR)
        box.pack_start(self.image, False, False, 0)

        # Window Title label
        self.title_label = Gtk.Label()
        self.title_label.set_use_markup(True)
        self.title_label.set_ellipsize(3)  # PANGO_ELLIPSIZE_END
        self.title_label.set_xalign(0.0)
        self.title_label.get_style_context().add_class("window-title")
        self.update_title()
        box.pack_start(self.title_label, True, True, 0)

        # Process/Application Name label
        self.proc_label = Gtk.Label()
        self.proc_label.set_use_markup(True)
        self.proc_label.set_ellipsize(3)  # PANGO_ELLIPSIZE_END
        self.proc_label.set_xalign(1.0)
        self.proc_label.get_style_context().add_class("process-title")
        self.update_process_title()
        box.pack_end(self.proc_label, False, False, 0)

        self.add(box)
        self.show_all()

    def update_title(self) -> None:
        markup = self.app_window.formatted_title or GLib.markup_escape_text(self.app_window.title)
        self.title_label.set_markup(markup)

    def update_process_title(self) -> None:
        markup = (
            self.app_window.formatted_process_title
            or GLib.markup_escape_text(self.app_window.process_title)
        )
        self.proc_label.set_markup(markup)

    def mark_closing(self) -> None:
        self.get_style_context().add_class("being-closed")


class SwitcherWindow(Gtk.Window):
    """The floating, keyboard-driven window switcher overlay."""

    def __init__(self, config: Config) -> None:
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.config = config
        self.finder = WindowFinder()
        self.filterer = WindowFilterer()

        self._windows: List[AppWindow] = []
        self._filtered_windows: List[AppWindow] = []
        self._foreground_process: Optional[str] = None
        self._is_switching = False

        self._setup_window_properties()
        self._load_css()
        self._build_ui()
        self._connect_signals()

    def _setup_window_properties(self) -> None:
        self.set_title("Switcheroo")
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_keep_above(True)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(self.config.window_width, 380)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)
            self.set_app_paintable(True)

        self.get_style_context().add_class("switcheroo-window")

    def _load_css(self) -> None:
        css_file = Path(__file__).parent / "style.css"
        if css_file.exists():
            provider = Gtk.CssProvider()
            provider.load_from_path(str(css_file))
            Gtk.StyleContext.add_provider_for_screen(
                Gdk.Screen.get_default(),
                provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )

    def _build_ui(self) -> None:
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        container.get_style_context().add_class("switcheroo-container")
        self.add(container)

        # Top search container
        search_box_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        search_box_container.get_style_context().add_class("search-container")

        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Type to search windows...")
        self.search_entry.get_style_context().add_class("search-box")
        search_box_container.pack_start(self.search_entry, True, True, 0)

        self.help_btn = Gtk.Button(label="?")
        self.help_btn.get_style_context().add_class("help-toggle-btn")
        self.help_btn.set_tooltip_text("Toggle shortcut cheat sheet")
        search_box_container.pack_end(self.help_btn, False, False, 0)

        container.pack_start(search_box_container, False, False, 0)

        # Help cheat sheet banner
        self.help_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        self.help_bar.get_style_context().add_class("help-bar")

        hints = [
            ("Enter", "switch"),
            ("Ctrl+W", "close"),
            ("Tab / ↑↓", "navigate"),
            ("Esc", "dismiss"),
        ]
        for key, desc in hints:
            h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
            lbl_key = Gtk.Label(label=f"<b>{key}</b>")
            lbl_key.set_use_markup(True)
            lbl_key.get_style_context().add_class("help-shortcut")
            lbl_desc = Gtk.Label(label=desc)
            h_box.pack_start(lbl_key, False, False, 0)
            h_box.pack_start(lbl_desc, False, False, 0)
            self.help_bar.pack_start(h_box, False, False, 0)

        self.help_bar.set_no_show_all(True)
        self.help_bar.set_visible(self.config.show_help)
        container.pack_start(self.help_bar, False, False, 0)

        # Window list inside scroll area
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(
            Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC
        )
        self.scrolled_window.set_min_content_height(280)
        self.scrolled_window.set_max_content_height(450)
        self.scrolled_window.set_propagate_natural_height(True)

        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.list_box.set_activate_on_single_click(False)
        self.list_box.get_style_context().add_class("window-list")
        self.scrolled_window.add(self.list_box)

        container.pack_start(self.scrolled_window, True, True, 0)

    def _connect_signals(self) -> None:
        self.connect("key-press-event", self._on_key_press)
        self.connect("focus-out-event", self._on_focus_out)
        self.connect("delete-event", lambda *args: True)

        self.search_entry.connect("changed", self._on_search_changed)
        self.help_btn.connect("clicked", self._toggle_help)
        self.list_box.connect("row-activated", self._on_row_activated)

    def _toggle_help(self, _widget: Gtk.Widget) -> None:
        new_state = not self.help_bar.get_visible()
        self.help_bar.set_visible(new_state)
        self.config.show_help = new_state
        self.config.save()
        self.search_entry.grab_focus()

    def show_switcher(self) -> None:
        """Refreshes open windows and presents the switcher overlay."""
        self._is_switching = False
        windows, active_window = self.finder.get_windows()
        self._windows = windows
        self._foreground_process = (
            active_window.process_title if active_window else None
        )

        self.search_entry.set_text("")
        self._update_list("")

        self.show_all()
        self.help_bar.set_visible(self.config.show_help)
        self.present()
        self.search_entry.grab_focus()

    def hide_switcher(self) -> None:
        """Hides the switcher overlay."""
        self.hide()

    def toggle(self) -> None:
        if self.is_visible():
            self.hide_switcher()
        else:
            self.show_switcher()

    def _update_list(self, query: str) -> None:
        # Clear existing rows
        for child in self.list_box.get_children():
            self.list_box.remove(child)

        self._filtered_windows = self.filterer.filter(
            self._windows, query, self._foreground_process
        )

        for win in self._filtered_windows:
            row = WindowRow(win)
            self.list_box.add(row)

        self.list_box.show_all()

        # Pre-select first item
        first_row = self.list_box.get_row_at_index(0)
        if first_row:
            self.list_box.select_row(first_row)

    def _on_search_changed(self, entry: Gtk.Entry) -> None:
        query = entry.get_text().strip()
        self._update_list(query)

    def _on_key_press(self, _widget: Gtk.Widget, event: Gdk.EventKey) -> bool:
        keyval = event.keyval
        state = event.state

        ctrl_pressed = bool(state & Gdk.ModifierType.CONTROL_MASK)
        alt_pressed = bool(state & Gdk.ModifierType.MOD1_MASK)
        shift_pressed = bool(state & Gdk.ModifierType.SHIFT_MASK)

        # Dismiss on Escape
        if keyval == Gdk.KEY_Escape:
            self.hide_switcher()
            return True

        # Activate on Enter (without Ctrl)
        if (keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter)) and not ctrl_pressed:
            self._activate_selected()
            return True

        # Close selected window on Ctrl+W or Alt+X
        if (ctrl_pressed and keyval in (Gdk.KEY_w, Gdk.KEY_W)) or (
            alt_pressed and keyval in (Gdk.KEY_x, Gdk.KEY_X)
        ):
            self._close_selected()
            return True

        # Navigate Down: Down arrow, Tab (without Shift), or Alt+J
        if (
            keyval == Gdk.KEY_Down
            or (keyval == Gdk.KEY_Tab and not shift_pressed)
            or (alt_pressed and keyval in (Gdk.KEY_j, Gdk.KEY_J))
        ):
            self._navigate_list(1)
            return True

        # Navigate Up: Up arrow, Shift+Tab, or Alt+K
        if (
            keyval == Gdk.KEY_Up
            or (keyval in (Gdk.KEY_ISO_Left_Tab, Gdk.KEY_Tab) and shift_pressed)
            or (alt_pressed and keyval in (Gdk.KEY_k, Gdk.KEY_K))
        ):
            self._navigate_list(-1)
            return True

        return False

    def _navigate_list(self, delta: int) -> None:
        children = self.list_box.get_children()
        count = len(children)
        if count == 0:
            return

        selected_row = self.list_box.get_selected_row()
        current_idx = selected_row.get_index() if selected_row else 0
        new_idx = (current_idx + delta) % count

        target_row = self.list_box.get_row_at_index(new_idx)
        if target_row:
            self.list_box.select_row(target_row)
            target_row.grab_focus()
            self.search_entry.grab_focus()

    def _activate_selected(self) -> None:
        selected_row = self.list_box.get_selected_row()
        if not selected_row:
            return

        app_win: AppWindow = selected_row.app_window
        self._is_switching = True
        self.hide_switcher()
        app_win.switch_to(Gtk.get_current_event_time())

    def _close_selected(self) -> None:
        selected_row = self.list_box.get_selected_row()
        if not selected_row:
            return

        app_win: AppWindow = selected_row.app_window
        selected_row.mark_closing()
        app_win.close(Gtk.get_current_event_time())

        # Remove from data lists
        idx = selected_row.get_index()
        if app_win in self._windows:
            self._windows.remove(app_win)
        if app_win in self._filtered_windows:
            self._filtered_windows.remove(app_win)

        # Animate removal after brief delay
        def remove_row() -> bool:
            self.list_box.remove(selected_row)
            # Reselect adjacent item
            new_row = self.list_box.get_row_at_index(min(idx, len(self.list_box.get_children()) - 1))
            if new_row:
                self.list_box.select_row(new_row)
            elif len(self.list_box.get_children()) == 0:
                self.hide_switcher()
            return False

        GLib.timeout_add(150, remove_row)

    def _on_row_activated(self, _box: Gtk.ListBox, row: WindowRow) -> None:
        if row and row.app_window:
            self._is_switching = True
            self.hide_switcher()
            row.app_window.switch_to(Gtk.get_current_event_time())

    def _on_focus_out(self, _widget: Gtk.Widget, _event: Gdk.EventFocus) -> bool:
        if not self._is_switching:
            self.hide_switcher()
        return False
