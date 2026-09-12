# cli/adapters.py

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from core.domain_models import BookmarkNode, BookmarkTree


def _parse_bookmark_node(
    payload: Any,
    *,
    location: str,
) -> BookmarkNode:
    """Parse one JSON bookmark object into a 0-based domain node."""
    if not isinstance(payload, Mapping):
        raise ValueError(f"{location} must be a JSON object")

    title = payload.get("title")
    page = payload.get("page")
    children = payload.get("children", [])

    if not isinstance(title, str) or not title:
        raise ValueError(f"{location}.title must be a non-empty string")

    if not isinstance(page, int) or isinstance(page, bool) or page < 1:
        raise ValueError(f"{location}.page must be a positive 1-based integer")

    if not isinstance(children, list):
        raise ValueError(f"{location}.children must be a JSON array")

    parsed_children = tuple(
        _parse_bookmark_node(
            child,
            location=f"{location}.children[{index}]",
        )
        for index, child in enumerate(children)
    )

    return BookmarkNode(
        title=title,
        page_number=page - 1,
        children=parsed_children,
    )


def load_bookmark_tree(bookmarks_file: Path) -> BookmarkTree:
    """Read a bookmark JSON file and convert page numbers to 0-based indices.

    The JSON schema uses ``title``, ``page``, and optional ``children`` keys.
    ``page`` values are user-facing 1-based page numbers and are converted to
    the core domain's strictly 0-based ``page_number`` values.

    Raises:
        ValueError: If the JSON structure or bookmark values are invalid.
        json.JSONDecodeError: If the file does not contain valid JSON.
    """
    with bookmarks_file.open("r", encoding="utf-8") as stream:
        payload = json.load(stream)

    if not isinstance(payload, list):
        raise ValueError("bookmark JSON root must be an array")

    roots = tuple(
        _parse_bookmark_node(item, location=f"roots[{index}]")
        for index, item in enumerate(payload)
    )
    return BookmarkTree(roots=roots)