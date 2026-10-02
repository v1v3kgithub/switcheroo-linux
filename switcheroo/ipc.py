"""Location of the single-instance IPC socket shared by the daemon and the CLI."""

import os
from pathlib import Path


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
