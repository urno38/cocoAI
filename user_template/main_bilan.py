from cocoAI.bilan import main
from common.path import COMMERCIAL_DOCUMENTS_PATH, rapatrie_file

CHIEN_QUI_FUME_PATH = (
    COMMERCIAL_DOCUMENTS_PATH
    / "2 - DOSSIERS à l'ETUDE"
    / "CHIEN QUI FUME (Le) - 75001 PARIS - 33 Rue du PONT-NEUF"
    / "3. DOCUMENTATION FINANCIÈRE"
)

# je rapatrie les fichiers qui m'interessent
# la routine copie les fichiers dans le dossier data
# ne pas hesiter à mettre des chem
# in qui pointent vers le ONEdrive de comptoirs et commerces, ils seront copiés vers data avant d'être interprétés
rapatrie_file(CHIEN_QUI_FUME_PATH / "2022 - GALLA - GL.xlsx")
rapatrie_file(CHIEN_QUI_FUME_PATH / "2023 - GALLA - GL.xlsx")
[rapatrie_file(f) for f in CHIEN_QUI_FUME_PATH.glob("*GALLA - BILAN*.pdf")]


# mettre ici tous les fichiers xls qui sont concernés par l'analyse pour les comptes de résultats

excel_path_list = [
    CHIEN_QUI_FUME_PATH / "2022 - GALLA - GL.xlsx",
    CHIEN_QUI_FUME_PATH / "2023 - GALLA - GL.xlsx",
]

main(excel_path_list, test=True)
