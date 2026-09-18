"""Configuration management for Switcheroo."""

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Config:
    """User configuration options."""
    hotkey: str = "<Alt>space"
    autostart: bool = False
    max_results: int = 12
    window_width: int = 560
    show_help: bool = False

    @classmethod
    def get_config_dir(cls) -> Path:
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config:
            path = Path(xdg_config) / "switcheroo"
        else:
            path = Path.home() / ".config" / "switcheroo"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def get_config_file(cls) -> Path:
        return cls.get_config_dir() / "config.json"

    @classmethod
    def load(cls) -> "Config":
        cfg_file = cls.get_config_file()
        if not cfg_file.exists():
            config = cls()
            config.save()
            return config

        try:
            with open(cfg_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        except Exception:
            return cls()

    def save(self) -> None:
        cfg_file = self.get_config_file()
        with open(cfg_file, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2)
