import argparse
import logging
import sys

from commands.slice_range import run as run_slice_range
from commands.slice_bookmarks import run as run_slice_bookmarks
from utils.logger import setup_logger

logger = setup_logger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pdf_slicer",
        description="PDF Slicer — slice PDF files by page range or bookmarks.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- slice-range command ---
    range_parser = subparsers.add_parser(
        "slice-range",
        help="Slice a PDF based on a specific page range.",
    )
    range_parser.add_argument("document", type=str, help="Path to the input PDF file.")
    range_parser.add_argument("output_dir", type=str, help="Directory where the output PDF will be saved.")
    range_parser.add_argument("start_page", type=int, help="Start page number (1-based, inclusive).")
    range_parser.add_argument("end_page", type=int, help="End page number (1-based, inclusive).")

    # --- slice-bookmarks command ---
    bookmarks_parser = subparsers.add_parser(
        "slice-bookmarks",
        help="Slice a PDF into chapters based on its bookmarks/outline.",
    )
    bookmarks_parser.add_argument("document", type=str, help="Path to the input PDF file.")
    bookmarks_parser.add_argument("output_dir", type=str, help="Directory where chapter PDFs will be saved.")
    bookmarks_parser.add_argument(
        "--level",
        type=int,
        default=0,
        help="Bookmark nesting level to slice by (0 = top-level chapters, 1 = sections, etc.). Default: 0.",
    )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("PDF Slicer started")
    logger.info(f"Command      : {args.command}")
    logger.info(f"Document     : {args.document}")
    logger.info(f"Output dir   : {args.output_dir}")

    if args.command == "slice-range":
        logger.info(f"Start page   : {args.start_page}")
        logger.info(f"End page     : {args.end_page}")
        logger.info("=" * 60)
        run_slice_range(
            document=args.document,
            output_dir=args.output_dir,
            start_page=args.start_page,
            end_page=args.end_page,
        )

    elif args.command == "slice-bookmarks":
        logger.info(f"Bookmark level: {args.level}")
        logger.info("=" * 60)
        run_slice_bookmarks(
            document=args.document,
            output_dir=args.output_dir,
            level=args.level,
        )

    logger.info("=" * 60)
    logger.info("PDF Slicer finished successfully.")


if __name__ == "__main__":
    main()
