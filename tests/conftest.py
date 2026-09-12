from __future__ import annotations

from io import BytesIO

import pytest
from pypdf import PdfWriter


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