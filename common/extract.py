import sys
from pprint import pprint

import fitz
import pytesseract

from common.logconfig import LOGGER
from common.path import (
    DATA_PATH,
    TESSERACT_EXE_PATH,
    WORK_PATH,
    create_parent_directory,
)

pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE_PATH
from PIL import Image


def extract_pdf(pdf_path, output_path, password=None):
    create_parent_directory(output_path)
    # Ouvrir le fichier PDF
    pdf_document = fitz.open(pdf_path)  # Ouvrir le fichier PDF
    # Parcourir chaque page du PDF
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        text = pytesseract.image_to_string(img)  # 'fra' pour le français
        # text = pytesseract.image_to_string(img, lang="fra")  # 'fra' pour le français
        LOGGER.info(f"Page {page_num + 1}:\n{text}\n")
        page_path = output_path / f"page_{page_num + 1}.txt"
        with open(page_path, "w", encoding="utf-8") as f:
            f.write(f"Page {page_num + 1}:\n{text}\n\n")
    # Fermer le document PDF
    pdf_document.close()
    return


if __name__ == "__main__":
    # Chemin vers le fichier PDF
    PDF_FOLDER_PATH = (
        DATA_PATH
        / "CHIEN QUI FUME (Le) - 75001 PARIS - 33 Rue du PONT-NEUF"
        / "1. DOSSIER AFFAIRE ACC - [SOCIÉTÉ]"
    )
    pdf_path = list(PDF_FOLDER_PATH.glob("*.pdf"))[0]
    # logging.info(DATA_PATH)
    LOGGER.info(pdf_path)
    LOGGER.info(f"Extraction du texte du fichier PDF: {pdf_path}")
    extract_pdf(pdf_path, WORK_PATH / "output")
