# cli/adapters.py

from __future__ import annotations

from core.domain_models import SliceRange


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