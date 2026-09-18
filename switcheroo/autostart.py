"""Autostart desktop entry manager."""

import os
import shutil
from pathlib import Path


class AutoStartManager:
    """Controls whether Switcheroo starts automatically upon login."""

    DESKTOP_ENTRY_NAME = "switcheroo.desktop"

    @classmethod
    def get_autostart_path(cls) -> Path:
        autostart_dir = Path.home() / ".config" / "autostart"
        autostart_dir.mkdir(parents=True, exist_ok=True)
        return autostart_dir / cls.DESKTOP_ENTRY_NAME

    @classmethod
    def is_enabled(cls) -> bool:
        return cls.get_autostart_path().exists()

    @classmethod
    def set_enabled(cls, enable: bool) -> bool:
        autostart_file = cls.get_autostart_path()
        if enable:
            content = """[Desktop Entry]
Type=Application
Name=Switcheroo
Comment=The incremental-search task switcher for Linux Mint
Exec=switcheroo
Icon=switcheroo
Terminal=false
Categories=Utility;
StartupNotify=false
X-GNOME-Autostart-enabled=true
"""
            try:
                with open(autostart_file, "w", encoding="utf-8") as f:
                    f.write(content)
                return True
            except IOError:
                return False
        else:
            if autostart_file.exists():
                try:
                    autostart_file.unlink()
                except OSError:
                    return False
            return True
