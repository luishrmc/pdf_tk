# pdf_tk Global Copilot Instructions

## 1. Project Toolchain & Environment
- **Python Version:** Python 3.14+ managed strictly via `uv`.
- **Primary Dependencies:** `pypdf`, `pydantic`.
- **Developer Tools:** `pytest` (with `pytest-cov`), `ruff` (formatting & linting), `mypy` (strict mode).
- **Execution Rule:** Execute commands via `uv run <command>` (e.g., `uv run pytest`, `uv run mypy core cli`, `uv run ruff check .`).

## 2. 3-Tier Boundary Architecture
- **`core/` (Domain Layer):** Pure PDF business logic (`slicer`, `bookmarker`, `inserter`, `stream_manager`). Uses in-memory binary streams (`io.BytesIO`) and immutable Pydantic models. Zero CLI or file system dependencies.
- **`cli/` (Adapter Layer):** CLI argument parsing (`argparse`), physical file I/O (`pathlib.Path`), and controllers. Translates 1-based human page inputs to 0-based core models.
- **`tests/` (Verification Layer):** 100% offline, in-memory testing using synthetic PDF byte generators (`BytesIO`). Zero static PDF binary files allowed.

## 3. Path-Scoped Context Rules
Detailed domain rules and boundary invariants are scoped automatically via path rules in `.github/instructions/`:
- `core/**/*.py` -> `.github/instructions/pdf-domain.instructions.md`
- `cli/**/*.py` -> `.github/instructions/cli.instructions.md`
- `tests/**/*.py` -> `.github/instructions/testing.instructions.md`
