"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - exists()

Purpose:
    Check whether a path exists in the filesystem.
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops.exists

Public API:
    exists

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


def exists(root: Path, path: str | Path) -> bool:
    """Check whether a path exists in the filesystem.

    Parameters
    ----------
    project : str
        Project name.
    path : str | Path
        Relative or absolute path inside the project.

    Returns
    -------
    bool
        True if the path exists, False otherwise.
    """
    target = resolve_path(root, path)
    return target.exists()
