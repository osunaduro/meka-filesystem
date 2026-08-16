"""Unit tests for workspace.core.ops.edit_text."""

from pathlib import Path

import pytest

from workspace.core.errors import AmbiguousMatchError, NoMatchError
from workspace.core.ops import edit_text


def _write(root: Path, name: str, content: str) -> Path:
    target = root / name
    target.write_text(content, encoding="utf-8")
    return target


def test_edit_text_replaces_single_match(tmp_path):
    _write(tmp_path, "file.txt", "hello world\n")

    result = edit_text(tmp_path, "file.txt", "hello", "goodbye")

    assert result.applied is True
    assert result.occurrences == 1
    assert (tmp_path / "file.txt").read_text(encoding="utf-8") == "goodbye world\n"


def test_edit_text_dry_run_does_not_write(tmp_path):
    _write(tmp_path, "file.txt", "hello world\n")

    result = edit_text(tmp_path, "file.txt", "hello", "goodbye", dry_run=True)

    assert result.applied is False
    assert (tmp_path / "file.txt").read_text(encoding="utf-8") == "hello world\n"


def test_edit_text_dry_run_diff_contains_change(tmp_path):
    _write(tmp_path, "file.txt", "hello world\n")

    result = edit_text(tmp_path, "file.txt", "hello", "goodbye", dry_run=True)

    assert "-hello world" in result.diff
    assert "+goodbye world" in result.diff


def test_edit_text_no_match_raises(tmp_path):
    _write(tmp_path, "file.txt", "hello world\n")

    with pytest.raises(NoMatchError):
        edit_text(tmp_path, "file.txt", "missing", "replacement")


def test_edit_text_ambiguous_match_raises(tmp_path):
    _write(tmp_path, "file.txt", "dup dup dup\n")

    with pytest.raises(AmbiguousMatchError):
        edit_text(tmp_path, "file.txt", "dup", "single")


def test_edit_text_expected_occurrences_allows_multiple(tmp_path):
    _write(tmp_path, "file.txt", "dup dup dup\n")

    result = edit_text(tmp_path, "file.txt", "dup", "one", expected_occurrences=3)

    assert result.occurrences == 3
    assert (tmp_path / "file.txt").read_text(encoding="utf-8") == "one one one\n"


def test_edit_text_invalid_expected_occurrences_raises(tmp_path):
    _write(tmp_path, "file.txt", "hello\n")

    with pytest.raises(ValueError):
        edit_text(tmp_path, "file.txt", "hello", "bye", expected_occurrences=0)


def test_edit_text_no_match_attaches_closest_match_for_near_miss(tmp_path):
    _write(tmp_path, "file.py", "def greet(name):\n    print('hello ' + name)\n")

    with pytest.raises(NoMatchError) as excinfo:
        edit_text(
            tmp_path,
            "file.py",
            "def greet(name):\n     print('hello ' + name)\n",  # extra space before print
            "def greet(name):\n    print('hi ' + name)\n",
        )

    assert excinfo.value.closest_match is not None
    assert excinfo.value.similarity is not None
    assert excinfo.value.similarity > 0.6
    assert "hello" in excinfo.value.closest_match
    # The hint is folded into the string form, so it reaches MCP clients
    # even if they only surface str(exc).
    assert "Closest match" in str(excinfo.value)


def test_edit_text_no_match_for_unrelated_text_has_no_hint(tmp_path):
    _write(tmp_path, "file.txt", "hello world\n")

    with pytest.raises(NoMatchError) as excinfo:
        edit_text(tmp_path, "file.txt", "completely unrelated Klingon opera libretto", "x")

    assert excinfo.value.closest_match is None
    assert excinfo.value.similarity is None
    assert "Closest match" not in str(excinfo.value)
