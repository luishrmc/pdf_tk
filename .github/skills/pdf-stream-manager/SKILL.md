---
name: pdf-stream-manager
description: Resource management and in-memory byte stream handling for PDF read, write, slice, and merge operations.
---

# PDF Stream Manager

Use this skill when implementing binary stream operations, stream copying, or context-managed PDF reading and writing.

## Reference Guides & Utility Scripts
- Detailed helper functions and context manager patterns are provided in [references/stream_patterns.py](references/stream_patterns.py).

## Execution Workflow
1. Use `core.stream_manager.open_pdf_input_bytes_io` or `open_pdf_output_bytes_io` to wrap raw streams safely.
2. Always rewind streams using `rewind_stream(stream)` before re-reading.
3. Perform stream-to-stream copies using bounded chunk sizes via `copy_stream(source, destination)`.
