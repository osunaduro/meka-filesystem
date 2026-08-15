"""Operacion de lectura de las ultimas lineas de un archivo."""

"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - tail()

Purpose:
    Read the last lines of a text file.
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops.tail

Public API:
    tail

Dependencies:
    collections
    pathlib
    sdk.internal.project
    sdk.internal.path

Thread Safe:
    yes

Pure:
    no
"""

from collections import deque
from pathlib import Path

from workspace.internal.path import resolve as resolve_path


def tail(
    root: Path,
    path: str | Path,
    lines: int = 10,
    *,
    encoding: str = "utf-8",
) -> str:
    """Read the last lines of a text file.

    Parameters
    ----------
    project : str
        Project name.

    path : str | Path
        Relative path inside the project.

    lines : int, optional
        Number of lines to return.

    encoding : str, optional
        Text encoding.

    Returns
    -------
    str
        Last lines of the file.
    """

    # Resolve the project root directory.

    # Resolve the target file inside the project.
    target = resolve_path(root, path)

    # deque(maxlen=N) automatically keeps only the last N
    # elements while iterating over the file.
    #
    # This avoids loading the entire file into memory and
    # provides behavior equivalent to the Unix `tail` command.
    with target.open("r", encoding=encoding) as file:
        return "".join(
            deque(
                file,
                maxlen=lines,
            )
        )
