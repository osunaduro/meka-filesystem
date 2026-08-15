"""Unit tests for workspace.core.ops.read_many."""

from workspace.core.ops import read_many


def test_read_many_reads_every_existing_file(tmp_path):
    (tmp_path / "a.txt").write_text("A", encoding="utf-8")
    (tmp_path / "b.txt").write_text("B", encoding="utf-8")

    results = read_many(tmp_path, ["a.txt", "b.txt"])

    assert [r.content for r in results] == ["A", "B"]
    assert all(r.error is None for r in results)


def test_read_many_continues_past_missing_file(tmp_path):
    (tmp_path / "a.txt").write_text("A", encoding="utf-8")

    results = read_many(tmp_path, ["a.txt", "missing.txt"])

    assert results[0].content == "A"
    assert results[0].error is None
    assert results[1].content is None
    assert results[1].error is not None


def test_read_many_preserves_request_order(tmp_path):
    (tmp_path / "a.txt").write_text("A", encoding="utf-8")
    (tmp_path / "b.txt").write_text("B", encoding="utf-8")

    results = read_many(tmp_path, ["b.txt", "a.txt"])

    assert [r.content for r in results] == ["B", "A"]


def test_read_many_reports_absolute_path_on_success_and_failure(tmp_path):
    (tmp_path / "a.txt").write_text("A", encoding="utf-8")

    results = read_many(tmp_path, ["a.txt", "missing.txt"])

    assert results[0].path.is_absolute()
    assert results[1].path.is_absolute()
