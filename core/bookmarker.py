# core/bookmarker.py

from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader, PdfWriter
from pypdf.generic import IndirectObject, TreeObject

from .domain_models import BookmarkNode, BookmarkTree, PDFIndexOutOfBoundsError

type OutlineParent = TreeObject | IndirectObject | None


def add_bookmarks_to_pdf(
    source: BytesIO,
    bookmarks: BookmarkTree,
) -> BytesIO:
    """Return a new PDF stream containing the supplied bookmark hierarchy.

    The source stream is caller-owned and remains open. Every bookmark
    destination in ``bookmarks`` is interpreted as a strictly 0-based page
    index. Parent-child relationships must be preserved recursively in the
    generated PDF outline.

    Raises:
        PDFIndexOutOfBoundsError: If a bookmark destination does not exist in
            the source PDF.
        pypdf.errors.PdfReadError: If the source is not a valid PDF.
    """
    source.seek(0)
    reader = PdfReader(source)
    total_pages = len(reader.pages)
    output = BytesIO()
    with PdfWriter() as writer:
        for page in reader.pages:
            writer.add_page(page)

        def add_nodes(
            nodes: tuple[BookmarkNode, ...],
            parent: OutlineParent = None,
        ) -> None:
            for node in nodes:
                if node.page_number >= total_pages:
                    raise PDFIndexOutOfBoundsError(
                        f"bookmark page_number {node.page_number} is outside "
                        f"the document with {total_pages} pages"
                    )

                outline_item = writer.add_outline_item(
                    title=node.title,
                    page_number=node.page_number,
                    parent=parent,
                )
                add_nodes(node.children, parent=outline_item)

        add_nodes(bookmarks.roots)
        writer.write(output)
    output.seek(0)
    return output
