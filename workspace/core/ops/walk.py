"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - walk()

Purpose:
    Recursively traverse a directory tree.
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops.walk

Public API:
    walk

Dependencies:
    os
    pathlib
    typing
    sdk.internal.project
    sdk.internal.path

Thread Safe:
    yes

Pure:
    no
"""

# ==========================================================================
# Imports
# ==========================================================================

import os

from pathlib import Path
from typing import Iterator

from workspace.internal.path import resolve as resolve_path


# ==========================================================================
# Public API
# ==========================================================================

def walk(
    root: Path,
    path: str | Path = ".",
) -> Iterator[Path]:
    """Recursively traverse a directory tree.

    Parameters
    ----------
    project : str
        Project name.

    path : str | Path, optional
        Root directory where the traversal begins.

    Yields
    ------
    Path
        Files and directories discovered during traversal.
    """

    # ----------------------------------------------------------------------
    # Resolve project context.
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Resolve traversal root.
    # ----------------------------------------------------------------------

    root = resolve_path(root, path)

    # ----------------------------------------------------------------------
    # Traverse the directory tree.
    #
    # os.walk() is the reference implementation provided by the Python
    # standard library for recursive directory traversal.
    #
    # Results are yielded one by one as pathlib.Path objects instead of
    # building a complete list in memory. This allows the caller to stop
    # iteration early and makes the operation scalable to very large
    # directory trees.
    # ----------------------------------------------------------------------

    for current_root, directories, files in os.walk(root):

        current = Path(current_root)

        # Yield directories.
        for directory in directories:
            yield current / directory

        # Yield files.
        for file in files:
            yield current / file
