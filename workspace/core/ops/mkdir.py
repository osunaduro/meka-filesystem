"""Operacion de creacion de directorios."""

"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - mkdir()

Purpose:
    Create a directory.
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops.mkdir

Public API:
    mkdir

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


def mkdir(
    root: Path,
    path: str | Path,
    *,
    parents: bool = False,
    exist_ok: bool = False,
) -> None:
    """Create a directory.

    Parameters
    ----------
    project : str
        Project name.

    path : str | Path
        Relative path inside the project.

    parents : bool, optional
        Create parent directories if needed.

    exist_ok : bool, optional
        Do not raise an exception if the directory already exists.
    """

    target = resolve_path(root, path)

    target.mkdir(
        parents=parents,
        exist_ok=exist_ok,
    )
