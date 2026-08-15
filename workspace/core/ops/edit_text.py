"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - edit_text()

Purpose:
    Replace a block of text inside a file, matched by content rather than
    by line number, with an optional dry-run preview.
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops.edit_text

Public API:
    edit_text

Dependencies:
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
from pathlib import Path

from workspace.core.errors import AmbiguousMatchError, NoMatchError
from workspace.core.models import EditResult
from workspace.internal.path import resolve as resolve_path


# ==========================================================================
# Public API
# ==========================================================================

def edit_text(
    root: Path,
    path: str | Path,
    old_text: str,
    new_text: str,
    *,
    expected_occurrences: int = 1,
    dry_run: bool = False,
    encoding: str = "utf-8",
) -> EditResult:
    """Replace a block of text matched by content, not by line number.

    Unlike ``replace_lines``, the target text is located by searching the
    file content for an exact match of ``old_text``. This is more robust
    when the file may have changed since it was last read, because the
    edit is anchored to content rather than to a line offset that may no
    longer point at the intended text.

    Parameters
    ----------
    root : Path
        Workspace root.

    path : str | Path
        Relative path inside the workspace.

    old_text : str
        Exact text to search for. Must match the file content precisely,
        including whitespace and newlines.

    new_text : str
        Replacement text. Pass an empty string to delete ``old_text``.

    expected_occurrences : int, optional
        Number of times ``old_text`` must appear in the file for the edit
        to proceed. Defaults to 1, the safe default for a targeted edit.

    dry_run : bool, optional
        When True, compute and return the diff without writing to disk.

    encoding : str, optional
        Text encoding.

    Returns
    -------
    EditResult
        ``applied`` is False whenever ``dry_run`` is True. ``diff`` is a
        unified diff of the change.

    Raises
    ------
    NoMatchError
        ``old_text`` was not found in the file.

    AmbiguousMatchError
        ``old_text`` matched a different number of times than
        ``expected_occurrences``.
    """

    # ----------------------------------------------------------------------
    # Validate arguments.
    # ----------------------------------------------------------------------

    if expected_occurrences < 1:
        raise ValueError("'expected_occurrences' must be greater than zero.")

    # ----------------------------------------------------------------------
    # Resolve target file.
    # ----------------------------------------------------------------------

    target = resolve_path(root, path)

    # ----------------------------------------------------------------------
    # Read the complete file and locate the requested text.
    #
    # Matching is done against the raw file content, not against
    # individual lines, so old_text may span multiple lines.
    # ----------------------------------------------------------------------

    original = target.read_text(encoding=encoding)

    occurrences = original.count(old_text)

    if occurrences == 0:
        raise NoMatchError(f"No match for the requested text in {path}.")

    if occurrences != expected_occurrences:
        raise AmbiguousMatchError(
            f"Expected {expected_occurrences} occurrence(s) of the requested "
            f"text in {path}, found {occurrences}."
        )

    # ----------------------------------------------------------------------
    # Build the replacement content and its diff.
    #
    # str.replace() with a count equal to the validated occurrences keeps
    # the operation limited to exactly the matches that were counted
    # above.
    # ----------------------------------------------------------------------

    updated = original.replace(old_text, new_text, occurrences)

    diff = "".join(
        difflib.unified_diff(
            original.splitlines(keepends=True),
            updated.splitlines(keepends=True),
            fromfile=str(path),
            tofile=str(path),
        )
    )

    # ----------------------------------------------------------------------
    # Apply the change, unless this is a dry run.
    # ----------------------------------------------------------------------

    if not dry_run:
        target.write_text(updated, encoding=encoding)

    return EditResult(
        path=target,
        applied=not dry_run,
        occurrences=occurrences,
        diff=diff,
    )
