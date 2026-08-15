"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - edit_text_many()

Purpose:
    Apply a sequence of content-based text edits to a file atomically,
    with an optional dry-run preview.
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops.edit_text_many

Public API:
    edit_text_many

Dependencies:
    dataclasses
    difflib
    pathlib
    workspace.core.errors
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

import difflib
from dataclasses import dataclass
from pathlib import Path

from workspace.core.errors import AmbiguousMatchError, NoMatchError
from workspace.core.models import EditResult
from workspace.internal.path import resolve as resolve_path


# ==========================================================================
# Input type
# ==========================================================================

@dataclass(frozen=True, slots=True)
class TextEdit:
    """A single content-based edit to apply as part of a batch."""

    old_text: str
    new_text: str
    expected_occurrences: int = 1


# ==========================================================================
# Public API
# ==========================================================================

def edit_text_many(
    root: Path,
    path: str | Path,
    edits: list[TextEdit],
    *,
    dry_run: bool = False,
    encoding: str = "utf-8",
) -> EditResult:
    """Apply a sequence of content-based edits to a file, all or nothing.

    Edits are applied in order against an in-memory copy of the file. Each
    edit's ``old_text`` is matched against the content as it stands *after*
    the previous edits in the sequence, so later edits can target text
    introduced by earlier ones. If any edit fails to match, no edit in the
    batch is written to disk.

    Parameters
    ----------
    root : Path
        Workspace root.

    path : str | Path
        Relative path inside the workspace.

    edits : list[TextEdit]
        Edits to apply in order. Each requires ``expected_occurrences``
        matches (default 1) in the content at the time it is applied.

    dry_run : bool, optional
        When True, compute and return the combined diff without writing
        to disk.

    encoding : str, optional
        Text encoding.

    Returns
    -------
    EditResult
        ``occurrences`` is the total number of matched occurrences across
        every edit in the batch. ``diff`` is a single unified diff of the
        file before the batch and after every edit was applied.

    Raises
    ------
    ValueError
        ``edits`` is empty.

    NoMatchError
        Some edit's ``old_text`` was not found in the content at the point
        it was applied.

    AmbiguousMatchError
        Some edit's ``old_text`` matched a different number of times than
        its ``expected_occurrences``.
    """

    # ----------------------------------------------------------------------
    # Validate arguments.
    # ----------------------------------------------------------------------

    if not edits:
        raise ValueError("'edits' must contain at least one edit.")

    for edit in edits:
        if edit.expected_occurrences < 1:
            raise ValueError("'expected_occurrences' must be greater than zero.")

    # ----------------------------------------------------------------------
    # Resolve target file.
    # ----------------------------------------------------------------------

    target = resolve_path(root, path)

    # ----------------------------------------------------------------------
    # Apply every edit in order against an in-memory copy. Nothing is
    # written until every edit in the batch has matched successfully,
    # which is what makes the batch all-or-nothing.
    # ----------------------------------------------------------------------

    original = target.read_text(encoding=encoding)
    current = original
    total_occurrences = 0

    for index, edit in enumerate(edits):
        occurrences = current.count(edit.old_text)

        if occurrences == 0:
            raise NoMatchError(
                f"No match for edit #{index + 1} of {len(edits)} in {path}."
            )

        if occurrences != edit.expected_occurrences:
            raise AmbiguousMatchError(
                f"Expected {edit.expected_occurrences} occurrence(s) for edit "
                f"#{index + 1} of {len(edits)} in {path}, found {occurrences}."
            )

        current = current.replace(edit.old_text, edit.new_text, occurrences)
        total_occurrences += occurrences

    # ----------------------------------------------------------------------
    # Build a single diff covering the whole batch.
    # ----------------------------------------------------------------------

    diff = "".join(
        difflib.unified_diff(
            original.splitlines(keepends=True),
            current.splitlines(keepends=True),
            fromfile=str(path),
            tofile=str(path),
        )
    )

    # ----------------------------------------------------------------------
    # Apply the change, unless this is a dry run.
    # ----------------------------------------------------------------------

    if not dry_run:
        target.write_text(current, encoding=encoding)

    return EditResult(
        path=target,
        applied=not dry_run,
        occurrences=total_occurrences,
        diff=diff,
    )
