"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - parse_blocks(), parse_inline()

Purpose:
    Parse a small, deliberately limited subset of Markdown into a
    structured, renderer-agnostic form shared by write_pdf() and
    write_docx(). Not a full Markdown implementation: headings (#, ##,
    ###), bullet lists (- or *), bold (**text**), italic (*text*), and
    plain paragraphs. No tables, links, images, or code blocks.
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops._markdown_lite

Public API:
    Blank
    BulletItem
    Heading
    InlineRun
    Paragraph
    parse_blocks
    parse_inline

Dependencies:
    dataclasses
    re
    typing

Thread Safe:
    yes

Pure:
    yes
"""

# ==========================================================================
# Imports
# ==========================================================================

import re
from dataclasses import dataclass
from typing import Iterator, Union

_BOLD = re.compile(r"\*\*(.+?)\*\*")
_ITALIC = re.compile(r"(?<!\*)\*(?!\*)(.+?)\*(?!\*)")


# ==========================================================================
# Inline runs (bold / italic / plain)
# ==========================================================================

@dataclass(frozen=True, slots=True)
class InlineRun:
    """A run of text with uniform bold/italic formatting."""

    text: str
    bold: bool = False
    italic: bool = False


def parse_inline(text: str) -> list[InlineRun]:
    """Split a line into runs, marking `**bold**` and `*italic*` spans.

    Two-pass split (bold, then italic within the non-bold pieces) keeps
    the precedence simple: bold markers are resolved first.
    """
    runs: list[InlineRun] = []
    pieces: list[tuple[str, bool]] = []
    last = 0
    for match in _BOLD.finditer(text):
        if match.start() > last:
            pieces.append((text[last:match.start()], False))
        pieces.append((match.group(1), True))
        last = match.end()
    if last < len(text):
        pieces.append((text[last:], False))

    for piece, is_bold in pieces:
        if is_bold:
            runs.append(InlineRun(text=piece, bold=True))
            continue
        sub_last = 0
        for match in _ITALIC.finditer(piece):
            if match.start() > sub_last:
                runs.append(InlineRun(text=piece[sub_last:match.start()]))
            runs.append(InlineRun(text=match.group(1), italic=True))
            sub_last = match.end()
        if sub_last < len(piece):
            runs.append(InlineRun(text=piece[sub_last:]))

    return runs or [InlineRun(text="")]


# ==========================================================================
# Block-level structure
# ==========================================================================

@dataclass(frozen=True, slots=True)
class Heading:
    """A `#`/`##`/`###` heading line."""

    level: int
    text: str


@dataclass(frozen=True, slots=True)
class BulletItem:
    """A single `-`/`*` bullet list item."""

    text: str


@dataclass(frozen=True, slots=True)
class Paragraph:
    """A plain paragraph line."""

    text: str


@dataclass(frozen=True, slots=True)
class Blank:
    """A blank line, used as a paragraph/list separator."""


Block = Union[Heading, BulletItem, Paragraph, Blank]


def parse_blocks(markdown: str) -> Iterator[Block]:
    """Classify each line of ``markdown`` into a block, in document order."""
    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()

        if not line:
            yield Blank()
        elif line.startswith("### "):
            yield Heading(level=3, text=line[4:])
        elif line.startswith("## "):
            yield Heading(level=2, text=line[3:])
        elif line.startswith("# "):
            yield Heading(level=1, text=line[2:])
        elif line.startswith("- ") or line.startswith("* "):
            yield BulletItem(text=line[2:])
        else:
            yield Paragraph(text=line)
