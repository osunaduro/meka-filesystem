"""Operacion de copia de archivos o directorios."""

"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - copy()

Purpose:
    Copy a file or directory.
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops.copy

Public API:
    copy

Dependencies:
    pathlib
    shutil
    sdk.internal.project
    sdk.internal.path

Thread Safe:
    yes

Pure:
    no
"""

from pathlib import Path
import shutil

from workspace.internal.path import resolve as resolve_path


def copy(
    root: Path,
    source: str | Path,
    destination: str | Path,
) -> None:
    """Copy a file or directory.

    Parameters
    ----------
    project : str
        Project name.

    source : str | Path
        Source path inside the project.

    destination : str | Path
        Destination path inside the project.
    """

    src = resolve_path(root, source)
    dst = resolve_path(root, destination)

    if src.is_dir():
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)
