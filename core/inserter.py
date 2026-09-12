# core/inserter.py

from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader, PdfWriter

from .domain_models import (
    PageInsertionRequest,
    PDFIndexOutOfBoundsError,
    SliceRange,
)
from .stream_manager import open_pdf_input


def _insert_readers(
    target_reader: PdfReader,
    source_reader: PdfReader,
    insertion_index: int,
    source_range: SliceRange | None,
) -> BytesIO:
    """Merge two readers into a rewound in-memory PDF stream."""
    target_page_count = len(target_reader.pages)
    source_page_count = len(source_reader.pages)

    if insertion_index < 0 or insertion_index > target_page_count:
        raise PDFIndexOutOfBoundsError(
            f"insert_index {insertion_index} is outside the target document "
            f"with {target_page_count} pages"
        )

    if source_range is None:
        source_start = 0
        source_end = source_page_count - 1
    else:
        source_start = source_range.start_page
        source_end = source_range.end_page
        if source_end >= source_page_count:
            raise PDFIndexOutOfBoundsError(
                f"source range {source_start}..{source_end} is outside the "
                f"source document with {source_page_count} pages"
            )

    output = BytesIO()
    with PdfWriter() as writer:
        for target_index in range(target_page_count + 1):
            if target_index == insertion_index:
                for source_index in range(source_start, source_end + 1):
                    writer.add_page(source_reader.pages[source_index])
            if target_index < target_page_count:
                writer.add_page(target_reader.pages[target_index])
        writer.write(output)

    output.seek(0)
    return output


def insert_pdf_pages(
    target: BytesIO,
    source: BytesIO,
    insertion_index: int,
    *,
    source_range: SliceRange | None = None,
) -> BytesIO:
    """Return a new PDF with source pages inserted into the target PDF.

    All page indices are strictly 0-based. ``insertion_index`` identifies the
    position before which source pages are inserted. An insertion index equal
    to the target page count appends the source pages.

    When ``source_range`` is provided, its inclusive 0-based page range selects
    the source pages to insert. When it is ``None``, all source pages are
    inserted.

    The input streams remain caller-owned and open. The returned ``BytesIO``
    stream is rewound to byte offset zero.

    Raises:
        PDFIndexOutOfBoundsError: If ``insertion_index`` is greater than the
            target page count or ``source_range`` exceeds the source page
            count.
        pypdf.errors.PdfReadError: If either input stream is not a valid PDF.
    """
    target.seek(0)
    source.seek(0)
    target_reader = PdfReader(target)
    source_reader = PdfReader(source)
    return _insert_readers(
        target_reader,
        source_reader,
        insertion_index,
        source_range,
    )


def insert_pdf_pages_with_request(
    target: BytesIO,
    request: PageInsertionRequest,
) -> BytesIO:
    """Apply a validated page-insertion request to a target PDF stream.

    The request's source may be a path or a ``BytesIO`` stream. Filesystem
    opening, when needed, must be delegated to the core stream manager.
    All request indices remain strictly 0-based.
    """
    target.seek(0)
    target_reader = PdfReader(target)
    with open_pdf_input(request.source) as source_stream:
        source_reader = PdfReader(source_stream)
        return _insert_readers(
            target_reader,
            source_reader,
            request.insert_index,
            request.source_range,
        )
