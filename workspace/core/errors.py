"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Exception Hierarchy

Purpose:
    Define the public exception contract for the Filesystem domain.
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    errors

Public API:
    FilesystemError
    PathError
    InvalidPathError
    PathNotFoundError
    PathAlreadyExistsError
    PathOutsideWorkspaceError
    FileError
    NotAFileError
    FileTooLargeError
    FileEncodingError
    EditError
    NoMatchError
    AmbiguousMatchError
    WorkbookError
    SheetNotFoundError
    DirectoryError
    NotADirectoryError
    DirectoryNotFoundError
    DirectoryNotEmptyError
    PermissionDeniedError
    BackendError
    BackendUnavailableError
    WatchBackendUnavailableError
    SearchBackendUnavailableError
    OcrBackendUnavailableError
    OperationCancelledError

Dependencies:
    (none)

Thread Safe:
    yes

Pure Function:
    yes
"""


class FilesystemError(Exception):
    """Base exception for all filesystem domain errors."""
    pass


class PathError(FilesystemError):
    """Base exception for path-related errors."""
    pass


class InvalidPathError(PathError):
    """The path format is invalid or malformed."""
    pass


class PathNotFoundError(PathError):
    """The specified path does not exist."""
    pass


class PathAlreadyExistsError(PathError):
    """The path already exists when it should not."""
    pass


class PathOutsideWorkspaceError(PathError):
    """The path is outside the allowed workspace boundary."""
    pass


class FileError(FilesystemError):
    """Base exception for file-related errors."""
    pass


class NotAFileError(FileError):
    """The path exists but is not a regular file."""
    pass


class FileTooLargeError(FileError):
    """The file exceeds the maximum allowed size."""
    pass


class FileEncodingError(FileError):
    """The file encoding is not supported or cannot be decoded."""
    pass


class DirectoryError(FilesystemError):
    """Base exception for directory-related errors."""
    pass


class NotADirectoryError(DirectoryError):
    """The path exists but is not a directory."""
    pass


class DirectoryNotFoundError(DirectoryError):
    """The specified directory does not exist."""
    pass


class DirectoryNotEmptyError(DirectoryError):
    """The directory is not empty when it should be."""
    pass


class PermissionDeniedError(FilesystemError):
    """The operation was denied due to insufficient permissions."""
    pass


class BackendError(FilesystemError):
    """Base exception for filesystem backend errors."""
    pass


class BackendUnavailableError(BackendError):
    """The filesystem backend is not available."""
    pass


class WatchBackendUnavailableError(BackendError):
    """The filesystem watch backend is not available."""
    pass


class SearchBackendUnavailableError(BackendError):
    """The filesystem search backend is not available."""
    pass


class OcrBackendUnavailableError(BackendError):
    """The OCR backend (Tesseract) is not installed or not on PATH."""
    pass


class OperationCancelledError(FilesystemError):
    """The operation was cancelled before completion."""
    pass


class EditError(FileError):
    """Base exception for content-based text edit errors."""
    pass


class NoMatchError(EditError):
    """The requested search text was not found in the file.

    When a near-miss is found (via fuzzy matching), it is attached as
    ``closest_match``/``similarity`` so callers can surface a helpful diff
    instead of a bare "not found".
    """

    def __init__(self, message: str, *, closest_match: str | None = None, similarity: float | None = None) -> None:
        super().__init__(message)
        self.closest_match = closest_match
        self.similarity = similarity

    def __str__(self) -> str:
        base = super().__str__()
        if not self.closest_match:
            return base
        return (
            f"{base} Closest match found ({self.similarity:.0%} similar): "
            f"{self.closest_match!r}"
        )


class AmbiguousMatchError(EditError):
    """The requested search text matched a different number of times than expected."""
    pass


class WorkbookError(FileError):
    """Base exception for Excel workbook errors."""
    pass


class SheetNotFoundError(WorkbookError):
    """The requested sheet does not exist in the workbook."""
    pass
