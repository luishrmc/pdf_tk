# cli/controllers.py

from __future__ import annotations

import re
from collections.abc import Sequence
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader
from pypdf.generic import Destination

from core.bookmarker import add_bookmarks_to_pdf
from core.domain_models import BookmarkNode, BookmarkTree
from core.slicer import slice_pdf_by_bookmarks, slice_pdf_by_range
from core.stream_manager import copy_stream, rewind_stream

from .adapters import load_bookmark_tree, to_slice_range


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


def _read_pdf_stream(input_file: Path) -> BytesIO:
    """Read a physical PDF path into a caller-owned in-memory stream."""
    with input_file.open("rb") as source:
        stream = BytesIO(source.read())
    stream.seek(0)
    return stream


def _sanitize_section_title(title: str) -> str:
    """Convert a bookmark title into a safe filename component."""
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "_", title).strip("._")
    return sanitized or "section"


def add_bookmarks_controller(
    input_file: Path,
    bookmarks_file: Path,
    output_file: Path,
    page_offset: int = 0,
) -> None:
    """Add JSON-defined bookmarks to a physical PDF file.

    This controller owns all physical file access. Bookmark JSON page values
    are converted from 1-based CLI representation to 0-based core values by
    ``load_bookmark_tree``.
    """
    source = _read_pdf_stream(input_file)
    bookmarks = load_bookmark_tree(bookmarks_file, page_offset=page_offset)
    result = add_bookmarks_to_pdf(source, bookmarks)

    rewind_stream(result)
    with output_file.open("wb") as destination:
        copy_stream(result, destination)


def _bookmark_tree_from_pdf(source: BytesIO) -> BookmarkTree:
    """Translate an existing PDF outline into the core bookmark model."""
    source.seek(0)
    reader = PdfReader(source)

    def parse_outline(items: Sequence[object]) -> tuple[BookmarkNode, ...]:
        nodes: list[BookmarkNode] = []
        for item in items:
            if isinstance(item, Destination):
                page_number = reader.get_destination_page_number(item)
                if page_number is None or not isinstance(item.title, str):
                    continue
                nodes.append(
                    BookmarkNode(title=item.title, page_number=page_number)
                )
            elif isinstance(item, list) and nodes:
                parent = nodes[-1]
                nodes[-1] = parent.model_copy(
                    update={"children": parse_outline(item)}
                )
        return tuple(nodes)

    return BookmarkTree(roots=parse_outline(reader.outline))


def slice_bookmarks_controller(
    input_file: Path,
    output_directory: Path,
) -> None:
    """Slice an outlined PDF into sanitized section files."""
    source = _read_pdf_stream(input_file)
    bookmark_tree = _bookmark_tree_from_pdf(source)
    sections = slice_pdf_by_bookmarks(source, bookmark_tree)
    output_directory.mkdir(parents=True, exist_ok=True)

    for index, (title, section_stream) in enumerate(sections.items(), start=1):
        output_file = output_directory / (
            f"{index:02d}_{_sanitize_section_title(title)}.pdf"
        )
        rewind_stream(section_stream)
        with output_file.open("wb") as destination:
            copy_stream(section_stream, destination)


def add_bookmarks_to_file(
    input_file: Path,
    bookmarks_file: Path,
    output_file: Path,
    page_offset: int = 0,
) -> None:
    """Compatibility wrapper for the original controller name."""
    add_bookmarks_controller(
        input_file,
        bookmarks_file,
        output_file,
        page_offset=page_offset,
    )


def slice_bookmarks_to_directory(
    input_file: Path,
    output_directory: Path,
) -> None:
    """Compatibility wrapper for the original controller name."""
    slice_bookmarks_controller(input_file, output_directory)