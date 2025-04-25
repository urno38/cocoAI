import glob
import os

from common.path import TMP_PATH


def concatener_fichiers_texte(dossier, fichier_sortie):
    # Liste tous les fichiers texte dans le dossier
    fichiers_texte = glob.glob(os.path.join(dossier, "*path.txt"))

    with open(fichier_sortie, "w", encoding="utf-8") as sortie:
        for fichier in fichiers_texte:
            if os.path.getsize(fichier) > 0:  # Vérifie si le fichier n'est pas vide
                with open(fichier, "r", encoding="utf-8") as f:
                    contenu = f.read()
                    sortie.write(contenu + "\n")

    print(f"Les fichiers ont été concaténés dans {fichier_sortie}")


# Exemple d'utilisation
dossier = TMP_PATH
fichier_sortie = "fichier_concatene.txt"
concatener_fichiers_texte(dossier, fichier_sortie)
concatener_fichiers_texte(dossier, fichier_sortie)
