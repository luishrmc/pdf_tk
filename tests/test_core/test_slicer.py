from __future__ import annotations

from io import BytesIO

import pytest
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from pypdf.generic import Destination

from core.domain_models import BookmarkNode, BookmarkTree, SliceRange
from core.slicer import slice_pdf_by_bookmarks, slice_pdf_by_range


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


def test_slice_pdf_by_bookmarks_splits_at_next_top_level_bookmark(
    five_page_pdf: BytesIO,
) -> None:
    bookmarks = BookmarkTree(
        roots=(
            BookmarkNode(title="Chapter 1", page_number=0),
            BookmarkNode(title="Chapter 2", page_number=3),
        )
    )

    result = slice_pdf_by_bookmarks(five_page_pdf, bookmarks)

    assert set(result) == {"Chapter 1", "Chapter 2"}
    assert len(PdfReader(result["Chapter 1"]).pages) == 3
    assert len(PdfReader(result["Chapter 2"]).pages) == 2


def test_slice_pdf_by_bookmarks_preserves_remapped_internal_hierarchy(
    five_page_pdf: BytesIO,
) -> None:
    bookmarks = BookmarkTree(
        roots=(
            BookmarkNode(
                title="Chapter 1",
                page_number=1,
                children=(
                    BookmarkNode(title="Section 1.1", page_number=2),
                    BookmarkNode(
                        title="Section 1.2",
                        page_number=3,
                        children=(
                            BookmarkNode(title="Section 1.2.1", page_number=3),
                        ),
                    ),
                ),
            ),
            BookmarkNode(title="Chapter 2", page_number=4),
        )
    )

    result = slice_pdf_by_bookmarks(five_page_pdf, bookmarks)
    reader = PdfReader(result["Chapter 1"])
    outline = reader.outline

    assert isinstance(outline[0], Destination)
    assert isinstance(outline[1], list)
    assert outline[0].title == "Chapter 1"
    assert reader.get_destination_page_number(outline[0]) == 0
    assert isinstance(outline[1][0], Destination)
    assert outline[1][0].title == "Section 1.1"
    assert reader.get_destination_page_number(outline[1][0]) == 1
    assert isinstance(outline[1][1], Destination)
    assert outline[1][1].title == "Section 1.2"
    assert isinstance(outline[1][2], list)
    assert isinstance(outline[1][2][0], Destination)
    assert outline[1][2][0].title == "Section 1.2.1"
    assert reader.get_destination_page_number(outline[1][2][0]) == 2


def test_slice_pdf_by_bookmarks_accepts_pdf_with_existing_nested_outline(
    pdf_with_bookmarks: BytesIO,
) -> None:
    reader = PdfReader(pdf_with_bookmarks)
    outline = reader.outline

    assert isinstance(outline[0], Destination)
    assert isinstance(outline[1], list)
    assert isinstance(outline[2], Destination)
    nested_outline = outline[1]
    assert isinstance(nested_outline[0], Destination)
    assert outline[0].title == "Chapter 1"
    assert nested_outline[0].title == "Section 1.1"
    assert outline[2].title == "Chapter 2"


def test_slice_pdf_by_bookmarks_rejects_empty_bookmark_tree(
    five_page_pdf: BytesIO,
) -> None:
    with pytest.raises(ValueError, match="without bookmarks"):
        slice_pdf_by_bookmarks(five_page_pdf, BookmarkTree())


def test_slice_pdf_by_bookmarks_coalesces_same_page_bookmarks(
    five_page_pdf: BytesIO,
) -> None:
    bookmarks = BookmarkTree(
        roots=(
            BookmarkNode(title="First", page_number=1),
            BookmarkNode(title="Same Page", page_number=1),
        )
    )

    result = slice_pdf_by_bookmarks(five_page_pdf, bookmarks)

    assert set(result) == {"First"}
    assert len(PdfReader(result["First"]).pages) == 4


def test_slice_pdf_by_bookmarks_can_slice_nested_hierarchy_level(
    five_page_pdf: BytesIO,
) -> None:
    bookmarks = BookmarkTree(
        roots=(
            BookmarkNode(
                title="Chapter 1",
                page_number=0,
                children=(BookmarkNode(title="Section 1", page_number=2),),
            ),
            BookmarkNode(title="Chapter 2", page_number=4),
        )
    )

    result = slice_pdf_by_bookmarks(five_page_pdf, bookmarks, level=1)

    assert set(result) == {"Section 1"}
    assert len(PdfReader(result["Section 1"]).pages) == 3


def test_slice_pdf_by_bookmarks_handles_bookmark_on_final_page(
    five_page_pdf: BytesIO,
) -> None:
    bookmarks = BookmarkTree(
        roots=(
            BookmarkNode(title="Chapter 1", page_number=0),
            BookmarkNode(title="Final Page", page_number=4),
        )
    )

    result = slice_pdf_by_bookmarks(five_page_pdf, bookmarks)

    assert len(PdfReader(result["Chapter 1"]).pages) == 4
    assert len(PdfReader(result["Final Page"]).pages) == 1