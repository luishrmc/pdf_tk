from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader, PdfWriter
from pypdf.generic import IndirectObject, TreeObject

from .domain_models import (
    BookmarkNode,
    BookmarkSection,
    BookmarkTree,
    PDFIndexOutOfBoundsError,
    SliceRange,
)
from .stream_manager import PdfStreamSource, open_pdf_input

type BookmarkSlices = dict[str, BytesIO]
type OutlineParent = TreeObject | IndirectObject | None


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
    *,
    level: int | None = None,
) -> tuple[BookmarkSection, ...]:
    """Flatten bookmark hierarchy into document-order bookmark entries.

    All bookmark page numbers remain strictly 0-based. Parent and descendant
    bookmarks are emitted in recursive document order.
    """
    if level is not None and level < 0:
        raise ValueError("bookmark level must be non-negative")

    sections: list[BookmarkSection] = []

    def visit(nodes: tuple[BookmarkNode, ...], current_level: int) -> None:
        for node in nodes:
            if level is None or current_level == level:
                sections.append(
                    BookmarkSection(
                        title=node.title,
                        page_range=SliceRange(
                            start_page=node.page_number,
                            end_page=node.page_number,
                        ),
                    )
                )
            visit(node.children, current_level + 1)

    visit(bookmarks.roots, 0)
    return tuple(sections)


def _bookmark_nodes_at_level(
    bookmarks: BookmarkTree,
    level: int,
) -> tuple[BookmarkNode, ...]:
    """Return bookmark nodes at one hierarchy level in document order."""
    nodes: list[BookmarkNode] = []

    def visit(current: tuple[BookmarkNode, ...], current_level: int) -> None:
        for node in current:
            if current_level == level:
                nodes.append(node)
            visit(node.children, current_level + 1)

    visit(bookmarks.roots, 0)
    return tuple(nodes)


def _add_outline_subtree(
    writer: PdfWriter,
    node: BookmarkNode,
    *,
    section_start: int,
    section_end: int,
    parent: OutlineParent = None,
) -> None:
    """Copy a bookmark subtree with destinations remapped to a slice."""
    if not section_start <= node.page_number <= section_end:
        return

    outline_item = writer.add_outline_item(
        title=node.title,
        page_number=node.page_number - section_start,
        parent=parent,
    )
    for child in node.children:
        _add_outline_subtree(
            writer,
            child,
            section_start=section_start,
            section_end=section_end,
            parent=outline_item,
        )


def resolve_bookmark_ranges(
    bookmarks: BookmarkTree,
    *,
    total_pages: int,
    level: int = 0,
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

    flattened = flatten_bookmark_tree(bookmarks, level=level)
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
    previous_start: int | None = None
    for section in flattened:
        start_page = section.page_range.start_page
        if previous_start is not None and start_page < previous_start:
            raise ValueError(
                "bookmark page numbers must be non-decreasing in document order"
            )
        if previous_start == start_page:
            continue

        next_start = total_pages
        for candidate in flattened:
            candidate_start = candidate.page_range.start_page
            if candidate_start > start_page:
                next_start = candidate_start
                break

        resolved.append(
            BookmarkSection(
                title=section.title,
                page_range=SliceRange(
                    start_page=start_page,
                    end_page=next_start - 1,
                ),
            )
        )
        previous_start = start_page

    return tuple(resolved)


def slice_pdf_by_bookmarks(
    source: BytesIO,
    bookmarks: BookmarkTree,
    *,
    level: int = 0,
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
        level=level,
    )
    section_nodes = {
        node.title: node for node in _bookmark_nodes_at_level(bookmarks, level)
    }

    sliced: BookmarkSlices = {}
    for section in sections:
        output = BytesIO()
        with PdfWriter() as writer:
            for page_number in range(
                section.page_range.start_page,
                section.page_range.end_page + 1,
            ):
                writer.add_page(reader.pages[page_number])
            _add_outline_subtree(
                writer,
                section_nodes[section.title],
                section_start=section.page_range.start_page,
                section_end=section.page_range.end_page,
            )
            writer.write(output)
        output.seek(0)
        sliced[section.title] = output

    return sliced