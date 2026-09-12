# cli/parser.py

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from .controllers import (
    add_bookmarks_controller,
    insert_pages_controller,
    slice_bookmarks_controller,
    slice_range_to_file,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser and register all PDF subcommands."""
    parser = argparse.ArgumentParser(
        prog="pdf-tk",
        description="PDF document manipulation toolkit",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    slice_range_parser = subparsers.add_parser(
        "slice-range",
        help="Extract an inclusive page range from a PDF",
    )
    slice_range_parser.add_argument("input_file", type=Path)
    slice_range_parser.add_argument("output_file", type=Path)
    slice_range_parser.add_argument("start_page", type=int)
    slice_range_parser.add_argument("end_page", type=int)
    slice_range_parser.set_defaults(handler=handle_slice_range)

    add_bookmarks_parser = subparsers.add_parser(
        "add-bookmarks",
        help="Add bookmarks from a JSON definition file",
    )
    add_bookmarks_parser.add_argument("input_file", type=Path)
    add_bookmarks_parser.add_argument("bookmarks_file", type=Path)
    add_bookmarks_parser.add_argument("output_file", type=Path)
    add_bookmarks_parser.add_argument(
        "--offset",
        dest="page_offset",
        type=int,
        default=0,
        help="Page offset added after converting 1-based bookmark pages",
    )
    add_bookmarks_parser.set_defaults(handler=handle_add_bookmarks)

    slice_bookmarks_parser = subparsers.add_parser(
        "slice-bookmarks",
        help="Split a PDF into sections defined by bookmarks",
    )
    slice_bookmarks_parser.add_argument("input_file", type=Path)
    slice_bookmarks_parser.add_argument("output_directory", type=Path)
    slice_bookmarks_parser.set_defaults(handler=handle_slice_bookmarks)

    register_insert_pages_command(subparsers)

    return parser


def handle_slice_range(arguments: argparse.Namespace) -> None:
    """Dispatch the slice-range command."""
    slice_range_to_file(
        input_file=arguments.input_file,
        output_file=arguments.output_file,
        start_page=arguments.start_page,
        end_page=arguments.end_page,
    )


def handle_add_bookmarks(arguments: argparse.Namespace) -> None:
    """Dispatch the add-bookmarks command."""
    add_bookmarks_controller(
        input_file=arguments.input_file,
        bookmarks_file=arguments.bookmarks_file,
        output_file=arguments.output_file,
        page_offset=arguments.page_offset,
    )


def handle_slice_bookmarks(arguments: argparse.Namespace) -> None:
    """Dispatch the slice-bookmarks command."""
    slice_bookmarks_controller(
        input_file=arguments.input_file,
        output_directory=arguments.output_directory,
    )


def register_insert_pages_command(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    """Register the ``insert-pages`` CLI subcommand."""
    parser = subparsers.add_parser(
        "insert-pages",
        help="Insert pages from one PDF into another",
    )
    parser.add_argument("target_file", type=Path)
    parser.add_argument("source_file", type=Path)
    parser.add_argument("output_file", type=Path)
    parser.add_argument(
        "insertion_position",
        type=int,
        help="1-based position before which source pages are inserted",
    )
    parser.add_argument(
        "--source-start-page",
        type=int,
        default=None,
        help="Optional 1-based first source page to insert",
    )
    parser.add_argument(
        "--source-end-page",
        type=int,
        default=None,
        help="Optional 1-based last source page to insert",
    )
    parser.set_defaults(handler=handle_insert_pages)


def handle_insert_pages(arguments: argparse.Namespace) -> None:
    """Dispatch parsed ``insert-pages`` arguments to its controller."""
    insert_pages_controller(
        target_file=arguments.target_file,
        source_file=arguments.source_file,
        output_file=arguments.output_file,
        insertion_position=arguments.insertion_position,
        source_start_page=arguments.source_start_page,
        source_end_page=arguments.source_end_page,
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Parse arguments, dispatch the selected command, and return a status."""
    parser = build_parser()
    arguments = parser.parse_args(argv)
    arguments.handler(arguments)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
