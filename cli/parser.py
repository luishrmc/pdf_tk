# cli/parser.py

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .controllers import slice_range_to_file


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level CLI parser and its subcommands."""
    parser = argparse.ArgumentParser(
        prog="pdf-tk",
        description="PDF document manipulation toolkit",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    slice_range_parser = subparsers.add_parser(
        "slice-range",
        help="Extract an inclusive page range from a PDF",
    )
    slice_range_parser.add_argument(
        "input_file",
        type=Path,
        help="Path to the input PDF",
    )
    slice_range_parser.add_argument(
        "output_file",
        type=Path,
        help="Path for the sliced output PDF",
    )
    slice_range_parser.add_argument(
        "start_page",
        type=int,
        help="First page to include, using 1-based numbering",
    )
    slice_range_parser.add_argument(
        "end_page",
        type=int,
        help="Last page to include, using 1-based numbering",
    )
    slice_range_parser.set_defaults(handler=handle_slice_range)

    return parser


def handle_slice_range(arguments: argparse.Namespace) -> None:
    """Dispatch parsed slice-range arguments to the CLI controller."""
    slice_range_to_file(
        input_file=arguments.input_file,
        output_file=arguments.output_file,
        start_page=arguments.start_page,
        end_page=arguments.end_page,
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Parse CLI arguments, dispatch the selected command, and return a status."""
    parser = build_parser()
    arguments = parser.parse_args(argv)
    arguments.handler(arguments)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())