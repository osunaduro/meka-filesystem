"""Operacion de eliminacion de archivos o directorios."""

"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - delete_file()

Purpose:
    Delete a file.
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops.delete_file

Public API:
    delete_file

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


def delete_file(
    root: Path,
    path: str | Path,
) -> None:
    """Delete a file.

    Parameters
    ----------
    project : str
        Project name.

    path : str | Path
        Relative path inside the project.
    """

    target = resolve_path(root, path)

    target.unlink()
