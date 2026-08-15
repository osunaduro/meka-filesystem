"""Operacion de obtencion de metadatos de archivos o directorios."""

from datetime import datetime
from pathlib import Path

from workspace.core.models import FileInfo, FileType
from workspace.internal.path import resolve as resolve_path


def stat(
    root: Path,
    path: str | Path,
) -> FileInfo:
    """Return filesystem metadata."""

    target = resolve_path(root, path)

    info = target.stat()

    if target.is_symlink():
        file_type = FileType.SYMLINK
    elif target.is_file():
        file_type = FileType.FILE
    elif target.is_dir():
        file_type = FileType.DIRECTORY
    else:
        file_type = FileType.OTHER

    return FileInfo(
        path=target,
        type=file_type,
        size=info.st_size,
        modified_at=datetime.fromtimestamp(info.st_mtime),
    )
