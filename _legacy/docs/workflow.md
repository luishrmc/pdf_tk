**Step-by-Step Execution Flow**

**Step 1: Planning (`py-planner`)**

* **Trigger:** You ask, "Add a feature to slice a specific page range from a PDF."
* **Instruction Applied:** Reads `py-base.instructions_3.md` to design immutable data models (`@dataclass(frozen=True, slots=True)`) and exact type signatures.


* **Skill Applied:** Uses `pdf-stream-manager` to ensure the blueprint specifies returning an `io.BytesIO` stream instead of writing directly to disk.
* **Result:** Outputs a step-by-step blueprint detailing exactly what files to touch.

**Step 2: Building (`py-builder`)**

* **Trigger:** You feed the blueprint to `py-builder`.
* **Instruction Applied:** Writes the code, strictly avoiding `# type: ignore` comments and utilizing PEP 695 generic syntax. It ensures local `.venv` execution.


* **Skill Applied:** Uses `python-quality-enforcer` to autonomously run `.venv/bin/ruff check --fix` and `.venv/bin/mypy --strict` on the newly created files.


* **Result:** The `core/slice.py` and `commands/slice.py` files are generated and type-safe.

**Step 3: Testing (`py-tester`)**

* **Trigger:** You ask `py-tester` to verify the new implementation.
* **Instruction Applied:** Reads `testing.instruction.md` to ensure no static binary PDFs are used.
* **Skill Applied:** Uses `python-synthetic-tester` to generate a 0-byte edge-case fixture and spy on the `.close()` method of the memory stream. It runs `.venv/bin/pytest`.


* **Result:** Tests are executed. If they fail, the agent edits the test or code until the suite is green.