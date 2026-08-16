"""Shared MCP tool definitions for the filesystem domain.

This module is the single source of truth for the MCP tools exposed by the
HTTP and STDIO transport adapters. Transport concerns (authentication, routing,
scope enforcement) are injected by the calling server, never defined here.
"""

import base64
from itertools import islice
from pathlib import Path
from typing import Callable, Iterable, Iterator

from fastmcp import FastMCP

from workspace.core.models import DocxOutlineResult, EditResult, ExcelSheetResult, FileInfo, GrepMatch, MediaFile
from workspace.core.models import PdfTextResult, ReadResult
from workspace.core.ops import PdfDeleteOperation, PdfInsertOperation, TextEdit, append, copy, copy_tree
from workspace.core.ops import delete_file, edit_docx, edit_pdf, edit_text, edit_text_many
from workspace.core.ops import exists, glob, head
from workspace.core.ops import list as list_directory_op
from workspace.core.ops import list_allowed, mkdir, move, ocr_image, read, read_docx, read_excel, read_many, read_media
from workspace.core.ops import read_pdf_text, read_range
from workspace.core.ops import replace_lines, rmdir, stat, tail
from workspace.core.ops import truncate, walk, write, write_docx, write_excel, write_media, write_pdf
from workspace.core.ops.grep import grep
from workspace.internal.config import WORKSPACE_ROOT

MAX_RESULTS = 1_000
READ_SCOPE = "filesystem:read"
WRITE_SCOPE = "filesystem:write"
DELETE_SCOPE = "filesystem:delete"
SUPPORTED_SCOPES = [READ_SCOPE, WRITE_SCOPE, DELETE_SCOPE]

INSTRUCTIONS = (
    "Manage files below the configured workspace root. Every supplied path is relative "
    "to that root; paths cannot access the server filesystem outside it."
)


def _root() -> Path:
    root = WORKSPACE_ROOT.resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"Workspace root does not exist: {root}")
    return root


def _relative(path: Path) -> str:
    return str(path.resolve().relative_to(_root())) or "."


def _file_info(info: FileInfo) -> dict[str, object]:
    return {
        "path": _relative(info.path),
        "type": info.type.value,
        "size": info.size,
        "modified_at": info.modified_at.isoformat(),
    }


def _edit_result(result: EditResult) -> dict[str, object]:
    return {
        "path": _relative(result.path),
        "applied": result.applied,
        "occurrences": result.occurrences,
        "diff": result.diff,
    }


def _read_result(result: ReadResult) -> dict[str, object]:
    return {
        "path": str(result.path),
        "content": result.content,
        "error": result.error,
    }


def _media_file(media: MediaFile) -> dict[str, object]:
    return {
        "path": _relative(media.path),
        "mime_type": media.mime_type,
        "data_base64": base64.b64encode(media.data).decode("ascii"),
    }


def _pdf_text_result(result: PdfTextResult) -> dict[str, object]:
    return {
        "path": _relative(result.path),
        "pages": [
            {"number": page.number, "text": page.text, "used_ocr": page.used_ocr}
            for page in result.pages
        ],
    }


def _excel_sheet_result(result: ExcelSheetResult) -> dict[str, object]:
    return {
        "path": _relative(result.path),
        "sheet_name": result.sheet_name,
        "sheet_names": result.sheet_names,
        "data": result.data,
        "total_rows": result.total_rows,
        "total_cols": result.total_cols,
    }


def _docx_outline_result(result: DocxOutlineResult) -> dict[str, object]:
    return {
        "path": _relative(result.path),
        "paragraphs": [
            {"index": p.index, "style": p.style, "text": p.text} for p in result.paragraphs
        ],
        "tables": [{"index": t.index, "rows": t.rows} for t in result.tables],
    }


def _paths(paths: Iterable[Path], limit: int) -> dict[str, object]:
    if not 1 <= limit <= MAX_RESULTS:
        raise ValueError(f"limit must be between 1 and {MAX_RESULTS}.")
    iterator: Iterator[Path] = iter(paths)
    items = list(islice(iterator, limit))
    return {"paths": [_relative(path) for path in items], "truncated": next(iterator, None) is not None}


def _matches(matches: Iterable[GrepMatch], limit: int) -> dict[str, object]:
    if not 1 <= limit <= MAX_RESULTS:
        raise ValueError(f"limit must be between 1 and {MAX_RESULTS}.")
    iterator: Iterator[GrepMatch] = iter(matches)
    items = list(islice(iterator, limit))
    return {
        "matches": [
            {"path": _relative(match.path), "line": match.line, "column": match.column, "text": match.text}
            for match in items
        ],
        "truncated": next(iterator, None) is not None,
    }


def register_tools(mcp: FastMCP, *, scope_guard: Callable[[str], Callable] | None = None) -> None:
    """Register every filesystem tool on ``mcp``.

    ``scope_guard`` is an optional factory that receives a scope name and
    returns a decorator that enforces it. It is supplied only by the HTTP
    transport in OIDC mode; STDIO and api-key modes pass ``None``.
    """

    def scoped(scope: str):
        if scope_guard is None:
            return lambda function: function
        return scope_guard(scope)

    @mcp.tool
    @scoped(READ_SCOPE)
    def path_exists(path: str) -> bool:
        """Check whether a workspace-relative path exists."""
        return exists(_root(), path)

    @mcp.tool
    @scoped(READ_SCOPE)
    def read_file(path: str, encoding: str = "utf-8") -> str:
        """Read a complete text file from the workspace."""
        return read(_root(), path, encoding=encoding)

    @mcp.tool
    @scoped(READ_SCOPE)
    def read_files(paths: list[str], encoding: str = "utf-8") -> list[dict[str, object]]:
        """Read several text files in one call. A failure on one path does not stop the others; check each result's 'error' field."""
        return [_read_result(result) for result in read_many(_root(), paths, encoding=encoding)]

    @mcp.tool
    @scoped(READ_SCOPE)
    def read_media_file(path: str) -> dict[str, object]:
        """Read a binary file (image, audio, etc.) as base64 with a guessed MIME type."""
        return _media_file(read_media(_root(), path))

    @mcp.tool
    @scoped(WRITE_SCOPE)
    def write_media_file(path: str, data_base64: str) -> dict[str, bool]:
        """Write a binary file (image, audio, etc.) from base64-encoded data."""
        write_media(_root(), path, base64.b64decode(data_base64))
        return {"written": True}

    @mcp.tool
    @scoped(READ_SCOPE)
    def read_file_range(path: str, start: int, count: int, encoding: str = "utf-8") -> str:
        """Read a 1-based range of text lines without loading the whole file."""
        return read_range(_root(), path, start, count, encoding=encoding)

    @mcp.tool
    @scoped(READ_SCOPE)
    def read_file_head(path: str, lines: int = 10, encoding: str = "utf-8") -> str:
        """Read the first text lines of a workspace file."""
        return head(_root(), path, lines, encoding=encoding)

    @mcp.tool
    @scoped(READ_SCOPE)
    def read_file_tail(path: str, lines: int = 10, encoding: str = "utf-8") -> str:
        """Read the final text lines of a workspace file."""
        return tail(_root(), path, lines, encoding=encoding)

    @mcp.tool
    @scoped(WRITE_SCOPE)
    def write_file(path: str, content: str, encoding: str = "utf-8") -> dict[str, bool]:
        """Create or replace a text file inside the workspace."""
        write(_root(), path, content, encoding=encoding)
        return {"written": True}

    @mcp.tool
    @scoped(WRITE_SCOPE)
    def append_file(path: str, content: str, encoding: str = "utf-8") -> dict[str, bool]:
        """Append text to a workspace file."""
        append(_root(), path, content, encoding=encoding)
        return {"appended": True}

    @mcp.tool
    @scoped(WRITE_SCOPE)
    def replace_file_lines(path: str, start: int, count: int, content: str, encoding: str = "utf-8") -> dict[str, bool]:
        """Replace, insert, or remove a 1-based range of text lines."""
        replace_lines(_root(), path, start, count, content, encoding=encoding)
        return {"replaced": True}

    @mcp.tool
    @scoped(WRITE_SCOPE)
    def edit_file_text(
        path: str,
        old_text: str,
        new_text: str,
        expected_occurrences: int = 1,
        dry_run: bool = False,
        encoding: str = "utf-8",
    ) -> dict[str, object]:
        """Replace text matched by exact content, with an optional dry-run diff preview.

        Unlike replace_file_lines, the match is anchored to the file content
        (old_text) rather than to a line number, so it stays correct even if
        the file changed since it was last read. Set dry_run=True to preview
        the unified diff without writing to disk. Raises an error if old_text
        is not found, or if it matches a different number of times than
        expected_occurrences.
        """
        result = edit_text(
            _root(),
            path,
            old_text,
            new_text,
            expected_occurrences=expected_occurrences,
            dry_run=dry_run,
            encoding=encoding,
        )
        return _edit_result(result)

    @mcp.tool
    @scoped(WRITE_SCOPE)
    def edit_file_text_many(
        path: str,
        edits: list[dict[str, object]],
        dry_run: bool = False,
        encoding: str = "utf-8",
    ) -> dict[str, object]:
        """Apply several content-based edits to one file atomically (all or nothing).

        Each item in 'edits' is an object with 'old_text', 'new_text', and
        an optional 'expected_occurrences' (default 1). Edits are applied
        in order, each matched against the content as it stands after the
        previous edits. If any edit fails to match, nothing in the batch
        is written to disk. Set dry_run=True to preview the combined diff
        without writing.
        """
        parsed_edits = [
            TextEdit(
                old_text=edit["old_text"],
                new_text=edit["new_text"],
                expected_occurrences=int(edit.get("expected_occurrences", 1)),
            )
            for edit in edits
        ]
        result = edit_text_many(_root(), path, parsed_edits, dry_run=dry_run, encoding=encoding)
        return _edit_result(result)

    @mcp.tool
    @scoped(WRITE_SCOPE)
    def truncate_file(path: str, size: int = 0) -> dict[str, bool]:
        """Set a workspace file's size in bytes."""
        truncate(_root(), path, size)
        return {"truncated": True}

    @mcp.tool
    @scoped(WRITE_SCOPE)
    def create_directory(path: str, parents: bool = False, exist_ok: bool = False) -> dict[str, bool]:
        """Create a directory inside the workspace."""
        mkdir(_root(), path, parents=parents, exist_ok=exist_ok)
        return {"created": True}

    @mcp.tool
    @scoped(DELETE_SCOPE)
    def remove_directory(path: str) -> dict[str, bool]:
        """Remove an empty workspace directory."""
        rmdir(_root(), path)
        return {"deleted": True}

    @mcp.tool
    @scoped(DELETE_SCOPE)
    def delete_file_path(path: str) -> dict[str, bool]:
        """Delete a regular file or symlink from the workspace."""
        delete_file(_root(), path)
        return {"deleted": True}

    @mcp.tool
    @scoped(WRITE_SCOPE)
    def copy_path(source: str, destination: str) -> dict[str, bool]:
        """Copy a file or directory inside the workspace."""
        copy(_root(), source, destination)
        return {"copied": True}

    @mcp.tool
    @scoped(WRITE_SCOPE)
    def copy_directory_tree(source: str, destination: str) -> dict[str, str]:
        """Recursively copy a directory to a new workspace destination."""
        return {"path": _relative(copy_tree(_root(), source, destination))}

    @mcp.tool
    @scoped(WRITE_SCOPE)
    def move_path(source: str, destination: str) -> dict[str, bool]:
        """Move or rename a file or directory inside the workspace."""
        move(_root(), source, destination)
        return {"moved": True}

    @mcp.tool
    @scoped(READ_SCOPE)
    def stat_path(path: str) -> dict[str, object]:
        """Return metadata for a workspace path."""
        return _file_info(stat(_root(), path))

    @mcp.tool
    @scoped(READ_SCOPE)
    def list_directory(path: str = ".") -> list[dict[str, object]]:
        """List direct children of a workspace directory."""
        return [_file_info(info) for info in list_directory_op(_root(), path)]

    @mcp.tool
    @scoped(READ_SCOPE)
    def list_allowed_directories() -> list[str]:
        """List the workspace root(s) this server is allowed to access."""
        return [_relative(path) for path in list_allowed(_root())]

    @mcp.tool
    @scoped(READ_SCOPE)
    def walk_paths(path: str = ".", limit: int = 200) -> dict[str, object]:
        """Recursively list workspace paths up to a bounded result count."""
        return _paths(walk(_root(), path), limit)

    @mcp.tool
    @scoped(READ_SCOPE)
    def glob_paths(pattern: str, path: str = ".", limit: int = 200) -> dict[str, object]:
        """Find workspace paths matching a glob pattern."""
        return _paths(glob(_root(), pattern, path), limit)

    @mcp.tool
    @scoped(READ_SCOPE)
    def grep_text(pattern: str, path: str = ".", limit: int = 200) -> dict[str, object]:
        """Search text with ripgrep inside the workspace."""
        return _matches(grep(_root(), pattern, path), limit)

    @mcp.tool
    @scoped(READ_SCOPE)
    def ocr_image_file(path: str, language: str = "eng+spa") -> str:
        """Extract text from an image file (PNG, JPEG, etc.) using OCR."""
        return ocr_image(_root(), path, language=language)

    @mcp.tool
    @scoped(READ_SCOPE)
    def read_pdf_text_file(path: str, ocr_fallback: bool = True, language: str = "eng+spa") -> dict[str, object]:
        """Extract text from a PDF, page by page.

        Pages with an embedded text layer are read directly. When
        ocr_fallback is True (default), pages with no text layer (scanned
        or image-only pages) are rendered and passed through OCR instead;
        check each page's 'used_ocr' field to see which path was taken.
        """
        return _pdf_text_result(read_pdf_text(_root(), path, ocr_fallback=ocr_fallback, language=language))

    @mcp.tool
    @scoped(WRITE_SCOPE)
    def create_pdf(path: str, markdown: str) -> dict[str, bool]:
        """Create or replace a PDF file rendered from Markdown-formatted text.

        Lightweight renderer, not full Markdown: supports headings (#, ##,
        ###), bullet lists (- or *), bold (**text**), italic (*text*), and
        plain paragraphs. Tables, links, images, and code blocks are not
        supported.
        """
        write_pdf(_root(), path, markdown)
        return {"created": True}

    @mcp.tool
    @scoped(WRITE_SCOPE)
    def edit_pdf_pages(path: str, operations: list[dict[str, object]]) -> dict[str, bool]:
        """Insert or delete pages in an existing PDF, applied atomically in order.

        Each operation is either:
        {"type": "insert", "at": <1-based page number>, "source": "<workspace-relative path to another PDF>"}
        {"type": "delete", "pages": [<1-based page numbers>]}

        Page numbers are 1-based, matching read_pdf_text_file. To insert new
        content rendered from Markdown, first create it as a standalone PDF
        with create_pdf, then insert its pages here. If any operation fails,
        nothing is written and the original file is left untouched.
        """
        parsed_operations: list[PdfInsertOperation | PdfDeleteOperation] = []
        for operation in operations:
            op_type = operation.get("type")
            if op_type == "insert":
                parsed_operations.append(
                    PdfInsertOperation(at=int(operation["at"]), source=str(operation["source"]))
                )
            elif op_type == "delete":
                parsed_operations.append(
                    PdfDeleteOperation(pages=[int(page) for page in operation["pages"]])
                )
            else:
                raise ValueError(f"Unsupported PDF page operation type: {op_type!r}")

        edit_pdf(_root(), path, parsed_operations)
        return {"edited": True}

    # ------------------------------------------------------------------
    # Excel
    # ------------------------------------------------------------------

    @mcp.tool
    @scoped(READ_SCOPE)
    def read_excel_file(path: str, sheet: str | None = None, cell_range: str | None = None) -> dict[str, object]:
        """Read an Excel sheet (.xlsx) as a 2D array of cell values.

        If 'sheet' is omitted, reads the workbook's active sheet.
        'cell_range' (e.g. "A1:D100") limits the read to that range; omit
        to read the sheet's whole used range. The result also lists every
        sheet name in the workbook, for discovery.
        """
        return _excel_sheet_result(read_excel(_root(), path, sheet=sheet, cell_range=cell_range))

    @mcp.tool
    @scoped(WRITE_SCOPE)
    def write_excel_file(
        path: str, data: list[list[object]], sheet: str = "Sheet1", start_cell: str = "A1"
    ) -> dict[str, bool]:
        """Write a 2D array of values into an Excel sheet, starting at start_cell.

        Creates the workbook if it does not exist. If it does, only the
        target sheet is replaced or created — every other sheet already in
        the workbook is preserved untouched.
        """
        write_excel(_root(), path, data, sheet=sheet, start_cell=start_cell)
        return {"written": True}

    # ------------------------------------------------------------------
    # DOCX
    # ------------------------------------------------------------------

    @mcp.tool
    @scoped(READ_SCOPE)
    def read_docx_outline(path: str) -> dict[str, object]:
        """Read a .docx file as a structured outline: paragraphs (with style
        name) and tables (as rows of cell text), in document order.
        """
        return _docx_outline_result(read_docx(_root(), path))

    @mcp.tool
    @scoped(WRITE_SCOPE)
    def create_docx(path: str, markdown: str) -> dict[str, bool]:
        """Create or replace a .docx file rendered from Markdown-formatted text.

        Same lightweight subset as create_pdf: headings, bullet lists, bold,
        italic. Tables, links, images, and code blocks are not supported.
        """
        write_docx(_root(), path, markdown)
        return {"created": True}

    @mcp.tool
    @scoped(WRITE_SCOPE)
    def edit_docx_text(
        path: str, old_text: str, new_text: str, expected_occurrences: int = 1, dry_run: bool = False
    ) -> dict[str, object]:
        """Replace text matched by content within a .docx (searches each
        paragraph and table cell; old_text must fall within a single
        paragraph, it cannot span two).

        When a match is found, the whole containing paragraph is rewritten
        as a single run — this can flatten run-level formatting (e.g. a
        single bolded word) within that specific paragraph. Set
        dry_run=True to preview the diff without writing.
        """
        result = edit_docx(
            _root(), path, old_text, new_text, expected_occurrences=expected_occurrences, dry_run=dry_run
        )
        return _edit_result(result)
