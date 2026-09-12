from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

from cli.parser import main


def test_main_slice_range_routes_terminal_arguments_to_controller() -> None:
    input_file = Path("input.pdf")
    output_file = Path("output.pdf")
    argv = [
        "pdf-tk",
        "slice-range",
        str(input_file),
        str(output_file),
        "2",
        "4",
    ]

    with patch.object(sys, "argv", argv), patch(
        "cli.parser.slice_range_to_file",
    ) as slice_range_to_file:
        exit_code = main()

    assert exit_code == 0
    slice_range_to_file.assert_called_once_with(
        input_file=input_file,
        output_file=output_file,
        start_page=2,
        end_page=4,
    )