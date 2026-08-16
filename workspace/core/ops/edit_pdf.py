"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - edit_pdf()

Purpose:
    Insert or delete pages in an existing PDF, applying a sequence of
    operations atomically.
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops.edit_pdf

Public API:
    edit_pdf
    PdfInsertOperation
    PdfDeleteOperation

Dependencies:
    dataclasses
    pymupdf
    pathlib
    workspace.internal.path

Thread Safe:
    yes

Pure:
    no
"""

# ==========================================================================
# Imports
# ==========================================================================

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

import pymupdf

from workspace.internal.path import resolve as resolve_path


# ==========================================================================
# Input types
# ==========================================================================

@dataclass(frozen=True, slots=True)
class PdfInsertOperation:
    """Insert every page of another workspace PDF at a 1-based position."""

    at: int
    source: str


@dataclass(frozen=True, slots=True)
class PdfDeleteOperation:
    """Delete a set of 1-based page numbers."""

    pages: list[int]


PdfPageOperation = PdfInsertOperation | PdfDeleteOperation


# ==========================================================================
# Public API
# ==========================================================================

def edit_pdf(root: Path, path: str | Path, operations: list[PdfPageOperation]) -> None:
    """Insert or delete pages in an existing PDF, applied atomically in order.

    Parameters
    ----------
    root : Path
        Workspace root.

    path : str | Path
        Relative path inside the workspace to the PDF being edited.

    operations : list[PdfPageOperation]
        Operations to apply in order. Page numbers throughout are 1-based,
        consistent with ``read_pdf_text``'s ``PdfPage.number``.

        - ``PdfInsertOperation(at, source)`` inserts every page of the
          workspace PDF at ``source`` immediately before page ``at``
          (``at`` may equal the page count + 1 to append at the end).
        - ``PdfDeleteOperation(pages)`` deletes the given 1-based page
          numbers.

    Raises
    ------
    ValueError
        ``operations`` is empty, or any page number/index is out of range
        for the document at the point the operation is applied.

    Notes
    -----
    Operations are applied to an in-memory copy of the document; the file
    on disk is only overwritten after every operation succeeds, so a
    failure partway through leaves the original file untouched.
    """
    if not operations:
        raise ValueError("'operations' must contain at least one operation.")

    target = resolve_path(root, path)

    with pymupdf.open(target) as document:
        for operation in operations:
            if isinstance(operation, PdfInsertOperation):
                _apply_insert(document, root, operation)
            elif isinstance(operation, PdfDeleteOperation):
                _apply_delete(document, operation)
            else:
                raise ValueError(f"Unsupported PDF page operation: {operation!r}")

        # PyMuPDF refuses to overwrite the file it was opened from unless
        # saving incrementally, which doesn't support every edit made here.
        # Save to a sibling temp file and swap it in atomically instead.
        fd, tmp_name = tempfile.mkstemp(dir=target.parent, suffix=".pdf")
        os.close(fd)
        try:
            document.save(tmp_name, incremental=False)
            os.replace(tmp_name, target)
        except BaseException:
            os.unlink(tmp_name)
            raise


# ==========================================================================
# Internal helpers
# ==========================================================================

def _apply_insert(document: pymupdf.Document, root: Path, operation: PdfInsertOperation) -> None:
    page_count = document.page_count

    if not 1 <= operation.at <= page_count + 1:
        raise ValueError(
            f"Insert position {operation.at} is out of range for a document with {page_count} page(s)."
        )

    source_path = resolve_path(root, operation.source)
    with pymupdf.open(source_path) as source_document:
        document.insert_pdf(source_document, start_at=operation.at - 1)


def _apply_delete(document: pymupdf.Document, operation: PdfDeleteOperation) -> None:
    page_count = document.page_count

    if not operation.pages:
        raise ValueError("'pages' must contain at least one page number.")

    for page_number in operation.pages:
        if not 1 <= page_number <= page_count:
            raise ValueError(
                f"Page {page_number} is out of range for a document with {page_count} page(s)."
            )

    zero_based = sorted({page_number - 1 for page_number in operation.pages})
    document.delete_pages(zero_based)
