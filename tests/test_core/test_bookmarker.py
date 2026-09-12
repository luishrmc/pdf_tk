from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader
from pypdf.generic import Destination

from core.bookmarker import add_bookmarks_to_pdf
from core.domain_models import BookmarkNode, BookmarkTree


def test_add_bookmarks_to_pdf_preserves_nested_outline_hierarchy(
    five_page_pdf: BytesIO,
) -> None:
    bookmarks = BookmarkTree(
        roots=(
            BookmarkNode(
                title="Chapter 1",
                page_number=0,
                children=(
                    BookmarkNode(title="Section 1.1", page_number=1),
                    BookmarkNode(title="Section 1.2", page_number=2),
                ),
            ),
            BookmarkNode(title="Chapter 2", page_number=3),
        )
    )

    result = add_bookmarks_to_pdf(five_page_pdf, bookmarks)
    reader = PdfReader(result)
    outline = reader.outline

    assert len(reader.pages) == 5
    assert isinstance(outline[0], Destination)
    assert isinstance(outline[1], list)
    assert isinstance(outline[2], Destination)
    nested_outline = outline[1]
    assert isinstance(nested_outline[0], Destination)
    assert isinstance(nested_outline[1], Destination)
    assert outline[0].title == "Chapter 1"
    assert nested_outline[0].title == "Section 1.1"
    assert nested_outline[1].title == "Section 1.2"
    assert outline[2].title == "Chapter 2"


def test_add_bookmarks_to_pdf_preserves_zero_based_destinations(
    five_page_pdf: BytesIO,
) -> None:
    bookmarks = BookmarkTree(
        roots=(
            BookmarkNode(title="First Page", page_number=0),
            BookmarkNode(title="Last Page", page_number=4),
        )
    )

    result = add_bookmarks_to_pdf(five_page_pdf, bookmarks)
    reader = PdfReader(result)
    outline = reader.outline

    assert isinstance(outline[0], Destination)
    assert isinstance(outline[1], Destination)
    assert reader.get_destination_page_number(outline[0]) == 0
    assert reader.get_destination_page_number(outline[1]) == 4
