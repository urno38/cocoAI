from cocoAI.compte_de_resultats import main
from common.path import COMMERCIAL_ONE_DRIVE_PATH, rapatrie_file

CHIEN_QUI_FUME_PATH = (
    COMMERCIAL_ONE_DRIVE_PATH
    / "2 - DOSSIERS à l'ETUDE"
    / "CHIEN QUI FUME (Le) - 75001 PARIS - 33 Rue du PONT-NEUF"
    / "3. DOCUMENTATION FINANCIÈRE"
)

# je rapatrie les fichiers qui m'interessent
rapatrie_file()


# mettre ici tous les fichiers xls qui sont concernés par l'analyse pour les comptes de résultats
# ne pas hesiter à mettre des chemin qui pointent vers le ONEdrive de comptoirs et commerces, ils seront copiés vers data avant d'être interprétés


excel_path_list = [
    (
        COMMERCIAL_ONE_DRIVE_PATH
        / "2 - DOSSIERS à l'ETUDE"
        / "CHIEN QUI FUME (Le) - 75001 PARIS - 33 Rue du PONT-NEUF"
        / "3. DOCUMENTATION FINANCIÈRE"
        / "2022 - GALLA - GL.xlsx"
    ),
    (
        COMMERCIAL_ONE_DRIVE_PATH
        / "2 - DOSSIERS à l'ETUDE"
        / "CHIEN QUI FUME (Le) - 75001 PARIS - 33 Rue du PONT-NEUF"
        / "3. DOCUMENTATION FINANCIÈRE"
        / "2023 - GALLA - GL.xlsx"
    ),
]


main(excel_path_list)
