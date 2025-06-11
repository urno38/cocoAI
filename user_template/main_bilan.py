from cocoAI.bilan import main
from common.folder_tree import get_enseigne_folder_path
from common.identifiers import verify_id
from common.logconfig import LOGGER
from common.path import DATALAKE_PATH, is_directory_empty


def main_user(siret=None):

    if siret is None:
        siret = input("\nEntrer un siret\n")
        verify_id(siret, "siret")

    print("\n-----------")
    print("Interpretation des FEC")
    print("-----------")

    ENSEIGNE_FOLDER = get_enseigne_folder_path(siret)
    FEC_PATH = (
        ENSEIGNE_FOLDER / "REFERENCE_DOCUMENTS" / "DOCUMENTATION_FINANCIERE" / "FEC"
    )

    if is_directory_empty(FEC_PATH):
        LOGGER.info(f"pas de FEC contenu dans {FEC_PATH}")
        LOGGER.info("GAME OVER")

    print(f"fichiers dans le dossier {FEC_PATH}")
    for fichier in FEC_PATH.iterdir():
        if fichier.is_file():
            print("- ", fichier.name)
    print("\n")

    LOGGER.info("je les interprete\n")

    path_list = [fichier for fichier in FEC_PATH.iterdir()]

    refyear = input("annee de reference (2023 par ex)\t")
    curyear = input("annee courante (2024 par ex)\t")
    print("\n")

    main(
        path_list,
        refyear=int(refyear),
        curyear=int(curyear),
        xlsx_path=ENSEIGNE_FOLDER
        / "COMMERCIAL_DOCUMENTS"
        / f"Bilan_detaille_{int(refyear)}_{int(curyear)}.xlsx",
    )

    return


if __name__ == "__main__":
    main_user()

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

    # DEI_FRATELLI_PATH = (
    #     DATALAKE_PATH
    #     / r"JRI_PYRAMIDES_839951027\CAFFE_DEI_FRATELLI\REFERENCE_DOCUMENTS\DOCUMENTATION_FINANCIERE\FEC"
    # )

    # path_list = [
    #     DEI_FRATELLI_PATH / "839951027FEC20231231.txt",
    #     DEI_FRATELLI_PATH / "839951027FEC20241231.txt",
    # ]

    # main(path_list, refyear=2023, curyear=2024)
