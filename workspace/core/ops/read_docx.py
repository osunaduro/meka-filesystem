"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - read_docx()

Purpose:
    Read a DOCX file as a structured outline of paragraphs and tables, in
    document order.
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops.read_docx

Public API:
    read_docx

Dependencies:
    docx
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

from docx import Document
from docx.table import Table

from workspace.core.models import DocxOutlineResult
from workspace.core.models import DocxParagraph as DocxParagraphModel
from workspace.core.models import DocxTable as DocxTableModel
from workspace.core.ops._docx_walk import iter_block_items
from workspace.internal.path import resolve as resolve_path


# ==========================================================================
# Internal helpers
# ==========================================================================

def _table_rows(table: Table) -> list[list[str]]:
    return [[cell.text for cell in row.cells] for row in table.rows]


# ==========================================================================
# Public API
# ==========================================================================

def read_docx(root: Path, path: str | Path) -> DocxOutlineResult:
    """Read a DOCX file as a structured outline, in document order.

    Parameters
    ----------
    root : Path
        Workspace root.

    path : str | Path
        Relative path inside the workspace to a .docx file.

    Returns
    -------
    DocxOutlineResult
        ``paragraphs`` and ``tables`` each carry their 0-based index in
        the document's body, so a caller can tell where a table falls
        relative to the surrounding paragraphs.
    """
    target = resolve_path(root, path)
    document = Document(target)

    paragraphs: list[DocxParagraphModel] = []
    tables: list[DocxTableModel] = []

    for index, item in enumerate(iter_block_items(document)):
        if isinstance(item, Table):
            tables.append(DocxTableModel(index=index, rows=_table_rows(item)))
        else:
            paragraphs.append(
                DocxParagraphModel(index=index, style=item.style.name if item.style else "", text=item.text)
            )

    return DocxOutlineResult(path=target, paragraphs=paragraphs, tables=tables)
