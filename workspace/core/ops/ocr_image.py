"""
MEKA Core SDK

Domain:
    Filesystem

Component:
    Operations - ocr_image()

Purpose:
    Extract text from an image file using OCR.
"""

"""
MEKA Metadata

Domain:
    filesystem

Component:
    ops.ocr_image

Public API:
    ocr_image

Dependencies:
    PIL
    pytesseract
    pathlib
    workspace.core.errors
    workspace.internal.path

Thread Safe:
    yes

Pure:
    no
"""

# ==========================================================================
# Imports
# ==========================================================================

from pathlib import Path

import pytesseract
from PIL import Image

from workspace.core.errors import OcrBackendUnavailableError
from workspace.internal.path import resolve as resolve_path

DEFAULT_LANGUAGE = "eng+spa"


# ==========================================================================
# Public API
# ==========================================================================

def ocr_image(root: Path, path: str | Path, *, language: str = DEFAULT_LANGUAGE) -> str:
    """Extract text from an image file using OCR.

    Parameters
    ----------
    root : Path
        Workspace root.

    path : str | Path
        Relative path inside the workspace, pointing to an image file
        (PNG, JPEG, TIFF, BMP, or any format Pillow can open).

    language : str, optional
        Tesseract language code(s), e.g. "eng", "spa", or "eng+spa" to try
        both. Defaults to "eng+spa".

    Returns
    -------
    str
        The text recognized in the image. Empty string if none is found.
    """
    target = resolve_path(root, path)

    try:
        with Image.open(target) as image:
            return pytesseract.image_to_string(image, lang=language)
    except pytesseract.TesseractNotFoundError as error:
        raise OcrBackendUnavailableError(
            "Tesseract OCR is not installed or not on PATH."
        ) from error
