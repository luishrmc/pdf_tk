# core/domain_models.py

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .stream_manager import PdfStreamSource


class PDFIndexOutOfBoundsError(ValueError):
    """Raised when a 0-based PDF page index is outside a document."""


class BookmarkNode(BaseModel):
    """Immutable hierarchical bookmark with a strictly 0-based page number."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
    )

    title: str = Field(min_length=1)
    page_number: int = Field(ge=0)
    children: tuple[BookmarkNode, ...] = ()


class BookmarkTree(BaseModel):
    """Immutable PDF bookmark tree whose page numbers are strictly 0-based."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
    )

    roots: tuple[BookmarkNode, ...] = ()


class SliceRange(BaseModel):
    """Inclusive PDF page range using strictly 0-based page indices."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
    )

    start_page: int = Field(ge=0)
    end_page: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_order(self) -> SliceRange:
        """Ensure the 0-based end page is not before the start page."""
        if self.end_page < self.start_page:
            raise ValueError("end_page must be greater than or equal to start_page")
        return self


class BookmarkSection(BaseModel):
    """A flattened bookmark section with a strictly 0-based page range."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
    )

    title: str = Field(min_length=1)
    page_range: SliceRange


class PageInsertionRequest(BaseModel):
    """Immutable PDF page-insertion request using strictly 0-based indices.

    ``insert_index`` identifies the position in the target PDF before which
    source pages are inserted. It may equal the target page count to append
    pages. ``source_range`` is an inclusive 0-based range within the source
    PDF; ``None`` means that all source pages are inserted.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
        arbitrary_types_allowed=True,
    )

    source: PdfStreamSource
    insert_index: int = Field(ge=0)
    source_range: SliceRange | None = None


class InsertOperation(BaseModel):
    """PDF insertion operation with a strictly 0-based insertion index."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
    )

    insert_index: int = Field(ge=0)
