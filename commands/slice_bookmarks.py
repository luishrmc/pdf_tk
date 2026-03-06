import os
from pypdf import PdfReader, PdfWriter
from pypdf.generic import Destination
from utils.logger import setup_logger
from utils.pdf_utils import ensure_output_dir, validate_pdf_path, sanitize_filename

logger = setup_logger(__name__)


def get_bookmarks(reader: PdfReader) -> list[dict]:
    """
    Recursively traverses the PDF outline (bookmarks) and returns a flat list
    of dicts with keys: title, page (0-indexed), level.
    """
    bookmarks = []

    def traverse(outline, level=0):
        for item in outline:
            if isinstance(item, Destination):
                page_num = reader.get_destination_page_number(item)
                logger.debug(
                    f"[slice-bookmarks]   Found bookmark — level={level}, "
                    f"page={page_num + 1}, title='{item.title}'"
                )
                bookmarks.append({
                    "title": item.title,
                    "page": page_num,
                    "level": level,
                })
            elif isinstance(item, list):
                traverse(item, level + 1)

    traverse(reader.outline)
    return bookmarks


def run(document: str, output_dir: str, level: int = 0):
    """
    Slices a PDF into multiple files based on its bookmarks/outline at a
    given nesting level, saving one PDF per chapter/section.

    Args:
        document   : Path to the source PDF.
        output_dir : Directory where chapter PDFs will be saved.
        level      : Bookmark nesting level to slice by (0 = top-level).
    """
    logger.info("[slice-bookmarks] Starting bookmark-based slice operation.")

    # --- Validate inputs ---
    validate_pdf_path(document)
    ensure_output_dir(output_dir)

    # --- Open document ---
    logger.info(f"[slice-bookmarks] Opening document: {document}")
    reader = PdfReader(document)
    total_pages = len(reader.pages)
    logger.info(f"[slice-bookmarks] Document has {total_pages} page(s).")

    # --- Extract bookmarks ---
    logger.info("[slice-bookmarks] Traversing document outline (bookmarks)...")
    all_bookmarks = get_bookmarks(reader)

    if not all_bookmarks:
        logger.error("[slice-bookmarks] No bookmarks/outline found in this document. Aborting.")
        raise RuntimeError("The document has no bookmarks/outline to slice by.")

    logger.info(f"[slice-bookmarks] Total bookmarks found (all levels): {len(all_bookmarks)}.")

    # --- Filter target level ---
    chapters = [b for b in all_bookmarks if b["level"] == level]

    if not chapters:
        available_levels = sorted(set(b["level"] for b in all_bookmarks))
        logger.error(
            f"[slice-bookmarks] No bookmarks found at level {level}. "
            f"Available levels: {available_levels}."
        )
        raise ValueError(
            f"No bookmarks at level {level}. Try one of: {available_levels}."
        )

    logger.info(f"[slice-bookmarks] Chapters found at level {level}: {len(chapters)}.")
    for i, ch in enumerate(chapters):
        logger.info(f"[slice-bookmarks]   [{i+1:02d}] p.{ch['page']+1} → '{ch['title']}'")

    # --- Slice and save each chapter ---
    logger.info("[slice-bookmarks] Starting chapter extraction...")

    for i, chapter in enumerate(chapters):
        start = chapter["page"]  # 0-indexed
        end = chapters[i + 1]["page"] if i < len(chapters) - 1 else total_pages
        page_count = end - start

        logger.info(
            f"[slice-bookmarks] Processing chapter {i+1}/{len(chapters)}: "
            f"'{chapter['title']}' — pages {start+1} to {end} ({page_count} page(s))."
        )

        writer = PdfWriter()
        for page_num in range(start, end):
            logger.debug(f"[slice-bookmarks]   Adding page {page_num + 1}.")
            writer.add_page(reader.pages[page_num])

        safe_title = sanitize_filename(chapter["title"])
        output_filename = f"{i+1:02d}_{safe_title}.pdf"
        output_path = os.path.join(output_dir, output_filename)

        logger.info(f"[slice-bookmarks]   Writing: {output_path}")
        with open(output_path, "wb") as f:
            writer.write(f)

        file_size_kb = os.path.getsize(output_path) / 1024
        logger.info(f"[slice-bookmarks]   Saved: {output_filename} ({file_size_kb:.1f} KB).")

    logger.info(
        f"[slice-bookmarks] All {len(chapters)} chapter(s) saved to '{output_dir}'."
    )
