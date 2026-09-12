---
name: pdf-stream-manager
description: Use when reading, writing, merging, or slicing PDF files to ensure memory-safe streaming, proper resource cleanup via context managers, and I/O decoupling (supporting both pathlib.Path and io.BytesIO).
---

# PDF Stream Manager

Use this skill to enforce memory safety and I/O decoupling when implementing PDF engine operations. This ensures the `core/` boundary can handle massive documents efficiently without memory leaks.

## Verified Domain Facts
- `pypdf` is the designated library for document restructuring, slicing, and merging.
- Operations must support both file paths (`pathlib.Path`) and in-memory streams (`io.BytesIO`) as input and output targets[cite: 9].
- Copying entire document objects in memory is strictly prohibited for large operations[cite: 9].

## Execution Workflow

1. **Interface Design (Planning Phase)**:
   - Ensure the function signature accepts `str | pathlib.Path | io.BytesIO` for inputs.
   - Return structured data (e.g., frozen dataclasses) or output streams (`io.BytesIO`) instead of writing directly to disk unless explicitly requested[cite: 9].

2. **Resource Management**:
   - Always open PDF sources using context managers (`with open(path, "rb") as f:`)[cite: 9].
   - Always wrap `PdfWriter()` in a context manager (`with PdfWriter() as writer:`) to ensure buffers are flushed and closed properly[cite: 9].

3. **Streaming Implementation**:
   - When extracting or slicing pages, append page references iteratively to the writer rather than cloning the entire `PdfReader` object.
   - For tests, always implement synthetic fixtures using `io.BytesIO` instead of static `.pdf` files[cite: 10].

## Working Rules
- Never use `print()` or `sys.stdout` within these streaming functions[cite: 9].
- Never leave file handlers unmanaged. If returning a stream, ensure the caller is responsible for closure, or return the bytes directly if small enough.
- When generating synthetic tests for these streams, cover 0-byte files, corrupted headers, and multi-page streams[cite: 10].