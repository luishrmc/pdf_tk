from __future__ import annotations

from io import BytesIO

import pytest

from core.stream_manager import (
    copy_stream,
    open_pdf_input,
    open_pdf_output,
    rewind_stream,
)


def test_open_pdf_input_bytes_io_rewinds_without_closing_stream() -> None:
    source = BytesIO(b"pdf data")
    source.seek(len(source.getvalue()))

    with open_pdf_input(source) as stream:
        assert stream is source
        assert stream.tell() == 0
        assert stream.read() == b"pdf data"

    assert not source.closed


def test_open_pdf_output_bytes_io_truncates_and_rewinds() -> None:
    target = BytesIO(b"old data")

    with open_pdf_output(target) as stream:
        assert stream is target
        stream.write(b"new data")

    assert not target.closed
    assert target.tell() == 0
    assert target.read() == b"new data"


def test_rewind_stream_returns_same_stream_at_zero() -> None:
    stream = BytesIO(b"pdf data")
    stream.seek(len(stream.getvalue()))

    result = rewind_stream(stream)

    assert result is stream
    assert result.tell() == 0


def test_copy_stream_copies_in_bounded_chunks() -> None:
    source = BytesIO(b"0123456789")
    destination = BytesIO()

    copy_stream(source, destination, chunk_size=3)

    assert destination.getvalue() == b"0123456789"
    assert not source.closed
    assert not destination.closed


def test_copy_stream_rejects_non_positive_chunk_size() -> None:
    with pytest.raises(ValueError, match="chunk_size"):
        copy_stream(BytesIO(b"data"), BytesIO(), chunk_size=0)
