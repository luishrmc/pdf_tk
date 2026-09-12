---
applyTo: "tests/**/*.py"
---

# Testing & Synthetic Fixture Instructions

## 1. 100% In-Memory Synthetic Testing
- Tests MUST construct dynamic, in-memory PDF streams (`io.BytesIO`) using `pypdf.PdfWriter()` or shared pytest fixtures (`tests/conftest.py`).
- NEVER read or write static `.pdf` binary files from the disk. Committing `.pdf` binary files to the repository is strictly prohibited.

## 2. Subsystem Boundary Isolation
- `tests/test_core/`: Verify 0-based domain logic, stream rewinding, edge-case bounds handling, and model immutability purely in-memory.
- `tests/test_cli/`: Mock `core/` services and file system calls to verify argument parsing, 1-based to 0-based adapter conversion, and controller file handling.

## 3. Property & Edge-Case Coverage
- Proactively test edge cases: single-page documents, out-of-bounds page indices, empty JSON trees, zero-offset and positive-offset bookmark injections.
- Utilize plain `pytest` assertions (`assert`) and `pytest.raises` for exception checks.
