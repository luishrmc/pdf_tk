# pdf_tk 🛠️

[![Python 3.14+](https://img.shields.io/badge/python-3.14%2B-blue.svg)](https://www.python.org/)
[![Tooling: uv](https://img.shields.io/badge/tooling-uv-purple.svg)](https://github.com/astral-sh/uv)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-261230.svg)](https://github.com/astral-sh/ruff)
[![Type Checker: mypy](https://img.shields.io/badge/types-mypy%20strict-blue.svg)](https://mypy.readthedocs.io/)

`pdf_tk` is a robust, production-grade command-line interface (CLI) toolkit and core library for deterministic PDF document manipulation. Engineered around memory-safe byte stream isolation and strict boundary separation, `pdf_tk` provides high-performance capabilities for slicing, bookmark injection, outline-based sectioning, and page merging without relying on disk intermediate files during core processing.

---

## 1. System Overview & Architecture

`pdf_tk` is built upon a **3-Tier Boundary Architecture** designed to enforce separation of concerns, memory safety, and high testability.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLI Layer (cli/)                              │
│  - Argument Parsing (argparse)      - Physical File Handling (Path)      │
│  - 1-based Human Page Translation   - I/O Adapters & Controllers        │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ Stream / Domain Models
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           Core Layer (core/)                            │
│  - Pure Domain Logic                - In-Memory Streaming (BytesIO)     │
│  - Strict 0-based Page Indexing     - Immutable Domain Models (Pydantic)│
│  - Zero File System / CLI Imports   - Memory-Safe Stream Rewinding      │
└─────────────────────────────────────────────────────────────────────────┘
                                     ▲
                                     │ Synthetic Stream Ingestion
┌────────────────────────────────────┴────────────────────────────────────┐
│                          Test Suite (tests/)                            │
│  - 100% Offline & In-Memory         - Zero External File Artifacts       │
│  - Fixture-driven Byte Generators   - Subsystem Isolation Auditing      │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3-Tier Boundary Architecture

1. **`core/` (Domain Layer)**
   - Contains pure business logic and operations (`slicer`, `bookmarker`, `inserter`, `stream_manager`).
   - Operates exclusively on memory-safe binary streams (`io.BytesIO`) and validated domain models (`Pydantic`).
   - Enforces **zero dependencies** on the local file system (`pathlib.Path`), environment variables, or CLI argument structures.
2. **`cli/` (Adapter & Interface Layer)**
   - Handles command-line invocation via `argparse`, input argument validation, and physical disk I/O (`pathlib.Path`).
   - Translates human-centric CLI inputs into core domain models before delegating execution to `core/` controllers.
3. **`tests/` (Verification Layer)**
   - 100% offline test suite utilizing synthetic in-memory PDF stream generators.
   - Validates internal domain models, boundary edge-cases, error handling, and CLI dispatchers independently.

### Indexing Standards

A central engineering principle of `pdf_tk` is its strict boundary index contract:

* **Internal Core Domain (0-Based Indexing):** All internal functions, slice ranges, domain models (`SliceRange`, `BookmarkNode`, `PageInsertionRequest`), and PDF stream operations use strictly **0-based indexing** (where page 0 represents the first page of a document).
* **CLI & User Interface (1-Based Human Indexing):** Terminal interactions, JSON outline files, and command arguments accept human-intuitive **1-based page numbers** (where page 1 represents the first page). The CLI adapter layer (`cli/adapters.py`) seamlessly translates 1-based human inputs to 0-based core domain models prior to execution.

---

## 2. Tech Stack & Tooling

| Tool | Role & Description |
| :--- | :--- |
| **`uv`** | Lightning-fast Python package and project manager. Manages Python 3.14 environments, dependencies, and lockfiles deterministically. |
| **`pypdf`** | Core PDF stream processing engine. Executes low-level page extraction, outline parsing, bookmark tree injection, and page insertion. |
| **`pydantic`** | Data validation and domain model enforcement. Guarantees immutability and strict type checking across the core domain contracts. |
| **`pytest`** | Modern testing framework used for executing offline, in-memory unit, integration, and CLI adapter test suites with coverage reports. |
| **`ruff` & `mypy`** | Static analysis suite. `ruff` provides fast linting and formatting enforcement, while `mypy` guarantees strict static type compliance across the codebase. |

---

## 3. Features & Command Reference

`pdf_tk` exposes its commands via the `pdf-tk` executable (or via `uv run pdf-tk`).

### Command Overview

```bash
pdf-tk <command> [options] [arguments]
```

---

### `slice-range`

Extract an inclusive range of pages from a source PDF document into a new destination file.

```bash
pdf-tk slice-range <input_file> <output_file> <start_page> <end_page>
```

#### Arguments
* `<input_file>`: Path to the source PDF.
* `<output_file>`: Path where the sliced PDF will be written.
* `<start_page>`: 1-based start page (inclusive).
* `<end_page>`: 1-based end page (inclusive).

#### Example
Extract pages 5 through 20 (inclusive) from `document.pdf`:
```bash
pdf-tk slice-range document.pdf output/extracted_chapter.pdf 5 20
```

---

### `add-bookmarks`

Inject a hierarchical JSON outline tree into a PDF document, optionally adjusting for page offsets.

```bash
pdf-tk add-bookmarks <input_file> <bookmarks_file> <output_file> [--offset OFFSET]
```

#### Arguments & Flags
* `<input_file>`: Path to the input PDF document.
* `<bookmarks_file>`: Path to the JSON file containing the bookmark tree.
* `<output_file>`: Path where the bookmarked PDF will be saved.
* `--offset OFFSET` *(Optional, default: `0`)*: Integer offset added to every 1-based page number (useful when PDF body pages differ from physical sheet counts).

#### Bookmarks JSON Specification
The JSON outline format supports arbitrary nesting via the `children` key and uses 1-based page numbers:

```json
[
  {
    "title": "Chapter 1: Architecture Overview",
    "page": 1,
    "children": [
      {
        "title": "1.1 Domain Boundary Layer",
        "page": 3
      },
      {
        "title": "1.2 Adapter Interface",
        "page": 7,
        "children": [
          {
            "title": "1.2.1 CLI Argument Translation",
            "page": 9
          }
        ]
      }
    ]
  },
  {
    "title": "Chapter 2: Command Reference",
    "page": 15
  }
]
```

#### Example
Inject bookmarks with a 5-page cover/preface offset:
```bash
pdf-tk add-bookmarks manual.pdf outline.json output/manual_bookmarked.pdf --offset 5
```

---

### `slice-bookmarks`

Automatically split an outlined PDF document into separate section files based on its top-level (or nested) bookmark outline.

```bash
pdf-tk slice-bookmarks <input_file> <output_directory>
```

#### Arguments
* `<input_file>`: Path to the input PDF containing an existing bookmark outline.
* `<output_directory>`: Target folder where output sections will be created.

#### Behavior
* Analyzes document outline hierarchy.
* Computes page ranges for each bookmark section.
* Generates sanitized filenames prefixed with sequential index numbers (e.g., `01_Chapter_1_Architecture_Overview.pdf`).

#### Example
```bash
pdf-tk slice-bookmarks full_report.pdf ./sections/
```

---

### `insert-pages`

Insert or merge pages from a source PDF document into a target PDF document at a specified 1-based insertion position.

```bash
pdf-tk insert-pages <target_file> <source_file> <output_file> <insertion_position> [--source-start-page START] [--source-end-page END]
```

#### Arguments & Flags
* `<target_file>`: Path to the base document receiving inserted pages.
* `<source_file>`: Path to the document supplying pages.
* `<output_file>`: Destination path for the merged result.
* `<insertion_position>`: 1-based page position before which source pages will be inserted.
* `--source-start-page START` *(Optional)*: 1-based initial page to select from source document.
* `--source-end-page END` *(Optional)*: 1-based final page to select from source document.

#### Examples

**Insert an entire document at page 1 (prepend):**
```bash
pdf-tk insert-pages main_doc.pdf cover_page.pdf combined.pdf 1
```

**Insert specific pages (pages 2-4) from source into page 10 of target:**
```bash
pdf-tk insert-pages report.pdf appendix.pdf final_report.pdf 10 --source-start-page 2 --source-end-page 4
```

---

## 4. Development & Testing

### Project Setup

`pdf_tk` uses `uv` for dependency management:

```bash
# Clone the repository
git clone https://github.com/your-org/pdf_tk.git
cd pdf_tk

# Install dependencies into virtual environment
uv sync
```

### Running Tests

Run the full in-memory test suite with `pytest`:

```bash
uv run pytest
```

### Static Analysis & Verification

Enforce strict formatting, linting, and type check gates:

```bash
# Code formatting and lint checking
uv run ruff check .
uv run ruff format --check .

# Type checking core & cli modules
uv run mypy core cli
```

---

## 5. Project Plans & Future Vision

The evolution of `pdf_tk` follows a structured multi-phase blueprint:

```
┌───────────────────────────────────────────────────────────────────────────┐
│ Completed (Phases 1–5): Architecture & Engine                             │
│  ✔ Core domain engine & memory-safe stream management (`core/`)           │
│  ✔ Strict 0-based domain model contracts (`pydantic`)                     │
│  ✔ CLI layer & 1-based adapter translation (`cli/`)                       │
│  ✔ Bookmark hierarchy coordination (`pdf-hierarchy-coordinator`)          │
│  ✔ Synthetic, offline in-memory test suite (`tests/`)                     │
└─────────────────────────────────────┬─────────────────────────────────────┘
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ Quality & Polish (Phase 6): Production Hardening                          │
│  ✔ Strict MyPy static typing across core domain & CLI adapters           │
│  ✔ Ruff linting and formatting rule integration                           │
│  ✔ Modernized project configuration & `uv` workspace alignment            │
└─────────────────────────────────────┬─────────────────────────────────────┘
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ Future Enhancements: Extended Capabilities                                │
│  🔹 Encryption & Decryption handling (password protection & permissions)  │
│  🔹 OCR Integration pipeline for scanned PDF text extraction              │
│  🔹 Parallelized Batch Processing pipeline for multi-document workflows   │
│  🔹 REST / Web API wrappers maintaining clean `core/` domain boundaries   │
└───────────────────────────────────────────────────────────────────────────┘
```

### Completed Roadmap (Phases 1–5)
* **Phase 1:** Architectural restructuring & environment standardization with `uv` and Pyproject metadata.
* **Phase 2:** Core domain engine implementation for stream-safe range slicing, bookmarking, and page insertion.
* **Phase 3:** CLI orchestration layer with 1-based to 0-based boundary adapter translation.
* **Phase 4:** Synthetic in-memory Pytest suite achieving 100% offline verification.
* **Phase 5:** Bookmark hierarchy coordinator and section splitting functionality.

### Quality & Polish (Phase 6)
* **Strict Static Typing:** Full compliance with `mypy` strict mode across `core/` and `cli/`.
* **Automated Code Formatting:** Zero-config linting and code style enforcement via `ruff`.
* **Dependency & Workspace Standardization:** Streamlined Python 3.14 tooling with `uv.lock`.

### Future Enhancements
* **Document Security:** Native APIs for password encryption, decryption, and permission flags.
* **OCR & Text Extraction Pipeline:** Optical character recognition plug-ins for scanned PDFs.
* **Batch Processing Engine:** Parallel processing workers for bulk folder operations.
* **Web & Microservice Integration:** Lightweight FastAPI / REST service wrappers exposing `core/` capabilities over HTTP while maintaining absolute domain purity.

---

## License

`pdf_tk` is licensed under the MIT License.
