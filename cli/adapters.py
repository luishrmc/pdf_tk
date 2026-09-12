# cli/adapters.py

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from core.domain_models import BookmarkNode, BookmarkTree, SliceRange


def to_slice_range(start_page: int, end_page: int) -> SliceRange:
    """Convert inclusive 1-based human page numbers to a 0-based SliceRange.

    Raises:
        ValueError: If either page number is less than one or the end page
            precedes the start page.
    """
    if start_page < 1:
        raise ValueError("start_page must be at least 1")
    if end_page < 1:
        raise ValueError("end_page must be at least 1")
    if end_page < start_page:
        raise ValueError("end_page must be greater than or equal to start_page")

    return SliceRange(
        start_page=start_page - 1,
        end_page=end_page - 1,
    )


def _parse_bookmark_node(
    payload: Any,
    *,
    location: str,
    page_offset: int = 0,
) -> BookmarkNode | None:
    """Parse one JSON bookmark object into a 0-based domain node.

    A bookmark without a ``page`` is a label-only outline entry and is omitted
    because the core domain requires every ``BookmarkNode`` to have a page.
    """
    if not isinstance(payload, Mapping):
        raise ValueError(f"{location} must be a JSON object")

    title = payload.get("title")
    page = payload.get("page")
    children = payload.get("children", [])

    if not isinstance(title, str) or not title:
        raise ValueError(f"{location}.title must be a non-empty string")
    if page is None:
        return None
    if not isinstance(page, int) or isinstance(page, bool) or page < 1:
        raise ValueError(f"{location}.page must be a positive 1-based integer")
    if not isinstance(children, list):
        raise ValueError(f"{location}.children must be a JSON array")

    page_number = page - 1 + page_offset
    if page_number < 0:
        raise ValueError(
            f"{location}.page with offset {page_offset} resolves to a "
            "negative 0-based page number"
        )

    return BookmarkNode(
        title=title,
        page_number=page_number,
        children=tuple(
            node
            for index, child in enumerate(children)
            if (
                node := _parse_bookmark_node(
                    child,
                    location=f"{location}.children[{index}]",
                    page_offset=page_offset,
                )
            )
            is not None
        ),
    )


def load_bookmark_tree(
    bookmarks_file: Path,
    *,
    page_offset: int = 0,
) -> BookmarkTree:
    """Read bookmark JSON and return a validated 0-based tree.

    Each positive 1-based JSON page is converted with ``page - 1`` and then
    adjusted by ``page_offset`` before entering the core domain.
    """
    with bookmarks_file.open("r", encoding="utf-8") as stream:
        payload = json.load(stream)

    if not isinstance(payload, list):
        raise ValueError("bookmark JSON root must be an array")

    roots = tuple(
        node
        for index, item in enumerate(payload)
        if (
            node := _parse_bookmark_node(
                item,
                location=f"roots[{index}]",
                page_offset=page_offset,
            )
        )
        is not None
    )
    return BookmarkTree(roots=roots)