"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - rmdir()

Purpose:
    Remove an empty directory.
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops.rmdir

Public API:
    rmdir

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


def rmdir(
    root: Path,
    path: str | Path,
) -> None:
    """Remove an empty directory.

    Parameters
    ----------
    project : str
        Project name.

    path : str | Path
        Relative path inside the project.
    """

    target = resolve_path(root, path)

    target.rmdir()
