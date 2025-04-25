from pathlib import Path
from tabula import read_pdf

# Spécifiez le chemin de votre fichier PDF
pdf_path = Path.cwd() / "data/CSV_2022_test_tableauv3.pdf"

# Extraction des tableaux du fichier PDF
# Assurez-vous que votre fichier PDF contient bien des données tabulaires
try:
    print("Extraction des données...")
    tables = read_pdf(pdf_path, pages="all", multiple_tables=True, stream=True)
    print(tables)
    # Vérifiez si des tableaux ont été extraits
    if tables:
        for i, table in enumerate(tables):
            # Sauvegarder chaque tableau en tant que fichier Excel
            output_file = f"table_{i + 1}.xlsx"
            table.to_excel(output_file, index=False)
            print(f"Tableau {i + 1} sauvegardé sous le nom : {output_file}")
    else:
        print("Aucun tableau trouvé dans le fichier PDF.")
except Exception as e:
    print(f"Une erreur s'est produite : {e}")
