"""Unit tests for workspace.core.ops.edit_text_many."""

from pathlib import Path

import pytest

from workspace.core.errors import AmbiguousMatchError, NoMatchError
from workspace.core.ops import TextEdit, edit_text_many


def _write(root: Path, name: str, content: str) -> Path:
    target = root / name
    target.write_text(content, encoding="utf-8")
    return target


def test_edit_text_many_applies_all_edits_in_order(tmp_path):
    _write(tmp_path, "file.txt", "one two three\n")

    edits = [
        TextEdit(old_text="one", new_text="1"),
        TextEdit(old_text="two", new_text="2"),
        TextEdit(old_text="three", new_text="3"),
    ]
    result = edit_text_many(tmp_path, "file.txt", edits)

    assert result.applied is True
    assert result.occurrences == 3
    assert (tmp_path / "file.txt").read_text(encoding="utf-8") == "1 2 3\n"


def test_edit_text_many_later_edit_can_target_earlier_replacement(tmp_path):
    _write(tmp_path, "file.txt", "placeholder\n")

    edits = [
        TextEdit(old_text="placeholder", new_text="TARGET"),
        TextEdit(old_text="TARGET", new_text="final"),
    ]
    result = edit_text_many(tmp_path, "file.txt", edits)

    assert (tmp_path / "file.txt").read_text(encoding="utf-8") == "final\n"
    assert result.occurrences == 2


def test_edit_text_many_dry_run_does_not_write(tmp_path):
    _write(tmp_path, "file.txt", "one two\n")

    edits = [TextEdit(old_text="one", new_text="1")]
    result = edit_text_many(tmp_path, "file.txt", edits, dry_run=True)

    assert result.applied is False
    assert (tmp_path / "file.txt").read_text(encoding="utf-8") == "one two\n"


def test_edit_text_many_is_all_or_nothing(tmp_path):
    _write(tmp_path, "file.txt", "one two\n")

    edits = [
        TextEdit(old_text="one", new_text="1"),
        TextEdit(old_text="missing", new_text="x"),
    ]
    with pytest.raises(NoMatchError):
        edit_text_many(tmp_path, "file.txt", edits)

    assert (tmp_path / "file.txt").read_text(encoding="utf-8") == "one two\n"


def test_edit_text_many_ambiguous_match_raises(tmp_path):
    _write(tmp_path, "file.txt", "dup dup\n")

    edits = [TextEdit(old_text="dup", new_text="single")]
    with pytest.raises(AmbiguousMatchError):
        edit_text_many(tmp_path, "file.txt", edits)


def test_edit_text_many_requires_at_least_one_edit(tmp_path):
    _write(tmp_path, "file.txt", "content\n")

    with pytest.raises(ValueError):
        edit_text_many(tmp_path, "file.txt", [])
