"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - write_pdf()

Purpose:
    Create or replace a PDF file rendered from Markdown-formatted text.
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops.write_pdf

Public API:
    write_pdf

Dependencies:
    reportlab
    pathlib
    workspace.core.ops._markdown_lite
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

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Flowable, ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer

from workspace.core.ops._markdown_lite import Blank, BulletItem, Heading, parse_blocks, parse_inline
from workspace.internal.path import resolve as resolve_path

_HEADING_STYLE = {1: "Heading1", 2: "Heading2", 3: "Heading3"}


def _reportlab_markup(text: str) -> str:
    """Render inline bold/italic runs as ReportLab's `<b>`/`<i>` tags."""
    rendered = ""
    for run in parse_inline(text):
        piece = run.text
        if run.bold:
            piece = f"<b>{piece}</b>"
        if run.italic:
            piece = f"<i>{piece}</i>"
        rendered += piece
    return rendered


# ==========================================================================
# Public API
# ==========================================================================

def write_pdf(root: Path, path: str | Path, markdown: str) -> None:
    """Create or replace a PDF file rendered from Markdown-formatted text.

    This is a lightweight renderer, not a full Markdown implementation.
    Supported: headings (#, ##, ###), bullet lists (- or *), bold
    (**text**), italic (*text*), and plain paragraphs. Not supported:
    tables, links, images, code blocks, numbered lists.

    Parameters
    ----------
    root : Path
        Workspace root.

    path : str | Path
        Relative path inside the workspace for the PDF to create.

    markdown : str
        Markdown-formatted source text.
    """
    target = resolve_path(root, path)
    styles = getSampleStyleSheet()
    story: list[Flowable] = []
    bullet_items: list[str] = []

    def flush_bullets() -> None:
        if not bullet_items:
            return
        story.append(
            ListFlowable(
                [ListItem(Paragraph(_reportlab_markup(item), styles["Normal"])) for item in bullet_items],
                bulletType="bullet",
            )
        )
        story.append(Spacer(1, 6))
        bullet_items.clear()

    for block in parse_blocks(markdown):
        if isinstance(block, Blank):
            flush_bullets()
            story.append(Spacer(1, 6))
        elif isinstance(block, Heading):
            flush_bullets()
            story.append(Paragraph(_reportlab_markup(block.text), styles[_HEADING_STYLE[block.level]]))
        elif isinstance(block, BulletItem):
            bullet_items.append(block.text)
        else:
            flush_bullets()
            story.append(Paragraph(_reportlab_markup(block.text), styles["Normal"]))

    flush_bullets()

    SimpleDocTemplate(str(target), pagesize=LETTER).build(story)
