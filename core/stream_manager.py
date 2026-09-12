# core/stream_manager.py

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from io import BytesIO
from pathlib import Path
from typing import BinaryIO

type PdfStreamSource = Path | BytesIO
type PdfStreamTarget = Path | BytesIO


@contextmanager
def open_pdf_input(source: PdfStreamSource) -> Iterator[BinaryIO]:
    """Yield a seekable PDF input stream without loading the document into memory.

    Path inputs are opened in binary read mode and closed when the context exits.
    BytesIO inputs are rewound before use and remain owned by the caller.
    """
    if isinstance(source, BytesIO):
        source.seek(0)
        yield source
        return

    with source.open("rb") as stream:
        yield stream


@contextmanager
def open_pdf_output(target: PdfStreamTarget) -> Iterator[BinaryIO]:
    """Yield a seekable PDF output stream without taking ownership of BytesIO.

    Path inputs are opened in binary write mode and closed when the context exits.
    BytesIO inputs are truncated and rewound before writing, then rewound for
    reading after the context exits. The caller retains ownership of BytesIO.
    """
    if isinstance(target, BytesIO):
        target.seek(0)
        target.truncate()
        yield target
        target.seek(0)
        return

    with target.open("wb") as stream:
        yield stream


def rewind_stream(stream: BinaryIO) -> BinaryIO:
    """Rewind a seekable PDF stream to byte offset zero and return it."""
    stream.seek(0)
    return stream


def copy_stream(
    source: BinaryIO,
    destination: BinaryIO,
    *,
    chunk_size: int = 1024 * 1024,
) -> None:
    """Copy a PDF stream incrementally using bounded memory.

    The function must not call ``read()`` without a size argument and must
    preserve stream ownership for both caller-provided streams.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    while chunk := source.read(chunk_size):
        destination.write(chunk)
