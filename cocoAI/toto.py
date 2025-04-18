import os
from pathlib import Path


def calculer_taille_fichier_mo(chemin_fichier):
    try:
        taille_octets = os.path.getsize(chemin_fichier)
        taille_mo = taille_octets / (1024 * 1024)  # Conversion en mégaoctets
        return taille_mo
    except OSError as e:
        return f"Erreur : {e}"


# Exemple d'utilisation
chemin_fichier = Path(
    r"C:\Users\lvolat\Documents\cocoAI\data\1_DOSSIERS_EN_COURS_DE_SIGNATURE\DEI_FRATELLI_75001_PARIS_10_Rue_des_PYRAMIDES\11._PHOTOS\PHOTOS_ET_PLANS.pdf"
)
taille_fichier_mo = calculer_taille_fichier_mo(chemin_fichier)
print(f"La taille du fichier est : {taille_fichier_mo:.2f} Mo")
print(f"La taille du fichier est : {taille_fichier_mo:.2f} Mo")
