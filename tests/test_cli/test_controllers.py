from __future__ import annotations

from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from cli.controllers import slice_range_to_file
from core.domain_models import BookmarkNode, BookmarkTree, SliceRange


def test_slice_range_to_file_passes_memory_stream_and_zero_based_range(
    tmp_path: Path,
) -> None:
    input_file = tmp_path / "input.pdf"
    output_file = tmp_path / "output.pdf"
    input_file.write_bytes(b"synthetic input PDF")
    sliced_stream = BytesIO(b"synthetic sliced PDF")

    with patch(
        "cli.controllers.slice_pdf_by_range",
        return_value=sliced_stream,
    ) as slice_pdf:
        slice_range_to_file(
            input_file=input_file,
            output_file=output_file,
            start_page=2,
            end_page=4,
        )

    slice_pdf.assert_called_once()
    source_stream, page_range = slice_pdf.call_args.args
    assert isinstance(source_stream, BytesIO)
    assert source_stream.getvalue() == b"synthetic input PDF"
    assert page_range == SliceRange(start_page=1, end_page=3)
    assert output_file.read_bytes() == b"synthetic sliced PDF"


def test_add_bookmarks_controller_routes_pdf_and_json_to_core(
    tmp_path: Path,
) -> None:
    input_file = tmp_path / "input.pdf"
    bookmarks_file = tmp_path / "bookmarks.json"
    output_file = tmp_path / "output.pdf"
    input_file.write_bytes(b"synthetic input PDF")
    bookmarks_file.write_text(
        '[{"title": "Chapter 1", "page": 1}]',
        encoding="utf-8",
    )
    bookmarked_stream = BytesIO(b"synthetic bookmarked PDF")

    with patch(
        "cli.controllers.add_bookmarks_to_pdf",
        return_value=bookmarked_stream,
    ) as add_bookmarks:
        from cli.controllers import add_bookmarks_controller

        add_bookmarks_controller(input_file, bookmarks_file, output_file)

    add_bookmarks.assert_called_once()
    source_stream, bookmark_tree = add_bookmarks.call_args.args
    assert isinstance(source_stream, BytesIO)
    assert source_stream.getvalue() == b"synthetic input PDF"
    assert isinstance(bookmark_tree, BookmarkTree)
    assert bookmark_tree.roots[0].page_number == 0
    assert output_file.read_bytes() == b"synthetic bookmarked PDF"


def test_slice_bookmarks_controller_writes_each_core_section(
    tmp_path: Path,
) -> None:
    input_file = tmp_path / "input.pdf"
    output_directory = tmp_path / "sections"
    input_file.write_bytes(b"synthetic input PDF")
    bookmark_tree = BookmarkTree(
        roots=(BookmarkNode(title="Chapter 1", page_number=0),)
    )
    sections = {
        "Chapter 1": BytesIO(b"chapter one"),
        "Section 2": BytesIO(b"section two"),
    }

    with patch(
        "cli.controllers._bookmark_tree_from_pdf",
        return_value=bookmark_tree,
    ), patch(
        "cli.controllers.slice_pdf_by_bookmarks",
        return_value=sections,
    ) as slice_bookmarks:
        from cli.controllers import slice_bookmarks_controller

        slice_bookmarks_controller(input_file, output_directory)

    slice_bookmarks.assert_called_once()
    source_stream, passed_tree = slice_bookmarks.call_args.args
    assert isinstance(source_stream, BytesIO)
    assert source_stream.getvalue() == b"synthetic input PDF"
    assert passed_tree == bookmark_tree
    assert (output_directory / "01_Chapter_1.pdf").read_bytes() == b"chapter one"
    assert (output_directory / "02_Section_2.pdf").read_bytes() == b"section two"