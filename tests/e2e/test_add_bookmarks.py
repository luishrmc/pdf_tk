from __future__ import annotations

from pathlib import Path

import pytest
from pypdf import PdfReader, PdfWriter

from cli.parser import main


def create_synthetic_pdf(path: Path, *, page_count: int) -> None:
    """Create a temporary blank PDF with a deterministic page count."""
    with path.open("wb") as output, PdfWriter() as writer:
        for _ in range(page_count):
            writer.add_blank_page(width=72, height=72)
        writer.write(output)


def invoke_cli(arguments: list[str]):
    """Invoke the Click-based CLI used by the Markdown E2E surface."""
    if not hasattr(main, "name"):
        pytest.skip("Markdown E2E requires the Click-based CLI entry point")
    from click.testing import CliRunner

    return CliRunner().invoke(main, arguments)


def test_add_bookmarks_markdown_e2e(tmp_path: Path) -> None:
    input_pdf = tmp_path / "sample.pdf"
    output_pdf = tmp_path / "output.pdf"
    markdown_file = tmp_path / "bookmarks.md"

    create_synthetic_pdf(input_pdf, page_count=5)
    markdown_file.write_text(
        "# Chapter 1: Overview - 1\n"
        "## Section 1.1: Introduction - 2\n"
        "### Section 1.1.1: Details - 3\n"
        "## Section 1.2: Getting Started - 4\n",
        encoding="utf-8",
    )

    result = invoke_cli(
        [
            "add-bookmarks",
            str(input_pdf),
            str(markdown_file),
            str(output_pdf),
        ]
    )

    assert result.exit_code == 0, result.output
    assert output_pdf.exists()

    reader = PdfReader(output_pdf)
    outline = reader.outline
    assert outline[0].title == "Chapter 1: Overview"
    assert reader.get_destination_page_number(outline[0]) == 0
    assert outline[1][0].title == "Section 1.1: Introduction"
    assert reader.get_destination_page_number(outline[1][0]) == 1
    assert outline[1][1][0].title == "Section 1.1.1: Details"
    assert reader.get_destination_page_number(outline[1][1][0]) == 2
    assert outline[1][2].title == "Section 1.2: Getting Started"
    assert reader.get_destination_page_number(outline[1][2]) == 3


@pytest.mark.parametrize("page_value", ["0", "-1", "not-a-number"])
def test_add_bookmarks_markdown_rejects_invalid_page_values(
    tmp_path: Path,
    page_value: str,
) -> None:
    input_pdf = tmp_path / "sample.pdf"
    output_pdf = tmp_path / "output.pdf"
    markdown_file = tmp_path / "bookmarks.md"

    create_synthetic_pdf(input_pdf, page_count=2)
    markdown_file.write_text(
        f"# Invalid Bookmark - {page_value}\n",
        encoding="utf-8",
    )

    result = invoke_cli(
        [
            "add-bookmarks",
            str(input_pdf),
            str(markdown_file),
            str(output_pdf),
        ]
    )

    assert result.exit_code != 0
    assert "positive 1-based" in result.output.lower()
    assert "traceback" not in result.output.lower()
    assert not output_pdf.exists()
