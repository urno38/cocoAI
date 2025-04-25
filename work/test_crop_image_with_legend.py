from common.path import create_parent_directory
import fitz  # PyMuPDF
from PIL import Image, ImageChops
import io


def trim_image(image):
    """Trim the white borders from an image."""
    bg = Image.new(image.mode, image.size, (255, 255, 255))
    diff = ImageChops.difference(image, bg)
    bbox = diff.getbbox()
    if bbox:
        return image.crop(bbox)
    return image  # Return the original image if no white border is found


def crop_image_from_pdf(pdf_path, output_path):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)

    # Iterate through each page to find the image
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        images = page.get_images(full=True)

        for img_index, img in enumerate(images):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]

            # Load the image using Pillow
            image = Image.open(io.BytesIO(image_bytes))

            # Convert image to RGB if it's not
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")

            # Trim the white borders while preserving content
            trimmed_image = trim_image(image)

            # Save the trimmed image
            trimmed_image.save(output_path)
            print(f"Trimmed image saved to {output_path}")
            return  # Exit after processing the first image


# Example usage
from pathlib import Path

pdf_path = Path(r"C:\Users\lvolat\Downloads\328311052_004.pdf")
output_folder = Path("output/cropped_image.png")
create_parent_directory(output_folder)
crop_image_from_pdf(pdf_path, output_folder)
