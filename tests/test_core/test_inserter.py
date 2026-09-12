from __future__ import annotations

from io import BytesIO

import pytest
from pypdf import PdfReader, PdfWriter

from core.domain_models import PDFIndexOutOfBoundsError, SliceRange
from core.inserter import insert_pdf_pages


def make_pdf(page_widths: tuple[float, ...]) -> BytesIO:
    """Build a synthetic PDF whose page widths identify page order."""
    stream = BytesIO()
    with PdfWriter() as writer:
        for width in page_widths:
            writer.add_blank_page(width=width, height=72)
        writer.write(stream)
    stream.seek(0)
    return stream


def page_widths(stream: BytesIO) -> list[float]:
    """Return page widths from an in-memory PDF stream."""
    return [float(page.mediabox.width) for page in PdfReader(stream).pages]


def test_insert_pdf_pages_at_beginning_uses_zero_based_index_zero() -> None:
    target = make_pdf((72.0, 73.0, 74.0))
    source = make_pdf((100.0, 101.0))

    result = insert_pdf_pages(target, source, insertion_index=0)

    assert page_widths(result) == [100.0, 101.0, 72.0, 73.0, 74.0]


def test_insert_pdf_pages_in_middle_preserves_target_page_order() -> None:
    target = make_pdf((72.0, 73.0, 74.0))
    source = make_pdf((100.0, 101.0))

    result = insert_pdf_pages(target, source, insertion_index=1)

    assert page_widths(result) == [72.0, 100.0, 101.0, 73.0, 74.0]


def test_insert_pdf_pages_at_target_page_count_appends_source_pages() -> None:
    target = make_pdf((72.0, 73.0, 74.0))
    source = make_pdf((100.0, 101.0))

    result = insert_pdf_pages(target, source, insertion_index=3)

    assert page_widths(result) == [72.0, 73.0, 74.0, 100.0, 101.0]


def test_insert_pdf_pages_supports_inclusive_zero_based_source_range() -> None:
    target = make_pdf((72.0, 73.0))
    source = make_pdf((100.0, 101.0, 102.0))

    result = insert_pdf_pages(
        target,
        source,
        insertion_index=1,
        source_range=SliceRange(start_page=1, end_page=2),
    )

    assert page_widths(result) == [72.0, 101.0, 102.0, 73.0]


@pytest.mark.parametrize("insertion_index", [-1, 4])
def test_insert_pdf_pages_rejects_out_of_bounds_insertion_indices(
    insertion_index: int,
) -> None:
    target = make_pdf((72.0, 73.0, 74.0))
    source = make_pdf((100.0,))

    with pytest.raises(PDFIndexOutOfBoundsError):
        insert_pdf_pages(target, source, insertion_index)


def test_insert_pdf_pages_rejects_out_of_bounds_source_range() -> None:
    target = make_pdf((72.0,))
    source = make_pdf((100.0, 101.0))

    with pytest.raises(PDFIndexOutOfBoundsError):
        insert_pdf_pages(
            target,
            source,
            insertion_index=0,
            source_range=SliceRange(start_page=0, end_page=2),
        )


def test_insert_pdf_pages_rewinds_inputs_and_returns_readable_output() -> None:
    target = make_pdf((72.0, 73.0))
    source = make_pdf((100.0,))
    target.seek(0, 2)
    source.seek(0, 2)

    result = insert_pdf_pages(target, source, insertion_index=1)

    assert not target.closed
    assert not source.closed
    assert result.tell() == 0
    assert result.read(5) == b"%PDF-"
    result.seek(0)
    assert len(PdfReader(result).pages) == 3
