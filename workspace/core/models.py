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


@dataclass(frozen=True, slots=True)
class PdfPage:
    """Extracted text for a single PDF page."""

    number: int
    text: str
    used_ocr: bool


@dataclass(frozen=True, slots=True)
class PdfTextResult:
    """Outcome of extracting text from a PDF, page by page."""

    path: Path
    pages: list[PdfPage]


@dataclass(frozen=True, slots=True)
class ExcelSheetResult:
    """A rectangular range of cell values read from one Excel sheet."""

    path: Path
    sheet_name: str
    sheet_names: list[str]
    data: list[list[object]]
    total_rows: int
    total_cols: int


@dataclass(frozen=True, slots=True)
class DocxParagraph:
    """A single paragraph in a DOCX outline."""

    index: int
    style: str
    text: str


@dataclass(frozen=True, slots=True)
class DocxTable:
    """A single table in a DOCX outline."""

    index: int
    rows: list[list[str]]


@dataclass(frozen=True, slots=True)
class DocxOutlineResult:
    """Outcome of reading a DOCX file as a structured outline."""

    path: Path
    paragraphs: list[DocxParagraph]
    tables: list[DocxTable]
