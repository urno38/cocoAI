from pathlib import Path
import fitz  # PyMuPDF
import pandas as pd


# do only work with pdfs coming from excel

# Spécifiez le chemin de votre fichier PDF
pdf_path = Path.cwd() / "data/CSV_2022_test_tableauv3.pdf"


# Nom du fichier Excel de sortie
excel_output = "output.xlsx"

# Liste pour stocker les données extraites
tables = []

# Charger le fichier PDF
try:
    pdf_document = fitz.open(pdf_path)
    print("Extraction en cours...")

    # Parcourir toutes les pages
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)  # Charger une page
        text = page.get_text("text")  # Extraire le texte brut
        lines = text.split("\n")  # Découper le texte en lignes

        # Ajouter les lignes dans une liste structurée (simple exemple)
        data = [line.split() for line in lines]
        tables.extend(data)  # Ajouter les données de la page aux tables

    # Fermer le document PDF
    pdf_document.close()

    # Convertir les données extraites en DataFrame
    df = pd.DataFrame(tables)

    # Sauvegarder dans un fichier Excel
    df.to_excel(excel_output, index=False, header=False)
    print(f"Données sauvegardées dans : {excel_output}")

except Exception as e:
    print(f"Une erreur s'est produite : {e}")
