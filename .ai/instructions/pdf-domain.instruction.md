---
description: PDF toolkit domain rules, engine boundaries, and decoupled architecture for CLI and UI.
applyTo: 'src/**/*.py,commands/**/*.py,utils/**/*.py,main.py'
---

# PDF Toolkit Domain Architecture & Rules

You are developing an extensible, modular Python PDF toolkit. The business logic must remain completely independent of the presentation layer (CLI or future GUI/Web).

## 1. Architectural Boundaries (Strict Separation of Concerns)
- **Three-Tier Isolation:**
  - `core/` (or `engine/`): Pure PDF domain operations. Zero dependencies on `sys.argv`, `argparse`, `click`, `typer`, or UI toolkits.
  - `cli/` (or `commands/`): Thin presentation wrappers that parse inputs, invoke core services, handle formatting (e.g., `rich`), and return exit codes.
  - `ui/` (future): Presentation layer invoking the exact same `core/` services without altering core logic.
- **Data Exchange:** Use frozen dataclasses or Pydantic models for command payloads and operation results (e.g., `BookmarkNode`, `SliceSpec`, `OperationResult`).
- **Return Values Over Prints:** Core functions must return structured results or generators; never call `print()` or write directly to `sys.stdout` inside domain modules.

## 2. PDF Engine Rules & Operations
- **Library Selection:**
  - Document restructuring, page slicing, merging, and bookmark injection: Use `pypdf`.
  - High-speed text extraction and rendering: Use `pymupdf` (`fitz`) if added, keeping it wrapped behind domain interfaces.
- **Page Indexing Convention:**
  - **Internal Engine:** Strictly **0-based** indexing (`0 <= index < total_pages`).
  - **User-Facing (CLI/UI):** Accept **1-based** human page numbers and convert to 0-based at the boundary layer.
- **Memory & Resource Safety:**
  - Always handle document streams with context managers (`with open(...)`, `with PdfWriter() as writer`).
  - For large operations, slice/merge by streaming page references rather than copying entire documents in memory.
  - Support both file paths (`pathlib.Path`) and binary streams (`io.BytesIO`) as input/output targets.

## 3. Bookmark & Hierarchy Conventions
- When manipulating outlines/bookmarks, preserve parent-child hierarchy using recursive tree structures:
  ```python
  @dataclass(frozen=True, slots=True)
  class BookmarkItem:
      title: str
      page_number: int  # 1-based for user input, normalized internally
      children: list[BookmarkItem] = field(default_factory=list)