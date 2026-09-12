from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

from cli.parser import main


def test_main_slice_range_routes_terminal_arguments_to_controller() -> None:
    input_file = Path("input.pdf")
    output_file = Path("output.pdf")
    argv = [
        "pdf-tk",
        "slice-range",
        str(input_file),
        str(output_file),
        "2",
        "4",
    ]

    with (
        patch.object(sys, "argv", argv),
        patch(
            "cli.parser.slice_range_to_file",
        ) as slice_range_to_file,
    ):
        exit_code = main()

    assert exit_code == 0
    slice_range_to_file.assert_called_once_with(
        input_file=input_file,
        output_file=output_file,
        start_page=2,
        end_page=4,
    )


def test_main_add_bookmarks_routes_terminal_arguments_to_controller() -> None:
    input_file = Path("input.pdf")
    bookmarks_file = Path("bookmarks.json")
    output_file = Path("bookmarked.pdf")
    argv = [
        "pdf-tk",
        "add-bookmarks",
        str(input_file),
        str(bookmarks_file),
        str(output_file),
    ]

    with (
        patch.object(sys, "argv", argv),
        patch(
            "cli.parser.add_bookmarks_controller",
        ) as add_bookmarks,
    ):
        exit_code = main()

    assert exit_code == 0
    add_bookmarks.assert_called_once_with(
        input_file=input_file,
        bookmarks_file=bookmarks_file,
        output_file=output_file,
        page_offset=0,
    )


def test_main_add_bookmarks_passes_page_offset_to_controller() -> None:
    input_file = Path("input.pdf")
    bookmarks_file = Path("bookmarks.json")
    output_file = Path("bookmarked.pdf")
    argv = [
        "pdf-tk",
        "add-bookmarks",
        str(input_file),
        str(bookmarks_file),
        str(output_file),
        "--offset",
        "27",
    ]

    with (
        patch.object(sys, "argv", argv),
        patch(
            "cli.parser.add_bookmarks_controller",
        ) as add_bookmarks,
    ):
        exit_code = main()

    assert exit_code == 0
    add_bookmarks.assert_called_once_with(
        input_file=input_file,
        bookmarks_file=bookmarks_file,
        output_file=output_file,
        page_offset=27,
    )


def test_main_slice_bookmarks_routes_terminal_arguments_to_controller() -> None:
    input_file = Path("input.pdf")
    output_directory = Path("sections")
    argv = [
        "pdf-tk",
        "slice-bookmarks",
        str(input_file),
        str(output_directory),
    ]

    with (
        patch.object(sys, "argv", argv),
        patch(
            "cli.parser.slice_bookmarks_controller",
        ) as slice_bookmarks,
    ):
        exit_code = main()

    assert exit_code == 0
    slice_bookmarks.assert_called_once_with(
        input_file=input_file,
        output_directory=output_directory,
    )


def test_main_insert_pages_routes_terminal_arguments_to_controller() -> None:
    target_file = Path("target.pdf")
    source_file = Path("source.pdf")
    output_file = Path("merged.pdf")
    argv = [
        "pdf-tk",
        "insert-pages",
        str(target_file),
        str(source_file),
        str(output_file),
        "2",
        "--source-start-page",
        "3",
        "--source-end-page",
        "5",
    ]

    with (
        patch.object(sys, "argv", argv),
        patch(
            "cli.parser.insert_pages_controller",
        ) as insert_pages,
    ):
        exit_code = main()

    assert exit_code == 0
    insert_pages.assert_called_once_with(
        target_file=target_file,
        source_file=source_file,
        output_file=output_file,
        insertion_position=2,
        source_start_page=3,
        source_end_page=5,
    )
