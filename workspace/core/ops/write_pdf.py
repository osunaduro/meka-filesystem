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
    re
    reportlab
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

import re
from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Flowable, ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer

from workspace.internal.path import resolve as resolve_path

_BOLD = re.compile(r"\*\*(.+?)\*\*")
_ITALIC = re.compile(r"(?<!\*)\*(?!\*)(.+?)\*(?!\*)")


def _inline_markup(text: str) -> str:
    text = _BOLD.sub(r"<b>\1</b>", text)
    text = _ITALIC.sub(r"<i>\1</i>", text)
    return text


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
                [ListItem(Paragraph(_inline_markup(item), styles["Normal"])) for item in bullet_items],
                bulletType="bullet",
            )
        )
        story.append(Spacer(1, 6))
        bullet_items.clear()

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()

        if not line:
            flush_bullets()
            story.append(Spacer(1, 6))
        elif line.startswith("### "):
            flush_bullets()
            story.append(Paragraph(_inline_markup(line[4:]), styles["Heading3"]))
        elif line.startswith("## "):
            flush_bullets()
            story.append(Paragraph(_inline_markup(line[3:]), styles["Heading2"]))
        elif line.startswith("# "):
            flush_bullets()
            story.append(Paragraph(_inline_markup(line[2:]), styles["Heading1"]))
        elif line.startswith("- ") or line.startswith("* "):
            bullet_items.append(line[2:])
        else:
            flush_bullets()
            story.append(Paragraph(_inline_markup(line), styles["Normal"]))

    flush_bullets()

    SimpleDocTemplate(str(target), pagesize=LETTER).build(story)
