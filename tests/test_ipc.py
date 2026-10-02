"""Unit tests for the IPC socket location and setup."""

import os
import socket
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from switcheroo.ipc import (
    IpcSocketError,
    create_server_socket,
    get_socket_path,
    is_own_socket,
    remove_stale_socket,
)


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


class SocketDirTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, "switcheroo.sock")

    def make_socket(self, path=None):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(path or self.path)
        self.addCleanup(sock.close)
        return sock

    def as_other_user(self):
        return mock.patch("switcheroo.ipc.os.getuid", return_value=os.getuid() + 1)


class TestIsOwnSocket(SocketDirTestCase):
    def test_own_socket(self):
        self.make_socket()
        self.assertTrue(is_own_socket(self.path))

    def test_missing_path(self):
        self.assertFalse(is_own_socket(self.path))

    def test_regular_file(self):
        Path(self.path).write_text("not a socket")
        self.assertFalse(is_own_socket(self.path))

    def test_symlink_to_socket(self):
        target = os.path.join(self.tmp.name, "real.sock")
        self.make_socket(target)
        os.symlink(target, self.path)
        self.assertFalse(is_own_socket(self.path))

    def test_socket_owned_by_another_user(self):
        self.make_socket()
        with self.as_other_user():
            self.assertFalse(is_own_socket(self.path))


class TestRemoveStaleSocket(SocketDirTestCase):
    def test_missing_path_is_noop(self):
        remove_stale_socket(self.path)

    def test_removes_own_stale_socket(self):
        self.make_socket()
        remove_stale_socket(self.path)
        self.assertFalse(os.path.lexists(self.path))

    def test_refuses_regular_file(self):
        Path(self.path).write_text("not a socket")
        with self.assertRaisesRegex(IpcSocketError, "not a socket"):
            remove_stale_socket(self.path)
        self.assertTrue(os.path.exists(self.path))

    def test_refuses_symlink(self):
        target = os.path.join(self.tmp.name, "real.sock")
        self.make_socket(target)
        os.symlink(target, self.path)
        with self.assertRaisesRegex(IpcSocketError, "not a socket"):
            remove_stale_socket(self.path)
        self.assertTrue(os.path.lexists(self.path))

    def test_refuses_socket_owned_by_another_user(self):
        self.make_socket()
        with self.as_other_user(), self.assertRaisesRegex(IpcSocketError, "another user"):
            remove_stale_socket(self.path)
        self.assertTrue(os.path.lexists(self.path))


class TestCreateServerSocket(SocketDirTestCase):
    def test_creates_listening_socket(self):
        server = create_server_socket(self.path)
        self.addCleanup(server.close)
        self.assertTrue(is_own_socket(self.path))

        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.addCleanup(client.close)
        client.connect(self.path)

    def test_replaces_stale_socket(self):
        self.make_socket().close()
        server = create_server_socket(self.path)
        self.addCleanup(server.close)
        self.assertTrue(is_own_socket(self.path))

    def test_refuses_foreign_socket(self):
        self.make_socket()
        with self.as_other_user(), self.assertRaises(IpcSocketError):
            create_server_socket(self.path)

    def test_bind_failure_raises_ipc_error(self):
        missing_dir = os.path.join(self.tmp.name, "missing", "switcheroo.sock")
        with self.assertRaisesRegex(IpcSocketError, "Cannot create IPC socket"):
            create_server_socket(missing_dir)


if __name__ == "__main__":
    unittest.main()
