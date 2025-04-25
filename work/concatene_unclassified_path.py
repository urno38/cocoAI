from pathlib import Path

from common.path import TMP_PATH


def concatener_fichiers(fichiers_entree, fichier_sortie):
    """
    Concatène plusieurs fichiers texte en un seul fichier.

    :param fichiers_entree: Liste des chemins des fichiers texte à concaténer.
    :param fichier_sortie: Chemin du fichier où le contenu sera écrit.
    """
    try:
        with open(fichier_sortie, "w", encoding="utf-8") as sortie:
            for fichier in fichiers_entree:
                print(fichier)
                try:
                    with open(fichier, "r", encoding="utf-8") as entree:
                        contenu = entree.read()
                        sortie.write(contenu + "\n")
                except FileNotFoundError:
                    print(f"Le fichier {fichier} n'existe pas et sera ignoré.")
                except IOError as e:
                    print(f"Erreur lors de la lecture du fichier {fichier}: {e}")
    except IOError as e:
        print(f"Erreur lors de l'écriture dans le fichier {fichier_sortie}: {e}")
    print(Path(fichier_sortie).resolve())


# Exemple d'utilisation
fichiers_a_concatener = list(TMP_PATH.glob("*.txt"))
fichier_concatene = "fichier_concatene.txt"
concatener_fichiers(fichiers_a_concatener, fichier_concatene)
