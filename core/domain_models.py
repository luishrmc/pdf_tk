# core/domain_models.py

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


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
    """Inclusive PDF page range using strictly 0-based start and end indices."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
    )

    start_page: int = Field(ge=0)
    end_page: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_order(self) -> SliceRange:
        """Ensure the 0-based end index is not before the start index."""
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

class InsertOperation(BaseModel):
    """PDF insertion request with a strictly 0-based insertion index."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
    )

    insert_index: int = Field(ge=0)