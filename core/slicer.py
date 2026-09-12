from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader, PdfWriter

from .domain_models import (
    BookmarkNode,
    BookmarkSection,
    BookmarkTree,
    PDFIndexOutOfBoundsError,
    SliceRange,
)
from .stream_manager import PdfStreamSource, open_pdf_input

type BookmarkSlices = dict[str, BytesIO]


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

def flatten_bookmark_tree(
    bookmarks: BookmarkTree,
) -> tuple[BookmarkSection, ...]:
    """Flatten bookmark hierarchy into document-order bookmark entries.

    All bookmark page numbers remain strictly 0-based. Parent and descendant
    bookmarks are emitted in recursive document order.
    """
    sections: list[BookmarkSection] = []

    def visit(nodes: tuple[BookmarkNode, ...]) -> None:
        for node in nodes:
            sections.append(
                BookmarkSection(
                    title=node.title,
                    page_range=SliceRange(
                        start_page=node.page_number,
                        end_page=node.page_number,
                    ),
                )
            )
            visit(node.children)

    visit(bookmarks.roots)
    return tuple(sections)


def resolve_bookmark_ranges(
    bookmarks: BookmarkTree,
    *,
    total_pages: int,
) -> tuple[BookmarkSection, ...]:
    """Resolve flattened bookmarks into inclusive, strictly 0-based ranges.

    Each section starts at its bookmark destination and ends immediately before
    the next bookmark in document order. The final section ends at the last
    page of the source document.

    Raises:
        PDFIndexOutOfBoundsError: If a bookmark destination is outside the
            document.
        ValueError: If the document has no pages, titles are duplicated, or
            bookmark destinations are not strictly increasing.
    """
    if total_pages <= 0:
        raise ValueError("cannot resolve bookmark ranges for an empty document")

    flattened = flatten_bookmark_tree(bookmarks)
    if not flattened:
        raise ValueError("cannot slice a document without bookmarks")

    titles: set[str] = set()
    for section in flattened:
        if section.title in titles:
            raise ValueError(f"duplicate bookmark title: {section.title!r}")
        titles.add(section.title)

        page_number = section.page_range.start_page
        if page_number >= total_pages:
            raise PDFIndexOutOfBoundsError(
                f"bookmark page_number {page_number} is outside "
                f"the document with {total_pages} pages"
            )

    resolved: list[BookmarkSection] = []
    for index, section in enumerate(flattened):
        start_page = section.page_range.start_page
        if index:
            previous_start = flattened[index - 1].page_range.start_page
            if start_page <= previous_start:
                raise ValueError(
                    "bookmark page numbers must be strictly increasing in "
                    "document order"
                )

        next_start = (
            flattened[index + 1].page_range.start_page
            if index + 1 < len(flattened)
            else total_pages
        )
        resolved.append(
            BookmarkSection(
                title=section.title,
                page_range=SliceRange(
                    start_page=start_page,
                    end_page=next_start - 1,
                ),
            )
        )

    return tuple(resolved)


def slice_pdf_by_bookmarks(
    source: BytesIO,
    bookmarks: BookmarkTree,
) -> BookmarkSlices:
    """Return one in-memory PDF stream for each bookmark-defined section.

    Nested bookmarks are flattened into strictly 0-based page ranges before
    extraction. The returned dictionary maps bookmark titles to new
    ``BytesIO`` streams. The source stream remains caller-owned and open.

    Raises:
        PDFIndexOutOfBoundsError: If a bookmark destination is outside the
            source document.
        ValueError: If bookmark ranges cannot be resolved.
        pypdf.errors.PdfReadError: If the source is not a valid PDF.
    """
    source.seek(0)
    reader = PdfReader(source)
    sections = resolve_bookmark_ranges(
        bookmarks,
        total_pages=len(reader.pages),
    )

    sliced: BookmarkSlices = {}
    for section in sections:
        output = BytesIO()
        with PdfWriter() as writer:
            for page_number in range(
                section.page_range.start_page,
                section.page_range.end_page + 1,
            ):
                writer.add_page(reader.pages[page_number])
            writer.write(output)
        output.seek(0)
        sliced[section.title] = output

    return sliced