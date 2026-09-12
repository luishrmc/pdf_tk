from __future__ import annotations

import pytest

from cli.adapters import to_slice_range


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