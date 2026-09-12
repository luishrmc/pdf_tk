---
applyTo: "core/**/*.py"
---

# Core Domain Instructions & Invariants

## 1. Strict 0-Based Indexing
- All page numbers, slice ranges (`SliceRange`), insertion positions, and bookmark page references within `core/` MUST be strictly **0-based** (`0 <= page_number < total_pages`).
- Never accept or output 1-based human page indices inside `core/` functions or domain models.

## 2. In-Memory Stream Isolation
- `core/` logic operates exclusively on binary byte streams (`io.BytesIO` / `PdfStreamSource`).
- NEVER import or reference `pathlib.Path`, `os`, `sys.argv`, or `argparse` in `core/`.
- Always rewind streams using `rewind_stream()` or `stream.seek(0)` when re-reading PDF inputs.

## 3. Pure Domain Output & Errors
- NEVER call `print()` or write directly to `sys.stdout` or `sys.stderr` within domain functions.
- Raise specific domain exceptions (e.g., `PDFIndexOutOfBoundsError`, `ValueError`) for invalid inputs or out-of-bounds page requests.
- Use immutable Pydantic models (`BaseModel` with `frozen=True`) for domain contracts (`BookmarkNode`, `BookmarkTree`, `SliceRange`).
