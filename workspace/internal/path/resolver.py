"""
MEKA Core SDK

Domain:
    Internal

Component:
    Path Resolver

Purpose:
    Resolve a path safely inside a project root.
"""

"""
MEKA Metadata

Domain:
    internal

Component:
    path.resolver

Public API:
    resolve

Dependencies:
    pathlib

Thread Safe:
    yes

Pure:
    yes
"""

from pathlib import Path

from workspace.core.errors import PathOutsideWorkspaceError


def resolve(root: Path, path: str | Path) -> Path:
    """Resolve a relative path safely inside a workspace root.

    Parameters
    ----------
    root : Path
        Workspace root directory.
    path : str | Path
        Relative path to resolve. Absolute paths are rejected.

    Returns
    -------
    Path
        Absolute resolved path.
    """
    requested_path = Path(path)
    if requested_path.is_absolute():
        raise PathOutsideWorkspaceError(
            f"Absolute paths are not allowed inside the workspace: {path}"
        )

    candidate = (root / requested_path).resolve()

    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise PathOutsideWorkspaceError(
            f"Path escapes project root: {path}"
        ) from exc

    return candidate
