"""Unit tests for workspace.core.ops.read_excel and write_excel."""

from datetime import date

import pytest

from workspace.core.errors import SheetNotFoundError
from workspace.core.ops import read_excel, write_excel


def test_write_then_read_roundtrips_values(tmp_path):
    data = [["name", "qty", "when"], ["bolts", 12, date(2026, 1, 15)], ["nuts", 8, None]]

    write_excel(tmp_path, "stock.xlsx", data)
    result = read_excel(tmp_path, "stock.xlsx")

    assert result.sheet_name == "Sheet1"
    assert result.sheet_names == ["Sheet1"]
    assert result.data[0] == ["name", "qty", "when"]
    assert result.data[1] == ["bolts", 12, "2026-01-15T00:00:00"]
    assert result.data[2] == ["nuts", 8, None]
    assert result.total_rows == 3
    assert result.total_cols == 3


def test_read_excel_with_cell_range_limits_result(tmp_path):
    data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    write_excel(tmp_path, "grid.xlsx", data)

    result = read_excel(tmp_path, "grid.xlsx", cell_range="A1:B2")

    assert result.data == [[1, 2], [4, 5]]
    assert result.total_rows == 2
    assert result.total_cols == 2


def test_write_excel_preserves_other_sheets(tmp_path):
    write_excel(tmp_path, "book.xlsx", [["a"]], sheet="First")
    write_excel(tmp_path, "book.xlsx", [["b"]], sheet="Second")

    first = read_excel(tmp_path, "book.xlsx", sheet="First")
    second = read_excel(tmp_path, "book.xlsx", sheet="Second")

    assert first.data == [["a"]]
    assert second.data == [["b"]]
    assert set(first.sheet_names) == {"First", "Second"}


def test_write_excel_replaces_target_sheet_content(tmp_path):
    write_excel(tmp_path, "book.xlsx", [["old"]], sheet="Data")
    write_excel(tmp_path, "book.xlsx", [["new"]], sheet="Data")

    result = read_excel(tmp_path, "book.xlsx", sheet="Data")

    assert result.data == [["new"]]


def test_write_excel_with_start_cell_offsets_write(tmp_path):
    write_excel(tmp_path, "offset.xlsx", [["x", "y"]], start_cell="B2")

    result = read_excel(tmp_path, "offset.xlsx")

    assert result.data[0] == [None, None, None]
    assert result.data[1] == [None, "x", "y"]


def test_read_excel_missing_sheet_raises(tmp_path):
    write_excel(tmp_path, "book.xlsx", [["a"]], sheet="Data")

    with pytest.raises(SheetNotFoundError):
        read_excel(tmp_path, "book.xlsx", sheet="DoesNotExist")
