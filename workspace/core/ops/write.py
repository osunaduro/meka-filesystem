"""Operacion de escritura de archivos.""""""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - write()

Purpose:
    Write text content to a file.
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops.write

Public API:
    write

Dependencies:
    pathlib
    sdk.internal.project
    sdk.internal.path

Thread Safe:
    yes

Pure:
    no
"""

from pathlib import Path

from workspace.internal.path import resolve as resolve_path


def write(
    root: Path,
    path: str | Path,
    content: str,
    *,
    encoding: str = "utf-8",
) -> None:
    """Write text content to a file.

    Parameters
    ----------
    project : str
        Project name.

    path : str | Path
        Relative path inside the project.

    content : str
        Text to write.

    encoding : str, optional
        Text encoding.
    """

    target = resolve_path(root, path)

    target.write_text(content, encoding=encoding)
