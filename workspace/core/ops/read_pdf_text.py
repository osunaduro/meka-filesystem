"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - read_pdf_text()

Purpose:
    Extract text from a PDF, page by page, falling back to OCR for pages
    with no embedded text layer (scanned or image-only pages).
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops.read_pdf_text

Public API:
    read_pdf_text

Dependencies:
    io
    pymupdf
    pytesseract
    PIL
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

import io
from pathlib import Path

import pymupdf
import pytesseract
from PIL import Image

from workspace.core.errors import OcrBackendUnavailableError
from workspace.core.models import PdfPage, PdfTextResult
from workspace.internal.path import resolve as resolve_path

DEFAULT_LANGUAGE = "eng+spa"
OCR_RENDER_DPI = 300


# ==========================================================================
# Public API
# ==========================================================================

def read_pdf_text(
    root: Path,
    path: str | Path,
    *,
    ocr_fallback: bool = True,
    language: str = DEFAULT_LANGUAGE,
) -> PdfTextResult:
    """Extract text from a PDF, page by page.

    Parameters
    ----------
    root : Path
        Workspace root.

    path : str | Path
        Relative path inside the workspace, pointing to a PDF file.

    ocr_fallback : bool, optional
        When True (default), pages with no extractable text layer are
        rendered to an image and passed through OCR. Set to False to only
        read the embedded text layer, which is faster but returns empty
        text for scanned/image-only pages.

    language : str, optional
        Tesseract language code(s) used for the OCR fallback, e.g. "eng",
        "spa", or "eng+spa". Defaults to "eng+spa".

    Returns
    -------
    PdfTextResult
        Text for every page, with ``used_ocr`` marking pages that had no
        text layer and were recognized via OCR instead.
    """
    target = resolve_path(root, path)

    pages: list[PdfPage] = []

    with pymupdf.open(target) as document:
        for index, page in enumerate(document, start=1):
            text = page.get_text().strip()
            used_ocr = False

            if not text and ocr_fallback:
                pixmap = page.get_pixmap(dpi=OCR_RENDER_DPI)
                image = Image.open(io.BytesIO(pixmap.tobytes("png")))
                try:
                    text = pytesseract.image_to_string(image, lang=language).strip()
                except pytesseract.TesseractNotFoundError as error:
                    raise OcrBackendUnavailableError(
                        "Tesseract OCR is not installed or not on PATH."
                    ) from error
                used_ocr = True

            pages.append(PdfPage(number=index, text=text, used_ocr=used_ocr))

    return PdfTextResult(path=target, pages=pages)
