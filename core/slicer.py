from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader, PdfWriter

from .domain_models import SliceRange
from .stream_manager import PdfStreamSource, open_pdf_input


def slice_pdf_by_range(
    source: PdfStreamSource,
    page_range: SliceRange,
) -> BytesIO:
    """Return an in-memory PDF containing an inclusive 0-based page range.

    The source may be a filesystem path or a caller-owned ``BytesIO`` stream.
    Pages are added one at a time to the writer, and the returned stream is
    rewound to byte offset zero for immediate reading.

    Raises:
        ValueError: If either range endpoint is outside the source document.
    """
    with open_pdf_input(source) as input_stream:
        reader = PdfReader(input_stream)
        total_pages = len(reader.pages)

        if page_range.end_page >= total_pages:
            raise ValueError(
                "page range is outside the source document: "
                f"end_page={page_range.end_page}, total_pages={total_pages}"
            )

        output_stream = BytesIO()
        with PdfWriter() as writer:
            for page_index in range(page_range.start_page, page_range.end_page + 1):
                writer.add_page(reader.pages[page_index])
            writer.write(output_stream)

    output_stream.seek(0)
    return output_stream