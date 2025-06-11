import os
import sys

from common.identifiers import verify_id
from user_template import main_archive_siret, main_bilan, main_global

print(
    """
--------      
cocoAI - Ensemble de scripts pour Comptoirs et Commerces
L. Volat juin 2025
--------
      """
)


siret = input("Entrez un siret\n")


verify_id(siret, kind="siret")

print("\n")

print("pour classer les fichiers d'un dossier, taper 1")
print("pour interpréter un FEC en tant que bilan comptable, taper 2")
print("pour produire un memorandum, taper 3")

print("\n")

choice = input("Votre choix\n")

match choice:
    case "1":
        main_archive_siret.main_user(siret)
    case "2":
        main_bilan.main_user(siret)
    case "3":
        main_global.main_user(siret)
    case _:
        print("Mauvais choix, réexécuter le script en faisant dans ce terminal")
        print("python3 " + os.path.abspath(sys.argv[0]))
