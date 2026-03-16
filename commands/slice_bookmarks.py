import os
from pypdf import PdfReader, PdfWriter
from pypdf.generic import Destination
from utils.logger import setup_logger
from utils.pdf_utils import ensure_output_dir, validate_pdf_path, sanitize_filename

logger = setup_logger(__name__)


def get_bookmark_tree(reader: PdfReader) -> list[dict]:
    """
    Parses the PDF outline into a tree structure.

    Each node has:
      - title
      - page   (0-indexed)
      - level
      - children
    """
    def parse(items, level=0):
        nodes = []
        last_node = None

        for item in items:
            if isinstance(item, Destination):
                page_num = reader.get_destination_page_number(item)
                logger.debug(
                    f"[slice-bookmarks]   Found bookmark — level={level}, "
                    f"page={page_num + 1}, title='{item.title}'" # type: ignore
                )
                node = {
                    "title": item.title,
                    "page": page_num,
                    "level": level,
                    "children": [],
                }
                nodes.append(node)
                last_node = node

            elif isinstance(item, list):
                children = parse(item, level + 1)

                # In a normal PDF outline, the nested list belongs to the
                # immediately previous destination.
                if last_node is not None:
                    last_node["children"].extend(children) # type: ignore
                else:
                    # Fallback for malformed outlines
                    nodes.extend(children)

        return nodes

    return parse(reader.outline)


def collect_nodes_at_level(tree: list[dict], target_level: int) -> list[dict]:
    """
    Returns all bookmark nodes at the requested nesting level, preserving
    document order.
    """
    result = []

    def walk(nodes):
        for node in nodes:
            if node["level"] == target_level:
                result.append(node)
            walk(node["children"])

    walk(tree)
    return result


def add_outline_subtree(
    writer: PdfWriter,
    node: dict,
    chapter_start: int,
    chapter_end: int,
    parent=None,
):
    """
    Rebuilds the bookmark subtree inside the sliced PDF.

    chapter_start/chapter_end are source-document page bounds.
    The output bookmark page is remapped relative to chapter_start.
    """
    page = node["page"]

    # Ignore bookmarks outside the extracted page interval
    if not (chapter_start <= page < chapter_end):
        return None

    local_page = page - chapter_start
    outline_ref = writer.add_outline_item(
        title=node["title"],
        page_number=local_page,
        parent=parent,
    )

    for child in node["children"]:
        add_outline_subtree(
            writer=writer,
            node=child,
            chapter_start=chapter_start,
            chapter_end=chapter_end,
            parent=outline_ref,
        )

    return outline_ref


def run(document: str, output_dir: str, level: int = 0):
    """
    Slices a PDF into multiple files based on its bookmarks/outline at a
    given nesting level, saving one PDF per chapter/section.

    Each output file preserves the internal bookmark subtree of the sliced
    chapter/section.
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

    # --- Extract bookmark tree ---
    logger.info("[slice-bookmarks] Traversing document outline (bookmarks)...")
    bookmark_tree = get_bookmark_tree(reader)

    if not bookmark_tree:
        logger.error("[slice-bookmarks] No bookmarks/outline found in this document. Aborting.")
        raise RuntimeError("The document has no bookmarks/outline to slice by.")

    chapters = collect_nodes_at_level(bookmark_tree, level)

    if not chapters:
        available_levels = sorted({
            node["level"]
            for node in collect_nodes_at_level(bookmark_tree, 0)
        })
        logger.error(
            f"[slice-bookmarks] No bookmarks found at level {level}."
        )
        raise ValueError(f"No bookmarks at level {level}.")

    logger.info(f"[slice-bookmarks] Chapters found at level {level}: {len(chapters)}.")
    for i, ch in enumerate(chapters):
        logger.info(f"[slice-bookmarks]   [{i+1:02d}] p.{ch['page']+1} → '{ch['title']}'")

    # --- Slice and save each chapter ---
    logger.info("[slice-bookmarks] Starting chapter extraction...")

    for i, chapter in enumerate(chapters):
        start = chapter["page"]
        end = chapters[i + 1]["page"] if i < len(chapters) - 1 else total_pages
        page_count = end - start

        logger.info(
            f"[slice-bookmarks] Processing chapter {i+1}/{len(chapters)}: "
            f"'{chapter['title']}' — pages {start+1} to {end} ({page_count} page(s))."
        )

        writer = PdfWriter()

        # Copy pages
        for page_num in range(start, end):
            logger.debug(f"[slice-bookmarks]   Adding page {page_num + 1}.")
            writer.add_page(reader.pages[page_num])

        # Rebuild internal bookmarks for this sliced chapter
        add_outline_subtree(
            writer=writer,
            node=chapter,
            chapter_start=start,
            chapter_end=end,
        )

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