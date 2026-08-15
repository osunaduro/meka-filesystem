"""Operacion de listado de contenidos de directorios."""

"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - list()

Purpose:
    List directory contents.
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops.list

Public API:
    list

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

from workspace.core.models import FileInfo
from workspace.core.ops.stat import stat
from workspace.internal.path import resolve as resolve_path


def list(
    root: Path,
    path: str | Path = ".",
) -> list[FileInfo]:
    """List directory contents."""

    target = resolve_path(root, path)

    return [
        stat(
            root,
            entry.relative_to(root),
        )
        for entry in target.iterdir()
    ]
