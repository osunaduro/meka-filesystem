"""Operacion de lectura de rangos de bytes en archivos."""
"""Operacion de escritura de rangos de bytes en archivos."""

"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - read_range()

Purpose:
    Read a range of lines from a text file.
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops.read_range

Public API:
    read_range

Dependencies:
    itertools
    pathlib
    sdk.internal.project
    sdk.internal.path

Thread Safe:
    yes

Pure:
    no
"""

from itertools import islice
from pathlib import Path

from workspace.internal.path import resolve as resolve_path


def read_range(
    root: Path,
    path: str | Path,
    start: int,
    count: int,
    *,
    encoding: str = "utf-8",
) -> str:
    """Read a range of lines from a text file.

    Parameters
    ----------
    project : str
        Project name.

    path : str | Path
        Relative path inside the project.

    start : int
        First line to read (1-based).

    count : int
        Number of lines to read.

    encoding : str, optional
        Text encoding.

    Returns
    -------
    str
        Requested range of lines.
    """

    # Resolve the project root.
    # Resolve the target file inside the project.
    target = resolve_path(root, path)

    # islice() consumes only the requested portion of the file.
    #
    # Unlike read().splitlines(), this implementation does not load
    # the entire file into memory. The file is read sequentially until
    # the requested range is reached and only the selected lines are
    # returned.
    #
    # Example:
    #
    # start = 11
    # count = 5
    #
    # Returned lines:
    #
    # 11
    # 12
    # 13
    # 14
    # 15
    with target.open("r", encoding=encoding) as file:
        return "".join(
            islice(
                file,
                start - 1,
                start - 1 + count,
            )
        )
