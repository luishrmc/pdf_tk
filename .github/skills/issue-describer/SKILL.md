---
name: issue-describer
description: Use when investigating defects, analyzing tracebacks, and specifying root causes to produce actionable, test-driven implementation blueprints for py-builder.
---

# Issue Describer

Use this skill to diagnose failures, trace execution paths across system boundaries, and formulate concise, testable specifications for implementation agents. This ensures bugs are isolated and handed off to `@py-builder` with clear reproduction fixtures and validation targets.

## Verified Domain Facts
- Internals must adhere strictly to 0-based page indexing within the `core/` boundary.
- Synthetic tests must construct dynamic, in-memory PDF fixtures using `io.BytesIO`; committing or loading static binary `.pdf` files from disk is prohibited.
- `core/` domain services must remain fully decoupled from `cli/` argument parsing, formatting libraries, and `print()` calls.

## Execution Workflow

1. **Context & Failure Mapping**:
   - Extract relevant file paths, function signatures, and error lines from the user prompt or stack trace.
   - Search the workspace to locate the caller chain and inspect boundary crossings between `cli/` presentation wrappers and `core/` domain logic.

2. **Root Cause Analysis**:
   - Verify failure modes against typed models (PEP 695 generics, frozen dataclasses) and parameter expectations.
   - Audit stream handling for premature closures, unbuffered reads, or memory leaks.
   - Identify missing domain exceptions and ensure error propagation respects architectural boundaries.

3. **Handoff Specification for Builder**:
   - Define target file paths and supply a concise (1–3 line) code hint demonstrating the required logic or signature fix.
   - Specify an isolated, in-memory synthetic pytest fixture to reproduce the failure and prevent regressions.
   - List exact validation commands including local environment test, lint, and type-check runs (`pytest`, `ruff`, `mypy`).

## Working Rules
- Never provide full file rewrites; limit code illustrations to minimal, targeted snippets so implementation remains with `@py-builder`.
- Zero `# type: ignore` comments are allowed in recommendations unless explicitly required by a third-party mock limitation.
- Always include edge-case checks (0-byte streams, out-of-bounds indexing, malformed headers) in the test specification.