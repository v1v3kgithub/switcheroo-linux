"""Location and setup of the single-instance IPC socket shared by the daemon and the CLI."""

import os
import socket
import stat
from pathlib import Path
from typing import Union

PathLike = Union[str, Path]


class IpcSocketError(RuntimeError):
    """The IPC socket cannot be created, e.g. its path is held by another user."""


def get_socket_path() -> Path:
    """Returns the IPC socket path, preferring the per-user runtime directory.

    `$XDG_RUNTIME_DIR` (typically `/run/user/<uid>`) is owned by the user and not
    accessible to others, so the socket cannot be pre-created or replaced by another
    local user. `/tmp` is only used when no runtime directory is available.
    """
    runtime_dir = os.environ.get("XDG_RUNTIME_DIR")
    if runtime_dir and os.path.isdir(runtime_dir):
        return Path(runtime_dir) / "switcheroo.sock"
    return Path("/tmp") / f"switcheroo-{os.getuid()}.sock"


def is_own_socket(path: PathLike) -> bool:
    """True if the path is a socket (not a symlink to one) owned by the current user."""
    try:
        st = os.lstat(path)
    except OSError:
        return False
    return stat.S_ISSOCK(st.st_mode) and st.st_uid == os.getuid()


def remove_stale_socket(path: PathLike) -> None:
    """Removes a socket left behind by a previous run, refusing to touch anything else."""
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        return
    except OSError as e:
        raise IpcSocketError(f"Cannot inspect IPC socket path {path}: {e.strerror}") from e

    if not stat.S_ISSOCK(st.st_mode):
        raise IpcSocketError(f"IPC socket path {path} exists but is not a socket; remove it and retry.")
    if st.st_uid != os.getuid():
        raise IpcSocketError(
            f"IPC socket path {path} is owned by another user (uid {st.st_uid}); refusing to use it."
        )

    try:
        os.unlink(path)
    except OSError as e:
        raise IpcSocketError(f"Cannot remove stale IPC socket {path}: {e.strerror}") from e


def create_server_socket(path: PathLike) -> socket.socket:
    """Creates the daemon's listening socket, replacing only a stale socket of our own."""
    remove_stale_socket(path)

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.bind(str(path))
        sock.listen(5)
    except OSError as e:
        sock.close()
        raise IpcSocketError(f"Cannot create IPC socket at {path}: {e.strerror}") from e
    sock.setblocking(False)
    return sock
