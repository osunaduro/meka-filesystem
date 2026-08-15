"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - read_many()

Purpose:
    Read several text files in a single call, continuing past individual
    failures instead of aborting the whole batch.
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops.read_many

Public API:
    read_many

Dependencies:
    pathlib
    workspace.core.models
    workspace.internal.path

Thread Safe:
    yes

Pure:
    no
"""

# ==========================================================================
# Imports
# ==========================================================================

from pathlib import Path

from workspace.core.models import ReadResult
from workspace.internal.path import resolve as resolve_path


# ==========================================================================
# Public API
# ==========================================================================

def read_many(
    root: Path,
    paths: list[str | Path],
    *,
    encoding: str = "utf-8",
) -> list[ReadResult]:
    """Read several text files, one result per requested path.

    Unlike calling ``read`` in a loop, a failure on one path (missing
    file, permission error, path outside the workspace, and so on) does
    not stop the batch: the corresponding result carries the error
    message instead, and every other path is still attempted.

    Parameters
    ----------
    root : Path
        Workspace root.

    paths : list[str | Path]
        Relative paths inside the workspace to read.

    encoding : str, optional
        Text encoding used for every file in the batch.

    Returns
    -------
    list[ReadResult]
        One result per requested path, in the same order. ``content`` is
        None when ``error`` is set, and vice versa.
    """

    results: list[ReadResult] = []

    for path in paths:
        target: Path | None = None
        try:
            target = resolve_path(root, path)
            content = target.read_text(encoding=encoding)
        except Exception as exc:
            reported_path = target if target is not None else Path(path)
            results.append(ReadResult(path=reported_path, content=None, error=str(exc)))
        else:
            results.append(ReadResult(path=target, content=content, error=None))

    return results
