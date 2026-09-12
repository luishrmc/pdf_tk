---
name: pdf-hierarchy-coordinator
description: Use when extracting, manipulating, or injecting PDF bookmarks and outlines. Enforces recursive tree structures for hierarchies and strict coordinate conversion between 1-based CLI inputs and 0-based internal engine indexing.
---

# PDF Hierarchy Coordinator

Use this skill to manage the extraction and injection of PDF bookmarks/outlines while preserving parent-child relationships and enforcing strict page indexing boundaries.

## Verified Domain Facts
- **Internal Engine:** Page indexing is strictly 0-based (`0 <= index < total_pages`)[cite: 9].
- **User Boundary (CLI/UI):** Page inputs are strictly 1-based[cite: 9]. 
- Bookmarks must be mapped to a recursive immutable structure (`BookmarkItem`)[cite: 9].

## Execution Workflow

1. **Domain Modeling**:
   - Rely on the standard `@dataclass(frozen=True, slots=True)` for `BookmarkItem`[cite: 9, 11].
   - The dataclass must include `title: str`, `page_number: int`, and `children: list[BookmarkItem]`[cite: 9].

2. **Boundary Conversion**:
   - When receiving inputs from the `cli/` layer, immediately convert the 1-based page numbers to 0-based indices before passing them to `pypdf`[cite: 9].
   - When returning outline data to the `cli/` layer, convert the 0-based indices retrieved from `pypdf` back into 1-based page numbers[cite: 9].

3. **Recursive Processing**:
   - When injecting bookmarks using `pypdf.PdfWriter.add_outline_item`, iterate through the `BookmarkItem` tree recursively.
   - Pass the parent object reference correctly to maintain nesting.

## Working Rules
- Never leak 0-based indices to terminal output wrappers[cite: 9].
- Ensure out-of-bounds page requests raise a custom domain error (e.g., `PDFIndexOutOfBoundsError`) rather than a generic `IndexError`[cite: 9, 11].
- Validate that the target page index exists in the `PdfReader` object before attempting to inject a bookmark.