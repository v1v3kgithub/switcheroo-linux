"""Main application coordinator and single-instance manager."""

import argparse
import logging
import os
import signal
import socket
import sys
from pathlib import Path
from typing import Optional

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

from switcheroo.config import Config
from switcheroo.hotkey import HotkeyManager
from switcheroo.tray import TrayIndicator
from switcheroo.ui.window import SwitcherWindow

logger = logging.getLogger("switcheroo")


class SwitcherooApp:
    """Coordinates window, hotkey, tray, and single-instance IPC."""

    SOCKET_PATH = f"/tmp/switcheroo-{os.getuid()}.sock"

    def __init__(self, config: Config) -> None:
        self.config = config
        self.window = SwitcherWindow(self.config)
        self.hotkey = HotkeyManager(self.toggle_switcher)
        self.tray = TrayIndicator(self.config, self.toggle_switcher, self.quit)
        self.server_sock: Optional[socket.socket] = None

    def toggle_switcher(self) -> None:
        GLib.idle_add(self.window.toggle)

    def show_switcher(self) -> None:
        GLib.idle_add(self.window.show_switcher)

    def hide_switcher(self) -> None:
        GLib.idle_add(self.window.hide_switcher)

    def quit(self) -> None:
        logger.info("Quitting Switcheroo...")
        self.hotkey.unregister()
        if self.server_sock:
            try:
                self.server_sock.close()
            except Exception:
                pass
        if os.path.exists(self.SOCKET_PATH):
            try:
                os.unlink(self.SOCKET_PATH)
            except Exception:
                pass
        Gtk.main_quit()

    def start_ipc_server(self) -> None:
        """Starts Unix domain socket listener for CLI toggle signals."""
        if os.path.exists(self.SOCKET_PATH):
            try:
                os.unlink(self.SOCKET_PATH)
            except Exception:
                pass

        self.server_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server_sock.bind(self.SOCKET_PATH)
        self.server_sock.listen(5)
        self.server_sock.setblocking(False)

        def handle_socket_connection(source, condition):
            try:
                conn, _ = self.server_sock.accept()
                data = conn.recv(1024).decode("utf-8").strip()
                conn.close()

                if data == "show":
                    self.show_switcher()
                elif data == "hide":
                    self.hide_switcher()
                elif data == "quit":
                    self.quit()
                else:
                    self.toggle_switcher()
            except Exception as e:
                logger.error("IPC socket error: %s", e)
            return True

        GLib.io_add_watch(
            self.server_sock.fileno(),
            GLib.IO_IN,
            handle_socket_connection,
        )

    def run(self, show_immediately: bool = False) -> None:
        """Starts the Switcheroo background daemon."""
        self.start_ipc_server()

        # Bind configured global hotkey
        success = self.hotkey.register(self.config.hotkey)
        if not success:
            logger.warning(
                "Could not register global hotkey '%s'. It may be in use by another app.",
                self.config.hotkey,
            )

        # Handle termination signals cleanly
        signal.signal(signal.SIGINT, lambda *args: self.quit())
        signal.signal(signal.SIGTERM, lambda *args: self.quit())

        if show_immediately:
            self.show_switcher()

        logger.info("Switcheroo daemon running. Press %s to toggle.", self.config.hotkey)
        Gtk.main()


def send_ipc_command(command: str) -> bool:
    """Attempts to send a command to an existing running Switcheroo instance."""
    sock_path = f"/tmp/switcheroo-{os.getuid()}.sock"
    if not os.path.exists(sock_path):
        return False

    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(sock_path)
        client.sendall(command.encode("utf-8"))
        client.close()
        return True
    except Exception:
        return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Switcheroo: Incremental-search task switcher for Linux Mint."
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Show the switcher window immediately.",
    )
    parser.add_argument(
        "--toggle",
        action="store_true",
        help="Toggle visibility of the switcher window.",
    )
    parser.add_argument(
        "--quit",
        action="store_true",
        help="Terminate running Switcheroo daemon.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging output.",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Check if daemon is already running
    if args.quit:
        if send_ipc_command("quit"):
            print("Switcheroo daemon stopped.")
        else:
            print("No running Switcheroo daemon found.")
        sys.exit(0)

    if args.toggle or args.show:
        cmd = "show" if args.show else "toggle"
        if send_ipc_command(cmd):
            sys.exit(0)

    # If already running and invoked with no args, toggle the running instance
    if send_ipc_command("toggle"):
        sys.exit(0)

    # Otherwise, start as daemon
    config = Config.load()
    app = SwitcherooApp(config)
    app.run(show_immediately=args.show)


if __name__ == "__main__":
    main()
