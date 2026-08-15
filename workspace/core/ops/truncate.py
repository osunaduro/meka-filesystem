"""Operacion de truncamiento de archivos."""

"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - truncate()

Purpose:
    Truncate a file.
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops.truncate

Public API:
    truncate

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


def truncate(
    root: Path,
    path: str | Path,
    size: int = 0,
) -> None:
    """Truncate a file.

    Parameters
    ----------
    project : str
        Project name.

    path : str | Path
        Relative path inside the project.

    size : int, optional
        New file size in bytes. Defaults to 0.
    """

    target = resolve_path(root, path)

    with target.open("r+b") as file:
        file.truncate(size)
