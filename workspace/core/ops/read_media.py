"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - read_media()

Purpose:
    Read a binary file (image, audio, or other non-text media) from the
    workspace, together with its guessed MIME type.
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops.read_media

Public API:
    read_media

Dependencies:
    mimetypes
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

import mimetypes
from pathlib import Path

from workspace.core.models import MediaFile
from workspace.internal.path import resolve as resolve_path

DEFAULT_MIME_TYPE = "application/octet-stream"


# ==========================================================================
# Public API
# ==========================================================================

def read_media(root: Path, path: str | Path) -> MediaFile:
    """Read a binary file's raw bytes and guess its MIME type.

    Parameters
    ----------
    root : Path
        Workspace root.

    path : str | Path
        Relative path inside the workspace.

    Returns
    -------
    MediaFile
        The file's raw bytes and a best-effort MIME type guessed from the
        file extension. Falls back to ``application/octet-stream`` when
        the type cannot be determined.
    """
    target = resolve_path(root, path)
    mime_type, _ = mimetypes.guess_type(target.name)
    return MediaFile(
        path=target,
        data=target.read_bytes(),
        mime_type=mime_type or DEFAULT_MIME_TYPE,
    )
