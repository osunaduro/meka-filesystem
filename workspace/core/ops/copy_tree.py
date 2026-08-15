"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - copy_tree()

Purpose:
    Copy a directory tree preserving its structure and contents.
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops.copy_tree

Public API:
    copy_tree

Dependencies:
    shutil
    pathlib
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

import shutil

from pathlib import Path

from workspace.internal.path import resolve as resolve_path


# ==========================================================================
# Public API
# ==========================================================================

def copy_tree(
    root: Path,
    source: str | Path,
    destination: str | Path,
) -> Path:
    """Copy a directory tree.

    Parameters
    ----------
    project : str
        Project name.

    source : str | Path
        Source directory.

    destination : str | Path
        Destination directory.

    Returns
    -------
    Path
        Absolute destination path.

    Notes
    -----
    The destination directory must not already exist.

    The operation copies the complete directory hierarchy,
    including all files and subdirectories.

    The implementation relies on ``shutil.copytree()``,
    the Python reference implementation for recursive
    directory copying.
    """

    # ----------------------------------------------------------------------
    # Resolve project context.
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Resolve source and destination paths.
    # ----------------------------------------------------------------------

    source_path = resolve_path(
        root,
        source,
    )

    destination_path = resolve_path(
        root,
        destination,
    )

    # ----------------------------------------------------------------------
    # Copy directory tree.
    #
    # shutil.copytree() recursively copies an entire directory,
    # preserving the directory structure and file metadata.
    # ----------------------------------------------------------------------

    shutil.copytree(
        source_path,
        destination_path,
    )

    return destination_path
