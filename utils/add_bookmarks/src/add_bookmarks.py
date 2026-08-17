import json
from pypdf import PdfReader, PdfWriter

def add_bookmarks_recursively(writer, items, offset=0, parent=None):
    for item in items:
        title = item["title"]
        # Convert 1-based printed page number to 0-based PDF page index
        target_page_index = (item["page"] - 1) + offset
        
        # Ensure page index is within PDF bounds
        if target_page_index < len(writer.pages):
            bookmark = writer.add_outline_item(
                title=title,
                page_number=target_page_index,
                parent=parent
            )
            # Add nested bookmarks if present
            if "children" in item and item["children"]:
                add_bookmarks_recursively(writer, item["children"], offset=offset, parent=bookmark)

def process_pdf(input_pdf_path, output_pdf_path, bookmarks_json_path, page_offset=0):
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    # Copy all pages from the original PDF
    for page in reader.pages:
        writer.add_page(page)

    # Load bookmark structure
    with open(bookmarks_json_path, "r", encoding="utf-8") as f:
        bookmarks = json.load(f)

    # Insert outlines
    add_bookmarks_recursively(writer, bookmarks, offset=page_offset)

    # Save modified PDF
    with open(output_pdf_path, "wb") as f_out:
        writer.write(f_out)

    print(f"Successfully wrote bookmarks to: {output_pdf_path}")

if __name__ == "__main__":
    # Example: If Chapter 1 is labeled 'Page 1' but appears on PDF sheet 10, offset = 9
    process_pdf(
        input_pdf_path="output/Hardware_Design_Using_VHDL_Coding_Pong_Chu.pdf",
        output_pdf_path="output/book_with_bookmarks.pdf",
        bookmarks_json_path="output/bookmarks.json",
        page_offset=27
    )