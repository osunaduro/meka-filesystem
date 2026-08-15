from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path


class FileType(Enum):
    """Filesystem resource type."""

    FILE = "file"
    DIRECTORY = "directory"
    SYMLINK = "symlink"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class FileInfo:
    """Filesystem metadata."""

    path: Path
    type: FileType
    size: int
    modified_at: datetime
    
@dataclass(frozen=True, slots=True)
class GrepMatch:
    """Text match returned by grep()."""

    path: Path
    line: int
    column: int
    text: str


@dataclass(frozen=True, slots=True)
class EditResult:
    """Outcome of a content-based text edit."""

    path: Path
    applied: bool
    occurrences: int
    diff: str


@dataclass(frozen=True, slots=True)
class ReadResult:
    """Outcome of reading one file as part of a batch read."""

    path: Path
    content: str | None
    error: str | None


@dataclass(frozen=True, slots=True)
class MediaFile:
    """Binary file content together with its guessed MIME type."""

    path: Path
    data: bytes
    mime_type: str
