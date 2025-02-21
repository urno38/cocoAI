import io
import os
from pathlib import Path

import fitz
import pytesseract
import requests
from PIL import Image

from common.logconfig import LOGGER, configure_logger
from common.path import DATA_PATH, TESSERACT_EXE_PATH, create_parent_directory

if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = str(TESSERACT_EXE_PATH)


def pdf_to_text(pdf_path):
    # Ouvrir le fichier PDF
    LOGGER.info("convert pdf to text")
    LOGGER.info(f"{pdf_path}")

    pdf_document = fitz.open(pdf_path)
    text = ""

    LOGGER.debug(f"{len(pdf_document)} pages")

    # Parcourir chaque page du PDF
    for page_num in range(len(pdf_document)):

        LOGGER.debug(f"page {page_num}")

        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()

        # Convertir l'image en mode RGB
        image = Image.open(io.BytesIO(pix.tobytes()))

        # Utiliser pytesseract pour effectuer l'OCR sur l'image
        page_text = pytesseract.image_to_string(image)
        text += page_text + "\n"

    LOGGER.info("Scan completed")
    return text


def convert_pdf_to_ascii(pdf_path, output_ascii_path=None):

    if output_ascii_path is None:
        output_ascii_path = pdf_path.with_suffix(".txt")

    if not output_ascii_path.exists():
        text = pdf_to_text(pdf_path)
        with open(output_ascii_path, "w", encoding="utf-8") as f:
            f.write(text)
        LOGGER.info(f"pdf converted to {output_ascii_path}")
    else:
        with open(output_ascii_path, encoding="utf-8") as f:
            text = "\n".join(f.readlines())
        LOGGER.info(f"{output_ascii_path.resolve()} loaded")

    return output_ascii_path, text


def extract_images_from_pdf(pdf_path, output_dir):
    """
    Extract all images from a PDF file and save them to the specified output directory.

    Args:
        pdf_path (str): Path to the PDF file
        output_dir (str): Directory where images will be saved

    Returns:
        list: List of paths to saved images
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Open the PDF
    pdf_document = fitz.open(pdf_path)
    saved_images = []

    # Iterate through each page
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]

        # Get all images on the page
        image_list = page.get_images()

        # Process each image
        for img_index, img in enumerate(image_list):
            # Get the image data
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]

            # Get image extension
            ext = base_image["ext"]

            # Generate output filename
            image_filename = f"page{page_num + 1}_img{img_index + 1}.{ext}"
            image_path = os.path.join(output_dir, image_filename)

            # Save the image
            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)

            # Open with PIL for potential post-processing
            with Image.open(io.BytesIO(image_bytes)) as img:
                # Save with PIL to ensure proper format
                img.save(image_path, format=ext.upper())

            saved_images.append(image_path)

    pdf_document.close()
    return saved_images


def download_pdf(url, save_path):
    LOGGER.debug(url)
    response = requests.get(url)
    create_parent_directory(save_path)
    if response.status_code == 200:
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        LOGGER.info(f"PDF downloaded successfully: {save_path}")
    elif response.status_code == 404:
        LOGGER.debug(
            "Site de la mairie de Paris en maintenance, pas possible de télécharger le pdf"
        )
    else:
        LOGGER.info(response)
        LOGGER.error(f"Failed to download PDF. Status code: {response.status_code}")


# Example usage
if __name__ == "__main__":

    logger = configure_logger()
    # test extraction images d'un pdf
    # pdf_path = r"c:\Users\lvolat\Downloads\328311052_004.pdf"
    # output_dir = "extracted_images2"

    # try:
    #     extracted_images = extract_images_from_pdf(pdf_path, output_dir)
    #     LOGGER.debug(f"Successfully extracted {len(extracted_images)} images:")
    #     for img_path in extracted_images:
    #         LOGGER.debug(f"- {img_path}")
    # except Exception as e:
    #     LOGGER.error(f"Error extracting images: {str(e)}")

    # test telechargement pdf
    # pdf_url = "https://affichette-commerce.paris.fr/2015/Q_59/595230061%20002.pdf"  # Replace with the actual PDF URL
    # save_location = (
    #     WORK_PATH / "downloaded_pdf" / "download.pdf"
    # )  # Change the save location if needed
    # create_parent_directory(save_location)
    # download_pdf(pdf_url, save_location)

    # test scan de pdf
    pdf_path = list(DATA_PATH.glob("*GILBERTE*/*BAIL*pdf"))[0]
    output_path, text = convert_pdf_to_ascii(pdf_path, Path("result.txt"))
