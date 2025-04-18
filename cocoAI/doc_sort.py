import os
import shutil
from collections import defaultdict
from pathlib import Path
from typing import List

import pandas as pd

from cocoAI.company import get_infos_from_a_siret
from cocoAI.folder_tree import (
    create_complete_folder_tree,
    get_df_folder_possibles,
    get_entreprise_folder,
)
from common.identifiers import get_etablissement_name, pick_id
from common.logconfig import LOGGER
from common.path import (
    COMMERCIAL_DOCUMENTS_PATH,
    COMMON_PATH,
    DATALAKE_PATH,
    TMP_PATH,
    WORK_PATH,
    calculer_taille_fichier_mo,
    is_photo,
    is_video,
    make_unix_compatible,
    rapatrie_file,
)
from common.pdf_document import (
    get_new_location_dictionary_path,
    process_file_by_Mistral_OCR,
)


def check_all_documents_sorted(etablissement_name):
    LOGGER.info(
        f"check if all the documents from {etablissement_name} are sorted and moved"
    )
    siret = pick_id(make_unix_compatible(etablissement_name), kind="siret")
    entreprise_name, etablissement = get_infos_from_a_siret(siret)
    dest_folder_path = get_entreprise_folder(siret[:-5])
    source_folder_path = get_source_folder_path(etablissement_name)

    unclassified_paths = []
    for file in source_folder_path.rglob("*"):
        if (
            file.is_file()
            and len(list(dest_folder_path.rglob(make_unix_compatible(file.name)))) == 0
        ):
            unclassified_paths.append(file)
            LOGGER.debug(f"{file} has not been sorted")

    return unclassified_paths


def classify_paths_by_parent(paths):
    """
    Classe les chemins selon leur dossier parent.

    :param paths: Liste de chemins Path à classer.
    :return: Dictionnaire avec les dossiers parents comme clés et les chemins correspondants comme valeurs.
    """
    classified_paths = defaultdict(list)

    for path in paths:
        parent = path.parent
        classified_paths[parent].append(path)

    return dict(classified_paths)


def write_paths_to_file(paths_list: List[Path], summary_file_path: Path):
    """
    Écrit les chemins classés dans un fichier texte.

    :param classified_paths: Dictionnaire de chemins classés.
    :param file_path: Chemin du fichier où écrire les chemins.
    """
    with open(summary_file_path, "w", encoding="utf-8") as file:
        for parent, files in paths_list.items():
            file.write(f"Dossier: {parent}\n")
            for file_path in files:
                file.write(f"  - {file_path.name}\n")

    LOGGER.info(f"List written in {summary_file_path.resolve()}")


def classify_pdf_document(enseigne_dest_folder, doc_new_path):
    ocr_response = process_file_by_Mistral_OCR(doc_new_path)
    location_dict = get_new_location_dictionary_path(doc_new_path, ocr_response)
    LOGGER.debug(location_dict)
    path_list = []
    for key, value in location_dict.items():
        if value:
            potential_path = enseigne_dest_folder / "REFERENCE_DOCUMENTS"
            for el in key.split("/"):
                potential_path = potential_path / make_unix_compatible(el)
            path_list.append(potential_path / doc_new_path.name)

    return path_list


# def classify_xlsx_document(dest_folder, xlsx_new_path):
#     # je decide d analyser la premiere sheet du xlsx, la convertir en csv et donner a manger a mistral
#     # de cette manière, j ai rapidement l info que je veux

#     # csv_path = xlsx_new_path.with_suffix(".csv")
#     # pd.read_excel(xlsx_new_path).to_csv(csv_path)
#     # ocr_response = process_file_by_Mistral_OCR(csv_path)
#     # location_dict = get_new_location_dictionary_path(csv_path, ocr_response)

#     ocr_response = process_file_by_Mistral_OCR(xlsx_new_path)
#     location_dict = get_new_location_dictionary_path(xlsx_new_path, ocr_response)

#     path_list = []
#     for key, value in location_dict.items():
#         if value:
#             potential_path = (
#                 dest_folder
#                 / make_unix_compatible(etablissement_name)
#                 / "REFERENCE_DOCUMENTS"
#             )
#             for el in key.split("/"):
#                 potential_path = potential_path / make_unix_compatible(el)
#             path_list.append(potential_path / xlsx_new_path.name)

#     return path_list


# def get_etablissement_name(doc_new_path):
#     tmpdf = pd.read_csv(list(COMMON_PATH.glob("*folder*csv"))[0])
#     for folder in tmpdf["folder"].values:
#         if make_unix_compatible(folder) in str(doc_new_path):
#             return make_unix_compatible(folder)


def classify_one_document(doc_path, siret):

    # LOGGER.debug(f"lets classify {doc_path}")

    enseigne_dest_folder = create_complete_folder_tree(siret)

    doc_new_path = rapatrie_file(doc_path)
    del doc_path  # securite pour eviter de toucher ulterieurement au fichier d'origine

    if "TEASER" in doc_new_path.name or "teaser" in doc_new_path.name:
        # Cas du teaser fait par comptoirs et commerces
        path_list = [
            (
                enseigne_dest_folder
                / "COMMERCIAL_DOCUMENTS"
                / make_unix_compatible(doc_new_path.name)
            )
        ]
    elif (
        "KBIS" in doc_new_path.name
        or "kbis" in doc_new_path.name
        or "K-BIS" in doc_new_path.name
        or "k-bis" in doc_new_path.name
        or "K-Bis" in doc_new_path.name
    ):
        # Cas du teaser fait par comptoirs et commerces
        path_list = [
            (
                enseigne_dest_folder
                / "REFERENCE_DOCUMENTS"
                / "JURIDIQUE_CORPORATE"
                / "K BIS - INSEE - STATUTS"
                / make_unix_compatible(doc_new_path.name)
            )
        ]
    elif (
        "liasse" in doc_new_path.name
        or "Liasse" in doc_new_path.name
        or "fiscale" in doc_new_path.name
        or "Fiscale" in doc_new_path.name
    ):
        path_list = [
            (
                enseigne_dest_folder
                / "REFERENCE_DOCUMENTS"
                / "DOCUMENTATION_FINANCIERE"
                / "BILANS - CA"
                / make_unix_compatible(doc_new_path.name)
            )
        ]
    elif "IM" in doc_new_path.name:
        # Cas du memorandum d'information fait par comptoirs et commerces
        path_list = [
            (
                enseigne_dest_folder
                / "COMMERCIAL_DOCUMENTS"
                / make_unix_compatible(doc_new_path.name)
            )
        ]
    elif (
        "Lettre" in doc_new_path.name
        or "lettre" in doc_new_path.name
        or "LETTRE" in doc_new_path.name
    ) and (
        "Offre" in doc_new_path.name
        or "offre" in doc_new_path.name
        or "OFFRE" in doc_new_path.name
    ):
        # Cas de la lettre d offre deja faite fait par comptoirs et commerces
        path_list = [
            (
                enseigne_dest_folder
                / "COMMERCIAL_DOCUMENTS"
                / make_unix_compatible(doc_new_path.name)
            )
        ]
    elif doc_new_path.suffix == ".json":
        path_list = [
            (
                enseigne_dest_folder
                / "MISTRAL_FILES"
                / make_unix_compatible(doc_new_path.name)
            )
        ]
    elif doc_new_path.suffix == ".pdf":

        # les fichiers pdfs contiennent des images
        # quand elles sont tres grosses, on fait rien
        taille_mo = calculer_taille_fichier_mo(doc_new_path)
        if taille_mo > 100:
            path_list = [
                (
                    enseigne_dest_folder
                    / "OTHERS"
                    / make_unix_compatible(doc_new_path.name)
                )
            ]

        # traitement classique
        path_list = classify_pdf_document(enseigne_dest_folder, doc_new_path)

    elif doc_new_path.suffix == ".xlsx":
        # path_list = classify_xlsx_document(dest_folder, doc_new_path)
        path_list = [
            (
                enseigne_dest_folder
                / "WORK_DOCUMENTS"
                / make_unix_compatible(doc_new_path.name)
            )
        ]
    elif is_photo(doc_new_path):
        path_list = [
            (
                enseigne_dest_folder
                / "REFERENCE_DOCUMENTS"
                / "PHOTOS"
                / make_unix_compatible(doc_new_path.name)
            )
        ]
    elif (
        is_video(doc_new_path)
        or doc_new_path.suffix == ".mov"  # videos IPHONE
        or doc_new_path.suffix == ".MOV"  # videos IPHONE
    ):
        path_list = [
            (
                enseigne_dest_folder
                / "REFERENCE_DOCUMENTS"
                / "VIDEOS"
                / make_unix_compatible(doc_new_path.name)
            )
        ]
    elif doc_new_path.suffix == ".htm":
        path_list = [
            (
                enseigne_dest_folder
                / "WORK_DOCUMENTS"
                / make_unix_compatible(doc_new_path.name)
            )
        ]
    elif doc_new_path.suffix == ".doc" or doc_new_path.suffix == ".docx":
        path_list = [
            (
                enseigne_dest_folder
                / "WORD_DOCUMENTS_UNCLASSIFIED"
                / make_unix_compatible(doc_new_path.name)
            )
        ]
    else:
        LOGGER.critical("not implemented")
        path_list = []

    new_path_list = list(set(path_list))

    if len(new_path_list) == 0:
        LOGGER.critical(f"not any new path found for the doc {doc_new_path}")
        LOGGER.critical("we do nothing")
    elif len(new_path_list) > 1:
        LOGGER.warning(f"several locations foreseen for that document")
        LOGGER.warning(list(set(path_list)))
        LOGGER.critical("we do nothing")
    else:
        # let us move the files
        new_path = new_path_list[0]
        new_path.parent.mkdir(exist_ok=True, parents=True)
        shutil.move(doc_new_path, new_path)
        LOGGER.info(f"final file {path_list[0]}")

    return


def get_source_folder_path(etablissement_name):
    df = get_df_folder_possibles()
    enseignes_possibles = df.ENSEIGNE.drop_duplicates().values.tolist()
    # je cherche le folder correspondant
    LOGGER.debug(enseignes_possibles)
    LOGGER.debug(etablissement_name)
    for e in enseignes_possibles:
        if e == etablissement_name:
            folder = df.set_index("ENSEIGNE").loc[e, "folder"]
    return list(COMMERCIAL_DOCUMENTS_PATH.rglob(f"{folder}/"))[0]


def get_unclassified_path_filepath(etablissement_name):
    return TMP_PATH / make_unix_compatible(
        f"{etablissement_name}_unclassified_path.txt"
    )


def get_encours_path_filepath(etablissement_name):
    return TMP_PATH / make_unix_compatible(f"{etablissement_name}_en_cours.txt")


def create_unclassified_statistics(etablissement_name):
    unclassified_paths_list = check_all_documents_sorted(etablissement_name)
    unclassified_paths = classify_paths_by_parent(unclassified_paths_list)
    os.makedirs(TMP_PATH, mode=0o777, exist_ok=True)
    write_paths_to_file(
        unclassified_paths,
        get_unclassified_path_filepath(etablissement_name),
    )
    return


if __name__ == "__main__":

    # # etablissement_name = "LE_CHIEN_QUI_FUME"
    # # etablissement_name = "CIRO"
    # etablissement_name = "AFFRANCHIS"
    # main(etablissement_name)

    pass
