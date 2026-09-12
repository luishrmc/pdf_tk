---
name: pdf-hierarchy-coordinator
description: Extraction, injection, and traversal of hierarchical PDF bookmark outline trees.
---

# PDF Hierarchy Coordinator

Use this skill when parsing bookmark JSON files, building nested `BookmarkTree` models, or injecting bookmark outlines into target PDFs.

## Reference Guides & Utility Scripts
- Reference data models and outline parser snippets are available in [references/hierarchy_patterns.py](references/hierarchy_patterns.py).

## Execution Workflow
1. Parse JSON outline trees into `BookmarkNode` objects (converting 1-based JSON pages to 0-based domain numbers).
2. Recursively traverse `BookmarkNode.children` when generating `pypdf` outline items.
3. Map PDF destinations securely to 0-based page indices.
