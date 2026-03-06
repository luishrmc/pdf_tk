import os
from pypdf import PdfReader, PdfWriter
from utils.logger import setup_logger
from utils.pdf_utils import ensure_output_dir, validate_pdf_path

logger = setup_logger(__name__)


def run(document: str, output_dir: str, start_page: int, end_page: int):
    """
    Slices a PDF file based on a given page range and saves the result
    as a single PDF file in the output directory.

    Args:
        document   : Path to the source PDF.
        output_dir : Directory where the sliced PDF will be saved.
        start_page : First page to include (1-based, inclusive).
        end_page   : Last page to include (1-based, inclusive).
    """
    logger.info("[slice-range] Starting page range slice operation.")

    # --- Validate inputs ---
    validate_pdf_path(document)
    ensure_output_dir(output_dir)

    if start_page < 1:
        raise ValueError(f"start_page must be >= 1, got {start_page}.")
    if end_page < start_page:
        raise ValueError(f"end_page ({end_page}) must be >= start_page ({start_page}).")

    # --- Open document ---
    logger.info(f"[slice-range] Opening document: {document}")
    reader = PdfReader(document)
    total_pages = len(reader.pages)
    logger.info(f"[slice-range] Document has {total_pages} page(s).")

    # --- Clamp range to document bounds ---
    if end_page > total_pages:
        logger.warning(
            f"[slice-range] end_page ({end_page}) exceeds total pages ({total_pages}). "
            f"Clamping to {total_pages}."
        )
        end_page = total_pages

    logger.info(f"[slice-range] Slicing pages {start_page} to {end_page} (inclusive).")

    # --- Build output PDF ---
    writer = PdfWriter()
    for page_num in range(start_page - 1, end_page):  # convert to 0-indexed
        logger.debug(f"[slice-range]   Adding page {page_num + 1} (0-index: {page_num}).")
        writer.add_page(reader.pages[page_num])

    pages_added = len(writer.pages)
    logger.info(f"[slice-range] Total pages added to output: {pages_added}.")

    # --- Resolve output path ---
    source_stem = os.path.splitext(os.path.basename(document))[0]
    output_filename = f"{source_stem}_pages_{start_page}-{end_page}.pdf"
    output_path = os.path.join(output_dir, output_filename)

    logger.info(f"[slice-range] Writing output file: {output_path}")
    with open(output_path, "wb") as out_file:
        writer.write(out_file)

    file_size_kb = os.path.getsize(output_path) / 1024
    logger.info(f"[slice-range] Done. File saved: {output_path} ({file_size_kb:.1f} KB).")
