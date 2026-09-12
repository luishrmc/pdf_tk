from __future__ import annotations

from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from cli.controllers import slice_range_to_file
from core.domain_models import SliceRange


def test_slice_range_to_file_passes_memory_stream_and_zero_based_range(
    tmp_path: Path,
) -> None:
    input_file = tmp_path / "input.pdf"
    output_file = tmp_path / "output.pdf"
    input_file.write_bytes(b"synthetic input PDF")
    sliced_stream = BytesIO(b"synthetic sliced PDF")

    with patch(
        "cli.controllers.slice_pdf_by_range",
        return_value=sliced_stream,
    ) as slice_pdf:
        slice_range_to_file(
            input_file=input_file,
            output_file=output_file,
            start_page=2,
            end_page=4,
        )

    slice_pdf.assert_called_once()
    source_stream, page_range = slice_pdf.call_args.args
    assert isinstance(source_stream, BytesIO)
    assert source_stream.getvalue() == b"synthetic input PDF"
    assert page_range == SliceRange(start_page=1, end_page=3)
    assert output_file.read_bytes() == b"synthetic sliced PDF"