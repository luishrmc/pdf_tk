# PDF Slicer

A modular Python CLI tool to slice PDF files by **page range** or **bookmarks**.

## Requirements

```bash
pip install -r requirements.txt
```

## Usage

### Command 1 — Slice by Page Range

```bash
python main.py slice-range <document> <output_dir> <start_page> <end_page>
```

**Example:** Extract pages 5 to 20 from `book.pdf`:

```bash
python main.py slice-range book.pdf ./output 5 20
```

---

### Command 2 — Slice by Bookmarks

```bash
python main.py slice-bookmarks <document> <output_dir> [--level LEVEL]
```

**Example:** Slice `book.pdf` into top-level chapters:

```bash
python main.py slice-bookmarks book.pdf ./chapters
```

**Example:** Slice by second-level sections (sub-chapters):

```bash
python main.py slice-bookmarks book.pdf ./sections --level 1
```

---

## Project Structure

```
pdf_slicer/
├── main.py                     # CLI entry point (argparse)
├── commands/
│   ├── slice_range.py          # Slice by page range logic
│   └── slice_bookmarks.py      # Slice by bookmarks/outline logic
├── utils/
│   ├── logger.py               # Shared logger factory
│   └── pdf_utils.py            # Shared helpers (validation, sanitize, mkdir)
└── README.md
```

## Logging

All operations are logged to **stdout** with timestamps and severity levels.
Use `--level` to inspect available bookmark depths before slicing.
