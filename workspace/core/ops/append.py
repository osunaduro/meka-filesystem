"""Operacion de agregado al final de archivos."""

"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - append()

Purpose:
    Append text to a file.
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops.append

Public API:
    append

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


def append(
    root: Path,
    path: str | Path,
    content: str,
    *,
    encoding: str = "utf-8",
) -> None:
    """Append text to a file.

    Parameters
    ----------
    project : str
        Project name.

    path : str | Path
        Relative path inside the project.

    content : str
        Text to append.

    encoding : str, optional
        Text encoding.
    """

    target = resolve_path(root, path)

    with target.open(
        mode="a",
        encoding=encoding,
    ) as file:
        file.write(content)
