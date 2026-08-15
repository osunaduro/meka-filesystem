"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - write_media()

Purpose:
    Write raw binary content to a file.
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops.write_media

Public API:
    write_media

Dependencies:
    pathlib
    workspace.internal.path

Thread Safe:
    yes

Pure:
    no
"""

from pathlib import Path

from workspace.internal.path import resolve as resolve_path


def write_media(root: Path, path: str | Path, data: bytes) -> None:
    """Write raw binary content to a file.

    Counterpart to ``read_media``: writes bytes as-is, with no text
    encoding involved, so it is safe for images, audio, or any other
    binary format.

    Parameters
    ----------
    root : Path
        Workspace root.

    path : str | Path
        Relative path inside the workspace.

    data : bytes
        Raw binary content to write.
    """

    target = resolve_path(root, path)

    target.write_bytes(data)
