from __future__ import annotations

from io import BytesIO

import pytest
from pypdf import PdfReader, PdfWriter


@pytest.fixture
def five_page_pdf() -> BytesIO:
    """Return a synthetic five-page PDF stream with zero-based page markers."""
    stream = BytesIO()
    with PdfWriter() as writer:
        for page_index in range(5):
            writer.add_blank_page(width=72 + page_index, height=72)
        writer.write(stream)
    stream.seek(0)
    return stream


@pytest.fixture
def pdf_with_bookmarks(five_page_pdf: BytesIO) -> BytesIO:
    """Return a synthetic PDF stream containing a nested bookmark outline."""
    reader = PdfReader(five_page_pdf)
    stream = BytesIO()
    with PdfWriter() as writer:
        for page in reader.pages:
            writer.add_page(page)

        chapter = writer.add_outline_item("Chapter 1", page_number=0)
        writer.add_outline_item("Section 1.1", page_number=1, parent=chapter)
        writer.add_outline_item("Chapter 2", page_number=3)
        writer.write(stream)

    stream.seek(0)
    return stream