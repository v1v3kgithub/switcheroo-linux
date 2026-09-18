"""Tests for Config dataclass and file persistence."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from switcheroo.config import Config


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_dir = Path(self.temp_dir.name)
        self.config_file = self.config_dir / "config.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_default_values(self):
        cfg = Config()
        self.assertEqual(cfg.hotkey, "<Alt>space")
        self.assertFalse(cfg.autostart)
        self.assertEqual(cfg.max_results, 12)
        self.assertEqual(cfg.window_width, 560)
        self.assertEqual(cfg.window_height, 500)
        self.assertFalse(cfg.show_help)

    def test_load_nonexistent_creates_default(self):
        with patch.object(Config, "get_config_file", return_value=self.config_file):
            cfg = Config.load()
            self.assertEqual(cfg.window_height, 500)
            self.assertEqual(cfg.window_width, 560)
            self.assertTrue(self.config_file.exists())

    def test_load_existing_file(self):
        custom_data = {
            "hotkey": "<Super>space",
            "autostart": True,
            "max_results": 20,
            "window_width": 700,
            "window_height": 650,
            "show_help": True,
        }
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(custom_data, f)

        with patch.object(Config, "get_config_file", return_value=self.config_file):
            cfg = Config.load()
            self.assertEqual(cfg.hotkey, "<Super>space")
            self.assertTrue(cfg.autostart)
            self.assertEqual(cfg.max_results, 20)
            self.assertEqual(cfg.window_width, 700)
            self.assertEqual(cfg.window_height, 650)
            self.assertTrue(cfg.show_help)

    def test_load_missing_fields_fills_defaults_and_saves(self):
        # Simulate legacy config without window_height
        legacy_data = {
            "hotkey": "<Control><Alt>space",
            "autostart": False,
            "max_results": 18,
            "window_width": 560,
            "show_help": False,
        }
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(legacy_data, f)

        with patch.object(Config, "get_config_file", return_value=self.config_file):
            cfg = Config.load()
            self.assertEqual(cfg.max_results, 18)
            self.assertEqual(cfg.window_height, 500)

            # Check that window_height was written to disk
            with open(self.config_file, "r", encoding="utf-8") as f:
                saved = json.load(f)
            self.assertIn("window_height", saved)
            self.assertEqual(saved["window_height"], 500)
            self.assertEqual(saved["max_results"], 18)


if __name__ == "__main__":
    unittest.main()
