---
description: Testing standards, pytest conventions, and synthetic PDF fixtures.
applyTo: 'tests/**/*.py,**/test_*.py'
---

# Testing & Quality Assurance Guidelines

You are writing automated tests for a Python document processing system using `pytest`.

## 1. Test Architecture & Structure
- **Framework:** `pytest` with `pytest-asyncio` and `pytest-mock`.
- **Test Style:** Use plain `assert` statements; do not use `unittest.TestCase`.
- **Naming:** Files must be named `test_<module>.py`, functions named `test_<function>_<scenario>_<expected_result>()`.
- **Isolation:** Tests must be deterministic and fully offline. Never attempt network access or external file downloads.

## 2. PDF Fixtures & Synthetic Data
- **No Binary Blobs in Git:** Never commit static `.pdf` files to the repository.
- **In-Memory Generation:** Always create test PDFs dynamically in memory using `io.BytesIO` via `pypdf` or `reportlab`:
  ```python
  import io
  from pypdf import PdfWriter
  import pytest

  @pytest.fixture
  def blank_pdf_stream() -> io.BytesIO:
      writer = PdfWriter()
      writer.add_blank_page(width=72, height=72)
      stream = io.BytesIO()
      writer.write(stream)
      stream.seek(0)
      return stream

* **Edge-Case Fixture Matrix:** Every parser or extractor must include tests for:
* 0-byte empty files (`io.BytesIO(b"")`).
* Corrupted header streams (`io.BytesIO(b"%PDF-truncated...")`).
* Blank/empty pages.
* Multi-page streams (verify memory handles close properly).



## 3. Mocking & Verification

* Use `unittest.mock` / `pytest-mock` to spy on stream reads and verify `.close()` is called.
* Check return types against exact `dataclass` or `BaseModel` schemas.

---

### What to Avoid (Anti-Patterns)

* **Do not create micro-instructions:** Avoid separate files like `errors.instruction.md`, `imports.instruction.md`, or `formatting.instruction.md`. Small files create token overhead and instruction conflicts.
* **Do not duplicate rules:** If a rule is in `py-base.instruction.md` (e.g., strict typing, no `# type: ignore`), do not repeat it in the testing or domain files.
* **Do not put dynamic state in instructions:** If you are tracking progress, roadmap items, or current sprint tasks, put them in a plain `PLAN.md` file at the root, not an `.instruction.md` file.

<ElicitationsGroup message="Next steps for configuring your workspace:">
  <Elicitation label="Create the pdf-domain.instruction.md file" query="Create the pdf-domain.instruction.md file targeting src/pdf/**/*.py covering coordinate math, streaming pipelines, and engine boundaries."/>
  <Elicitation label="Configure VS Code tasks for automated testing" query="Show how to configure .vscode/tasks.json to run ruff and pytest inside the .venv with single-key shortcuts."/>
  <Elicitation label="Set up a PLAN.md file to guide incremental build" query="Draft a PLAN.md file tailored to track the step-by-step implementation of this Python PDF project."/>
</ElicitationsGroup>
