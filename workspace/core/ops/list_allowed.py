"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - list_allowed()

Purpose:
    Report the workspace root(s) a caller is permitted to access.
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops.list_allowed

Public API:
    list_allowed

Dependencies:
    pathlib

Thread Safe:
    yes

Pure:
    yes
"""

# ==========================================================================
# Imports
# ==========================================================================

from pathlib import Path


# ==========================================================================
# Public API
# ==========================================================================

def list_allowed(root: Path) -> list[Path]:
    """Report the workspace root(s) a caller is permitted to access.

    The workspace currently supports a single configured root, so this
    always returns a one-element list. The list shape mirrors what a
    multi-root configuration would return, so callers do not need to
    special-case the single-root case.

    Parameters
    ----------
    root : Path
        Workspace root.

    Returns
    -------
    list[Path]
        The allowed root(s), currently always ``[root]``.
    """
    return [root]
