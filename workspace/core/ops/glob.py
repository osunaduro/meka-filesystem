"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - glob()

Purpose:
    Find filesystem entries matching a glob pattern.
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops.glob

Public API:
    glob

Dependencies:
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

from pathlib import Path
from typing import Iterator

from workspace.internal.path import resolve as resolve_path


# ==========================================================================
# Public API
# ==========================================================================

def glob(
    root: Path,
    pattern: str,
    path: str | Path = ".",
) -> Iterator[Path]:
    """Find filesystem entries matching a glob pattern.

    Parameters
    ----------
    project : str
        Project name.

    pattern : str
        Glob pattern.

    root : str | Path, optional
        Directory where the search starts.

    Yields
    ------
    Path
        Matching filesystem entries.
    """

    # ----------------------------------------------------------------------
    # Resolve project context.
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Resolve search root.
    # ----------------------------------------------------------------------

    search_root = resolve_path(root, path)

    # ----------------------------------------------------------------------
    # Execute glob search.
    #
    # pathlib.Path.glob() implements the standard Python glob syntax.
    #
    # Results are yielded one by one instead of building a complete list,
    # allowing the caller to process large result sets efficiently.
    #
    # Examples:
    #
    # *.py
    # **/*.md
    # src/**/*.py
    # ----------------------------------------------------------------------

    yield from search_root.glob(pattern)
