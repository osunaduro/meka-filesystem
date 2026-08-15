"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - read()

Purpose:
    Read text content from a file in the filesystem.
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops.read

Public API:
    read

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


def read(root: Path, path: str | Path, *, encoding: str = "utf-8") -> str:
    """Read text content from a file.

    Parameters
    ----------
    project : str
        Project name.
    path : str | Path
        Relative or absolute path inside the project.
    encoding : str, optional
        Text encoding used to read the file.

    Returns
    -------
    str
        File contents as text.
    """
    target = resolve_path(root, path)
    return target.read_text(encoding=encoding)
