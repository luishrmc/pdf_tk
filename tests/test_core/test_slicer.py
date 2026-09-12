from __future__ import annotations

from io import BytesIO

import pytest
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from core.domain_models import SliceRange
from core.slicer import slice_pdf_by_range


def page_widths(stream: BytesIO) -> list[float]:
    """Return page widths used to verify zero-based fixture page selection."""
    return [float(page.mediabox.width) for page in PdfReader(stream).pages]


def test_slice_pdf_by_range_returns_requested_page_count(
    five_page_pdf: BytesIO,
) -> None:
    result = slice_pdf_by_range(
        five_page_pdf,
        SliceRange(start_page=1, end_page=3),
    )

    assert len(PdfReader(result).pages) == 3


def test_slice_pdf_by_range_uses_strict_zero_based_indices(
    five_page_pdf: BytesIO,
) -> None:
    result = slice_pdf_by_range(
        five_page_pdf,
        SliceRange(start_page=1, end_page=2),
    )

    assert page_widths(result) == [73.0, 74.0]


def test_slice_pdf_by_range_supports_single_page_slice(
    five_page_pdf: BytesIO,
) -> None:
    result = slice_pdf_by_range(
        five_page_pdf,
        SliceRange(start_page=2, end_page=2),
    )

    assert page_widths(result) == [74.0]


def test_slice_pdf_by_range_supports_slice_to_document_end(
    five_page_pdf: BytesIO,
) -> None:
    result = slice_pdf_by_range(
        five_page_pdf,
        SliceRange(start_page=3, end_page=4),
    )

    assert page_widths(result) == [75.0, 76.0]


@pytest.mark.parametrize(
    ("start_page", "end_page"),
    [(0, 5), (5, 5)],
)
def test_slice_pdf_by_range_rejects_out_of_bounds_indices(
    five_page_pdf: BytesIO,
    start_page: int,
    end_page: int,
) -> None:
    with pytest.raises(ValueError, match="outside the source document"):
        slice_pdf_by_range(
            five_page_pdf,
            SliceRange(start_page=start_page, end_page=end_page),
        )


@pytest.mark.parametrize("payload", [b"", b"%PDF-truncated"])
def test_slice_pdf_by_range_rejects_malformed_streams(payload: bytes) -> None:
    with pytest.raises(PdfReadError):
        slice_pdf_by_range(BytesIO(payload), SliceRange(start_page=0, end_page=0))