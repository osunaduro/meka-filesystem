"""Unit tests for workspace.core.ops.list_allowed."""

from workspace.core.ops import list_allowed


def test_list_allowed_returns_the_root(tmp_path):
    assert list_allowed(tmp_path) == [tmp_path]
