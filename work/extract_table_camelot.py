import camelot

# NON FONCTIONNEL

# Chemin du fichier PDF
pdf_path = "votre_fichier.pdf"

# Dossier ou fichiers Excel de sortie
output_folder = "tables_output"

# Extraction des tableaux
try:
    print("Extraction des tableaux en cours...")
    tables = camelot.read_pdf(
        pdf_path, pages="all", flavor="stream"
    )  # Utilisez 'stream' ou 'lattice'

    # Vérifier si des tableaux ont été trouvés
    if tables:
        print(f"{len(tables)} tableau(x) détecté(s).")

        # Sauvegarder chaque tableau dans un fichier Excel distinct
        for i, table in enumerate(tables):
            output_file = f"{output_folder}/table_{i + 1}.xlsx"
            table.to_excel(output_file)
            print(f"Tableau {i + 1} sauvegardé sous le nom : {output_file}")
    else:
        print("Aucun tableau trouvé dans le PDF.")

except Exception as e:
    print(f"Une erreur s'est produite : {e}")
