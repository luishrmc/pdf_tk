import json
import os
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from utils.logger import setup_logger

logger = setup_logger(__name__)


def add_bookmarks_recursively(writer, items, offset=0, parent=None):
    for item in items:
        title = item["title"]
        # Convert 1-based printed page number to 0-based PDF page index
        target_page_index = (item["page"] - 1) + offset

        # Ensure page index is within PDF bounds
        if target_page_index < len(writer.pages):
            bookmark = writer.add_outline_item(
                title=title,
                page_number=target_page_index,
                parent=parent,
            )
            # Add nested bookmarks if present
            if "children" in item and item["children"]:
                add_bookmarks_recursively(
                    writer, item["children"], offset=offset, parent=bookmark
                )


def run(document: str, bookmarks_file: str, output: str, offset: int = 0):
    reader = PdfReader(document)
    writer = PdfWriter()

    # Copy all pages from the original PDF
    for page in reader.pages:
        writer.add_page(page)

    # Load bookmark structure
    with open(bookmarks_file, "r", encoding="utf-8") as f:
        bookmarks = json.load(f)

    # Insert outlines
    add_bookmarks_recursively(writer, bookmarks, offset=offset)

    # Ensure destination directory exists
    out_path = Path(output)
    if out_path.parent:
        os.makedirs(out_path.parent, exist_ok=True)

    # Save modified PDF
    with open(out_path, "wb") as f_out:
        writer.write(f_out)

    logger.info(f"Successfully wrote bookmarks to: {output}")