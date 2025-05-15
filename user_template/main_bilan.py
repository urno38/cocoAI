from cocoAI.bilan import main
from common.FEC import extract_df_FEC
from common.path import COMMERCIAL_DOCUMENTS_PATH, DATALAKE_PATH, rapatrie_file

###########################################
# cas CHIEN QUI FUME

# CHIEN_QUI_FUME_PATH = (
#     COMMERCIAL_DOCUMENTS_PATH
#     / "2 - DOSSIERS à l'ETUDE"
#     / "1 - FONDS DE COMMERCES"
#     / "CHIEN QUI FUME (Le) - 75001 PARIS - 33 Rue du PONT-NEUF"
#     / "3. DOCUMENTATION FINANCIÈRE"
# )

# # je rapatrie les fichiers qui m'interessent
# # la routine copie les fichiers dans le dossier data
# # ne pas hesiter à mettre des chemin qui pointent vers le ONEdrive de comptoirs et commerces, ils seront copiés vers data avant d'être interprétés
# rapatrie_file(CHIEN_QUI_FUME_PATH / "2022 - GALLA - GL.xlsx")
# rapatrie_file(CHIEN_QUI_FUME_PATH / "2023 - GALLA - GL.xlsx")
# [rapatrie_file(f) for f in CHIEN_QUI_FUME_PATH.glob("*GALLA - BILAN*.pdf")]


# # mettre ici tous les fichiers xls qui sont concernés par l'analyse pour les comptes de résultats

# excel_path_list = [
#     CHIEN_QUI_FUME_PATH / "2022 - GALLA - GL.xlsx",
#     CHIEN_QUI_FUME_PATH / "2023 - GALLA - GL.xlsx",
# ]

# main(excel_path_list)


###########################################
# cas DEI FRATELLI

DEI_FRATELLI_PATH = (
    DATALAKE_PATH
    / r"JRI_PYRAMIDES_839951027\CAFFE_DEI_FRATELLI\REFERENCE_DOCUMENTS\DOCUMENTATION_FINANCIERE\FEC"
)


path_list = [
    DEI_FRATELLI_PATH / "839951027FEC20231231.txt",
    DEI_FRATELLI_PATH / "839951027FEC20241231.txt",
]


main(path_list, refyear=2023, curyear=2024)
