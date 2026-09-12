# core/domain_models.py

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BookmarkNode(BaseModel):
    """Immutable PDF bookmark node with a 0-based destination page index."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
    )

    title: str = Field(min_length=1)
    page_index: int = Field(ge=0)
    children: tuple[BookmarkNode, ...] = ()

    
class BookmarkTree(BaseModel):
    """Immutable PDF bookmark tree whose destination indices are 0-based."""

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


class InsertOperation(BaseModel):
    """PDF insertion request with a strictly 0-based insertion index."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        strict=True,
    )

    insert_index: int = Field(ge=0)