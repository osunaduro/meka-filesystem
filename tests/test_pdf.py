"""Unit tests for workspace.core.ops.write_pdf, read_pdf_text, edit_pdf, and ocr_image."""

import io

import pymupdf
import pytest
from PIL import Image, ImageDraw, ImageFont

from workspace.core.ops import PdfDeleteOperation, PdfInsertOperation, edit_pdf, ocr_image, read_pdf_text, write_pdf


def _image_with_text(text: str) -> bytes:
    image = Image.new("RGB", (800, 200), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=48)
    draw.text((20, 60), text, fill="black", font=font)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _write_image_only_pdf(path, text: str) -> None:
    document = pymupdf.open()
    page = document.new_page(width=800, height=200)
    page.insert_image(page.rect, stream=_image_with_text(text))
    document.save(path)
    document.close()


def test_write_pdf_then_read_pdf_text_roundtrips_text_layer(tmp_path):
    markdown = "# Title\n\nA paragraph with **bold** and *italic* text.\n\n- item one\n- item two\n"

    write_pdf(tmp_path, "doc.pdf", markdown)
    result = read_pdf_text(tmp_path, "doc.pdf")

    assert len(result.pages) == 1
    page = result.pages[0]
    assert page.number == 1
    assert page.used_ocr is False
    assert "Title" in page.text
    assert "bold" in page.text
    assert "item one" in page.text


def test_read_pdf_text_falls_back_to_ocr_for_image_only_page(tmp_path):
    pdf_path = tmp_path / "scanned.pdf"
    _write_image_only_pdf(pdf_path, "HELLO OCR")

    result = read_pdf_text(tmp_path, "scanned.pdf")

    assert len(result.pages) == 1
    page = result.pages[0]
    assert page.used_ocr is True
    assert "HELLO" in page.text.upper()


def test_read_pdf_text_without_ocr_fallback_leaves_image_only_page_empty(tmp_path):
    pdf_path = tmp_path / "scanned.pdf"
    _write_image_only_pdf(pdf_path, "HELLO OCR")

    result = read_pdf_text(tmp_path, "scanned.pdf", ocr_fallback=False)

    page = result.pages[0]
    assert page.used_ocr is False
    assert page.text == ""


def test_ocr_image_extracts_text_from_a_standalone_image(tmp_path):
    image_path = tmp_path / "note.png"
    image_path.write_bytes(_image_with_text("STANDALONE TEXT"))

    text = ocr_image(tmp_path, "note.png")

    assert "STANDALONE" in text.upper()


def test_edit_pdf_delete_pages_removes_them(tmp_path):
    # write_pdf renders everything onto a single page, so build a real
    # 3-page PDF directly to exercise per-page deletion.
    document = pymupdf.open()
    for label in ("One", "Two", "Three"):
        page = document.new_page()
        page.insert_text((72, 72), label)
    document.save(tmp_path / "multi.pdf")
    document.close()

    edit_pdf(tmp_path, "multi.pdf", [PdfDeleteOperation(pages=[2])])

    result = read_pdf_text(tmp_path, "multi.pdf")
    assert len(result.pages) == 2
    assert "One" in result.pages[0].text
    assert "Three" in result.pages[1].text


def test_edit_pdf_insert_pages_from_source(tmp_path):
    write_pdf(tmp_path, "base.pdf", "# Base\n")
    write_pdf(tmp_path, "extra.pdf", "# Inserted\n")

    edit_pdf(tmp_path, "base.pdf", [PdfInsertOperation(at=1, source="extra.pdf")])

    result = read_pdf_text(tmp_path, "base.pdf")
    assert len(result.pages) == 2
    assert "Inserted" in result.pages[0].text
    assert "Base" in result.pages[1].text


def test_edit_pdf_invalid_page_index_raises_and_leaves_file_untouched(tmp_path):
    write_pdf(tmp_path, "doc.pdf", "# Only page\n")
    original_bytes = (tmp_path / "doc.pdf").read_bytes()

    with pytest.raises(ValueError):
        edit_pdf(tmp_path, "doc.pdf", [PdfDeleteOperation(pages=[5])])

    assert (tmp_path / "doc.pdf").read_bytes() == original_bytes


def test_edit_pdf_requires_at_least_one_operation(tmp_path):
    write_pdf(tmp_path, "doc.pdf", "# Only page\n")

    with pytest.raises(ValueError):
        edit_pdf(tmp_path, "doc.pdf", [])
