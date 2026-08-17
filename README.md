# PDF Slicer

A modular Python CLI tool to slice PDF files by **page range** or **bookmarks**, and to **inject bookmark hierarchies** into PDF files.

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

### Command 3 — Add Bookmarks from JSON

```bash
python main.py add-bookmarks <document> <bookmarks_file> <output> [--offset OFFSET]

```

**Example:** Add bookmarks to `book.pdf` using a JSON outline file:

```bash
python main.py add-bookmarks book.pdf bookmarks.json ./output/book_with_bookmarks.pdf

```

**Example:** Add bookmarks with a page offset (e.g., if page 1 of the body text begins at PDF sheet 28):

```bash
python main.py add-bookmarks book.pdf bookmarks.json ./output/book_with_bookmarks.pdf --offset 27

```

#### Bookmarks JSON Format

The JSON file supports arbitrary nesting using the `children` key and 1-based page numbers:

```json
[
  {
    "title": "Chapter 1: Introduction",
    "page": 1,
    "children": [
      {
        "title": "1.1 Background",
        "page": 2
      },
      {
        "title": "1.2 Device Technologies",
        "page": 5,
        "children": [
          {
            "title": "1.2.1 Fabrication of an IC",
            "page": 8
          }
        ]
      }
    ]
  },
  {
    "title": "Chapter 2: Overview",
    "page": 23
  }
]

```

---

## Project Structure

```
pdf_slicer/
├── main.py                     # CLI entry point (argparse)
├── commands/
│   ├── add_bookmarks.py        # Add bookmarks/outline logic
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
