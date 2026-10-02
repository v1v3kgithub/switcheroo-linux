"""Unit tests for the IPC socket location and setup."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from switcheroo.ipc import get_socket_path


class TestGetSocketPath(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_uses_runtime_dir_when_set(self):
        with mock.patch.dict(os.environ, {"XDG_RUNTIME_DIR": self.tmp.name}):
            self.assertEqual(get_socket_path(), Path(self.tmp.name) / "switcheroo.sock")

    def test_falls_back_to_tmp_when_unset(self):
        env = {k: v for k, v in os.environ.items() if k != "XDG_RUNTIME_DIR"}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(
                get_socket_path(), Path("/tmp") / f"switcheroo-{os.getuid()}.sock"
            )

    def test_falls_back_to_tmp_when_empty(self):
        with mock.patch.dict(os.environ, {"XDG_RUNTIME_DIR": ""}):
            self.assertEqual(
                get_socket_path(), Path("/tmp") / f"switcheroo-{os.getuid()}.sock"
            )

    def test_falls_back_to_tmp_when_runtime_dir_missing(self):
        missing = os.path.join(self.tmp.name, "does-not-exist")
        with mock.patch.dict(os.environ, {"XDG_RUNTIME_DIR": missing}):
            self.assertEqual(
                get_socket_path(), Path("/tmp") / f"switcheroo-{os.getuid()}.sock"
            )


if __name__ == "__main__":
    unittest.main()
