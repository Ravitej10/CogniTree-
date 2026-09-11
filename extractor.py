"""Step 1 of Module 1: extract raw text from an uploaded document.

Only PDF is implemented for now (matches the deck's PDFPlumber choice).
Extend `extract_text` with an elif branch when other formats (docx,
slides) need to be supported.
"""

from pathlib import Path

import pdfplumber


class ExtractionError(Exception):
    """Raised when a document's text can't be extracted at all."""


def extract_text(file_path: str) -> str:
    """Returns the full text of a PDF, page breaks joined with newlines.

    Scanned/image-only PDFs will return an empty or near-empty string
    here — pdfplumber does not OCR. Flag that upstream rather than
    silently indexing a near-blank document.
    """
    path = Path(file_path)
    if not path.exists():
        raise ExtractionError(f"File not found: {file_path}")
    if path.suffix.lower() != ".pdf":
        raise ExtractionError(f"Unsupported file type: {path.suffix} (only .pdf is implemented)")

    text_parts: list[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text_parts.append(page.extract_text() or "")

    full_text = "\n".join(text_parts).strip()
    if not full_text:
        raise ExtractionError(
            f"No extractable text found in {path.name} — it may be a scanned/image-only PDF."
        )
    return full_text
