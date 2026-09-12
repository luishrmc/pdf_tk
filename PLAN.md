## `PLAN.md` - pdf_tk Refactoring & Implementation Blueprint

### Phase 1: Architectural Restructuring & Environment Standardization

The current flat structure with `commands/` and `utils/` mixes CLI orchestration with PDF manipulation. We will establish strict boundaries and migrate from `requirements.txt` to `uv`.

* **Initialize `uv` Workspace:** Replace `requirements.txt` with `pyproject.toml`. Define `pypdf`, `pydantic` (for domain boundaries), `pytest`, `ruff`, and `mypy`.


* **Directory Scaffolding:** Create `core/`, `cli/`, `ui/` (empty placeholder), and `tests/`.
* **Deprecate Current Files:** Temporarily move existing `main.py`, `commands/`, and `utils/` to a `_legacy/` directory for reference during the rewrite.



### Phase 2: Core Domain Implementation (Pure PDF Services)

The `core/` directory will contain isolated, testable, 0-based indexed PDF logic using memory-safe streaming. Zero CLI awareness.

* **`core/stream_manager.py`:** Implement context managers for safe `io.BytesIO` and file stream handling (`pdf-stream-manager` skill). Ensure no large binaries are loaded entirely into RAM.
* **`core/domain_models.py`:** Define immutable Pydantic models or Dataclasses for inputs/outputs (e.g., `BookmarkTree`, `SliceResult`, `InsertOperation`) to guarantee a stable API for both CLI and future UI.
* **`core/slicer.py`:**
* *By Range:* Accept 0-based start/end indices. Stream pages to a new PDF writer.
* *By Bookmarks:* Traverse the PDF hierarchy (`pdf-hierarchy-coordinator` skill), map logical sections to 0-based page ranges, and extract streams.


* **`core/bookmarker.py`:** Ingest a `BookmarkTree` object (parsed from JSON in the CLI layer) and recursively apply it to the target PDF stream.
* **`core/inserter.py`:** Accept target PDF stream, source PDF stream, and a 0-based insertion index. Yield a merged PDF stream.

### Phase 3: CLI Orchestration Layer

The `cli/` directory acts as a thin translation layer. It parses terminal inputs, handles file I/O bounds, and maps 1-based human inputs to 0-based core inputs.

* **`cli/parser.py`:** Set up the main command parser (`argparse` or `typer`) with subcommands: `slice-range`, `slice-bookmarks`, `add-bookmarks`, and `insert`.
* **`cli/adapters.py`:** Implement strict validation and 1-based to 0-based index converters.
* **`cli/controllers.py`:** Handle file opening/closing using `core/stream_manager.py`, read JSON for bookmarks, pass streams to `core/` services, and write the output streams to disk.

### Phase 4: Synthetic In-Memory Testing

Enforce the strictly diskless testing strategy using `@py-tester`.

* **`tests/conftest.py`:** Build Pytest fixtures that generate synthetic, valid PDF byte streams in-memory (`io.BytesIO`) using `pypdf.PdfWriter` (e.g., `fixture_5_page_pdf`, `fixture_pdf_with_bookmarks`).
* **`tests/test_core/`:** Verify 0-based indexing logic, memory footprint bounds, and correct PDF outputs purely in-memory.
* **`tests/test_cli/`:** Mock the core services and file system to ensure the CLI correctly parses arguments and properly subtracts 1 from user-provided page numbers.

---