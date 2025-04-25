from pathlib import Path
from pdf2image import convert_from_path
import pytesseract
import pandas as pd
import os

pytesseract.pytesseract.tesseract_cmd = r"D:\Program Files\Tesseract-OCR\tesseract.exe"

# Spécifiez le chemin de votre fichier PDF
pdf_path = Path.cwd() / "data/CSV_2022_test_tableauv3.pdf"

# Dossier temporaire pour stocker les images
temp_image_folder = "temp_images"
print(os.path.realpath(temp_image_folder))
os.makedirs(temp_image_folder, exist_ok=True)

# Fichier Excel de sortie
output_excel = "output.xlsx"


# Liste pour stocker les données extraites
extracted_data = []

# Convertir les pages du PDF en images
print("Conversion du PDF en images...")
images = convert_from_path(pdf_path, dpi=300)

for i, image in enumerate(images):
    # Nom de l'image temporaire
    image_path = os.path.join(temp_image_folder, f"page_{i + 1}.png")
    image.save(image_path, "PNG")

    # Extraction de texte à l'aide de Tesseract
    print(f"Extraction de texte depuis : {image_path}")
    text = pytesseract.image_to_string(image)

    with open(f"output_page_{i}.txt", "w", encoding="utf8") as f:
        f.write(text)
