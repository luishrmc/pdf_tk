from __future__ import annotations

import json
from pathlib import Path

import pytest

from cli.adapters import load_bookmark_tree, to_slice_range


def test_to_slice_range_converts_one_based_pages_to_zero_based_range() -> None:
    result = to_slice_range(start_page=1, end_page=5)

    assert result.start_page == 0
    assert result.end_page == 4


@pytest.mark.parametrize(
    ("start_page", "end_page"),
    [(0, 5), (-1, 5), (1, 0), (3, 2)],
)
def test_to_slice_range_rejects_invalid_human_page_ranges(
    start_page: int,
    end_page: int,
) -> None:
    with pytest.raises(ValueError):
        to_slice_range(start_page=start_page, end_page=end_page)


def test_load_bookmark_tree_converts_json_pages_to_zero_based_model(
    tmp_path: Path,
) -> None:
    bookmarks_file = tmp_path / "bookmarks.json"
    bookmarks_file.write_text(
        json.dumps(
            [
                {
                    "title": "Chapter 1",
                    "page": 1,
                    "children": [
                        {"title": "Section 1.1", "page": 3},
                    ],
                }
            ]
        ),
        encoding="utf-8",
    )

    result = load_bookmark_tree(bookmarks_file)

    assert result.roots[0].page_number == 0
    assert result.roots[0].children[0].page_number == 2


def test_load_bookmark_tree_applies_page_offset(tmp_path: Path) -> None:
    bookmarks_file = tmp_path / "bookmarks.json"
    bookmarks_file.write_text(
        '[{"title": "Chapter 1", "page": 1}]',
        encoding="utf-8",
    )

    result = load_bookmark_tree(bookmarks_file, page_offset=27)

    assert result.roots[0].page_number == 27


@pytest.mark.parametrize(
    "payload",
    [
        {"title": "Chapter 1", "page": 0},
        {"title": "Chapter 1", "page": -1},
        {"title": "Chapter 1", "page": "one"},
        {"title": "Chapter 1", "page": 1, "children": {}},
        {"page": 1},
    ],
)
def test_load_bookmark_tree_rejects_invalid_bookmark_values(
    tmp_path: Path,
    payload: dict[str, object],
) -> None:
    bookmarks_file = tmp_path / "bookmarks.json"
    bookmarks_file.write_text(json.dumps([payload]), encoding="utf-8")

    with pytest.raises(ValueError):
        load_bookmark_tree(bookmarks_file)


def test_load_bookmark_tree_skips_page_less_outline_labels(tmp_path: Path) -> None:
    bookmarks_file = tmp_path / "bookmarks.json"
    bookmarks_file.write_text(
        '[{"title": "Chapter 1", "page": 1}, '
        '{"title": "Label without destination"}]',
        encoding="utf-8",
    )

    result = load_bookmark_tree(bookmarks_file)

    assert [node.title for node in result.roots] == ["Chapter 1"]


@pytest.mark.parametrize("payload", [{"title": "not a list"}, "invalid"])
def test_load_bookmark_tree_rejects_invalid_json_root(
    tmp_path: Path,
    payload: object,
) -> None:
    bookmarks_file = tmp_path / "bookmarks.json"
    bookmarks_file.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="root must be an array"):
        load_bookmark_tree(bookmarks_file)