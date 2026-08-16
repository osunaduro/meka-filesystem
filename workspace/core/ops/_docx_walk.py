"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - iter_block_items()

Purpose:
    Walk a DOCX document's body yielding paragraphs and tables in their
    real document order, shared by read_docx() and edit_docx().
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops._docx_walk

Public API:
    iter_block_items

Dependencies:
    docx
    typing

Thread Safe:
    yes

Pure:
    no
"""

# ==========================================================================
# Imports
# ==========================================================================

from typing import Iterator, Union

from docx import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph


# ==========================================================================
# Public API
# ==========================================================================

def iter_block_items(document: Document) -> Iterator[Union[Paragraph, Table]]:
    """Yield paragraphs and tables in the order they appear in the body.

    python-docx exposes ``document.paragraphs`` and ``document.tables``
    as two separate, unordered-relative-to-each-other lists. Walking the
    body's XML children directly is the standard way to recover their
    real document order.
    """
    for child in document.element.body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, document)
        elif isinstance(child, CT_Tbl):
            yield Table(child, document)
