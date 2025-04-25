from common.path import create_parent_directory
import fitz  # PyMuPDF


def extract_section_from_pdf(pdf_path, output_path, target_text):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)

    # Iterate through each page to find the target text
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text_instances = page.search_for(target_text)

        # Check if the target text is found on this page
        if text_instances:
            # Assuming the first instance is the one we want
            text_instance = text_instances[0]

            # Correctly access the coordinates of the Rect object
            x0, y0, x1, y1 = (
                text_instance.x0,
                text_instance.y0,
                text_instance.x1,
                text_instance.y1,
            )

            # Define a region to extract (adjust as necessary)
            # Extend the region to include the table or image below the text
            region_x0 = x0
            region_y0 = y0
            region_x1 = page.rect.x1  # Right edge of the page
            region_y1 = page.rect.y1  # Bottom edge of the page

            # Crop the page to the defined region
            page.set_cropbox((region_x0, region_y0, region_x1, region_y1))

            # Create a new PDF with just this page
            new_pdf = fitz.open()
            new_pdf.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)
            new_pdf.save(output_path)
            print(f"Extracted section saved to {output_path}")
            return

    print("Target text not found in the PDF.")


# Example usage
from pathlib import Path

# Example usage
pdf_path = Path(r"C:\Users\lvolat\Downloads\328311052_004.pdf")
output_path = Path("output/cropped_pdf.pdf")
create_parent_directory(output_path)
target_text = "Emplacement indicatif des installations autorisées"
extract_section_from_pdf(pdf_path, output_path, target_text)
