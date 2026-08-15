"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - replace_lines()

Purpose:
    Replace, insert or remove lines from a text file.
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops.replace_lines

Public API:
    replace_lines

Dependencies:
    pathlib
    sdk.internal.project
    sdk.internal.path

Thread Safe:
    yes

Pure:
    no
"""

# ==========================================================================
# Imports
# ==========================================================================

from pathlib import Path

from workspace.internal.path import resolve as resolve_path


# ==========================================================================
# Public API
# ==========================================================================

def replace_lines(
    root: Path,
    path: str | Path,
    start: int,
    count: int,
    content: str,
    *,
    encoding: str = "utf-8",
) -> None:
    """Replace a range of lines in a text file.

    Parameters
    ----------
    project : str
        Project name.

    path : str | Path
        Relative path inside the project.

    start : int
        First line to replace (1-based).

    count : int
        Number of lines to replace.

    content : str
        Replacement text.

    encoding : str, optional
        Text encoding.
    """

    # ----------------------------------------------------------------------
    # Validate arguments.
    #
    # Line numbers are 1-based. Negative values are not valid.
    # ----------------------------------------------------------------------

    if start < 1:
        raise ValueError("'start' must be greater than zero.")

    if count < 0:
        raise ValueError("'count' cannot be negative.")

    # ----------------------------------------------------------------------
    # Resolve project context.
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # Resolve target file.
    # ----------------------------------------------------------------------

    target = resolve_path(root, path)

    # ----------------------------------------------------------------------
    # Read the complete file.
    #
    # splitlines(keepends=True) preserves the original line endings
    # (\n, \r\n, etc.) so the file formatting remains unchanged after
    # rewriting.
    # ----------------------------------------------------------------------

    lines = target.read_text(
        encoding=encoding,
    ).splitlines(
        keepends=True,
    )

    # ----------------------------------------------------------------------
    # Prepare replacement content.
    #
    # The replacement text is also split preserving line endings.
    #
    # Slice assignment is used because it naturally supports:
    #
    # - replacing lines
    # - inserting lines (count == 0)
    # - removing lines (content == "")
    #
    # Examples:
    #
    # count = 3
    # content = 3 lines
    #     -> replace
    #
    # count = 0
    # content = N lines
    #     -> insert
    #
    # count = N
    # content = ""
    #     -> delete
    # ----------------------------------------------------------------------

    replacement = content.splitlines(
        keepends=True,
    )

    lines[start - 1 : start - 1 + count] = replacement

    # ----------------------------------------------------------------------
    # Rewrite the file.
    #
    # The complete file is written back after applying the requested
    # modification.
    # ----------------------------------------------------------------------

    target.write_text(
        "".join(lines),
        encoding=encoding,
    )
