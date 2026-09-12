# cli/controllers.py

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from core.slicer import slice_pdf_by_range
from core.stream_manager import copy_stream, rewind_stream

from .adapters import to_slice_range


def slice_range_to_file(
    input_file: Path,
    output_file: Path,
    start_page: int,
    end_page: int,
) -> None:
    """Slice a physical PDF file using 1-based CLI page numbers.

    This CLI controller owns filesystem access. It reads the source path into
    a caller-owned BytesIO stream, converts human-facing page numbers into
    the core's inclusive 0-based SliceRange, delegates PDF manipulation to
    core.slicer, and writes the returned stream to the output path.

    The core tier performs no filesystem access or CLI input conversion.
    """
    page_range = to_slice_range(start_page, end_page)
    input_stream = BytesIO(input_file.read_bytes())
    output_stream = slice_pdf_by_range(input_stream, page_range)

    rewind_stream(output_stream)
    with output_file.open("wb") as destination:
        copy_stream(output_stream, destination)