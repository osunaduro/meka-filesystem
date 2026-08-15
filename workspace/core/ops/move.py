"""Operacion de movimiento o renombrado de archivos o directorios."""

"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - move()

Purpose:
    Move or rename a file or directory.
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops.move

Public API:
    move

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


def move(
    root: Path,
    source: str | Path,
    destination: str | Path,
) -> None:
    """Move or rename a file or directory.

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

    shutil.move(src, dst)
