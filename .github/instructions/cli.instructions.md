---
applyTo: "cli/**/*.py"
---

# CLI & Boundary Adapter Instructions

## 1. 1-Based Human Interface Translation
- Terminal arguments, flags, and JSON outline files accept **1-based human page numbers** (where page 1 is the document start).
- The `cli/` adapters (`cli/adapters.py`) MUST convert 1-based human inputs to 0-based core domain models prior to calling `core/` services (e.g., `start_page - 1`).
- When formatting human outputs or messages, convert 0-based core page indices back to 1-based human page numbers.

## 2. Physical File I/O Ownership
- The `cli/` controllers (`cli/controllers.py`) own physical disk I/O (`pathlib.Path`).
- Controllers read file paths into in-memory `io.BytesIO` streams before delegating to `core/` services, and stream resulting `io.BytesIO` buffers back to output files.

## 3. Argument Validation & Error Formatting
- Validate human input bounds (e.g., `start_page >= 1`, `end_page >= start_page`, `insertion_position >= 1`) in adapters.
- Catch domain exceptions (e.g., `PDFIndexOutOfBoundsError`) at the CLI boundary and present user-friendly error messages with non-zero exit codes.
