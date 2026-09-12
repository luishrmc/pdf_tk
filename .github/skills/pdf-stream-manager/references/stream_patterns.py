# PDF Stream Manager Patterns

from io import BytesIO

from core.stream_manager import copy_stream, open_pdf_input_bytes_io, rewind_stream


def process_pdf_stream(source_bytes: bytes) -> BytesIO:
    """Process an incoming byte stream safely in memory."""
    with open_pdf_input_bytes_io(source_bytes) as input_stream:
        output_stream = BytesIO()
        copy_stream(input_stream, output_stream)
        return rewind_stream(output_stream)
