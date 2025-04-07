import os
import shutil
from collections import defaultdict
from pathlib import Path
from typing import List

import pandas as pd

from cocoAI.company import get_infos_from_a_siret
from cocoAI.folder_tree import create_complete_folder_tree, get_entreprise_folder
from common.identifiers import pick_id
from common.logconfig import LOGGER
from common.path import (
    COMMERCIAL_DOCUMENTS_PATH,
    COMMON_PATH,
    DATALAKE_PATH,
    TMP_PATH,
    WORK_PATH,
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
        if file.is_file() and len(list(dest_folder_path.rglob(file.name))) == 0:
            unclassified_paths.append(file)
            LOGGER.info(f"{file} has not been sorted")

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

    LOGGER.debug(f"List written in {summary_file_path.resolve()}")


def classify_pdf_document(dest_folder, doc_new_path, etablissement_name):
    ocr_response = process_file_by_Mistral_OCR(doc_new_path)
    location_dict = get_new_location_dictionary_path(doc_new_path, ocr_response)
    LOGGER.debug(location_dict)
    path_list = []
    for key, value in location_dict.items():
        if value:
            potential_path = (
                dest_folder
                / make_unix_compatible(etablissement_name)
                / "REFERENCE_DOCUMENTS"
            )
            for el in key.split("/"):
                potential_path = potential_path / make_unix_compatible(el)
            path_list.append(potential_path / doc_new_path.name)

    return path_list


def classify_xlsx_document(dest_folder, xlsx_new_path):
    # je decide d analyser la premiere sheet du xlsx, la convertir en csv et donner a manger a mistral
    # de cette manière, j ai rapidement l info que je veux

    # csv_path = xlsx_new_path.with_suffix(".csv")
    # pd.read_excel(xlsx_new_path).to_csv(csv_path)
    # ocr_response = process_file_by_Mistral_OCR(csv_path)
    # location_dict = get_new_location_dictionary_path(csv_path, ocr_response)

    ocr_response = process_file_by_Mistral_OCR(xlsx_new_path)
    location_dict = get_new_location_dictionary_path(xlsx_new_path, ocr_response)

    path_list = []
    for key, value in location_dict.items():
        if value:
            potential_path = (
                dest_folder
                / make_unix_compatible(etablissement_name)
                / "REFERENCE_DOCUMENTS"
            )
            for el in key.split("/"):
                potential_path = potential_path / make_unix_compatible(el)
            path_list.append(potential_path / xlsx_new_path.name)

    return path_list


def get_etablissement_name(doc_new_path):
    tmpdf = pd.read_csv(list(COMMON_PATH.glob("*folder*csv"))[0])
    for folder in tmpdf["folder"].values:
        if make_unix_compatible(folder) in str(doc_new_path):
            return make_unix_compatible(folder)


def classify_one_document(doc_path, siret):

    LOGGER.debug(f"lets classify {doc_path}")

    siren = int(str(siret)[:-5])
    dest_folder = create_complete_folder_tree(siren)

    try:
        # soit je recupere le nom de l etablissement de ma databank
        entreprise_name, etablissement_name = get_infos_from_a_siret(siret)
    except:
        # soit je le recupere de mon csv
        get_etablissement_name(doc_new_path)

    doc_new_path = rapatrie_file(doc_path)
    del doc_path  # securite pour eviter de toucher ulterieurement au fichier d'origine

    if "TEASER" in doc_new_path.name or "teaser" in doc_new_path.name:
        # Cas du teaser fait par comptoirs et commerces
        path_list = [
            (
                dest_folder
                / make_unix_compatible(etablissement_name)
                / "COMMERCIAL_DOCUMENTS"
                / make_unix_compatible(doc_new_path.name)
            )
        ]
    elif (
        "LIASSE_FISCALE" in doc_new_path.name
        or "liasse_fiscale" in doc_new_path.name
        or "liasse fiscale" in doc_new_path.name
        or "LIASSE FISCALE" in doc_new_path.name
    ):
        path_list = [
            (
                dest_folder
                / make_unix_compatible(etablissement_name)
                / "REFERENCE_DOCUMENTS"
                / "DOCUMENTATION_FINANCIERE"
                / "BILANS - CA"
                / make_unix_compatible(doc_new_path.name)
            )
        ]
    elif "IM" in doc_new_path.name:
        # Cas du memorandum d'information fait par comptoirs et commerces fait par comptoirs et commerces
        path_list = [
            (
                dest_folder
                / make_unix_compatible(etablissement_name)
                / "COMMERCIAL_DOCUMENTS"
                / make_unix_compatible(doc_new_path.name)
            )
        ]
    elif doc_new_path.suffix == ".json":
        path_list = [
            (
                dest_folder
                / make_unix_compatible(etablissement_name)
                / "MISTRAL_FILES"
                / make_unix_compatible(doc_new_path.name)
            )
        ]
    elif doc_new_path.suffix == ".pdf":
        path_list = classify_pdf_document(dest_folder, doc_new_path, etablissement_name)
    elif doc_new_path.suffix == ".xlsx":
        # path_list = classify_xlsx_document(dest_folder, doc_new_path)
        path_list = []
    elif is_photo(doc_new_path):
        path_list = [
            (
                dest_folder
                / make_unix_compatible(etablissement_name)
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
                dest_folder
                / make_unix_compatible(etablissement_name)
                / "REFERENCE_DOCUMENTS"
                / "VIDEOS"
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
        LOGGER.debug(f"new location {path_list[0]}")

    return


def get_etablissement_folder_name(etablissement_name):
    # fonction pour corriger eventuellement les fautes d orthographe a l'encodage
    return (
        etablissement_name.replace("LE", "")
        .replace("_", " ")
        .replace("BISTRO", "BISTROT")
        .strip()
    )


def get_source_folder_path(etablissement_name):

    if etablissement_name == "LE_CHIEN_QUI_FUME":
        # rustine car il existe deux chien qui fume
        folder_name = get_etablissement_folder_name("CHIEN QUI FUME (Le)")
    else:
        folder_name = get_etablissement_folder_name(etablissement_name)

    source_folder_path_list = list(
        (COMMERCIAL_DOCUMENTS_PATH / "2 - DOSSIERS à l'ETUDE").rglob(
            f"*{folder_name}*/"
        )
    )

    if len(source_folder_path_list) != 1:
        LOGGER.debug(
            (COMMERCIAL_DOCUMENTS_PATH / f"2 - DOSSIERS à l'ETUDE/*{folder_name}*/")
        )
        LOGGER.debug(source_folder_path_list)
        raise ValueError("not the right source_folder_path")

    return source_folder_path_list[0]


def create_unclassified_statistics(etablissement_name):
    unclassified_paths_list = check_all_documents_sorted(etablissement_name)
    unclassified_paths = classify_paths_by_parent(unclassified_paths_list)
    os.makedirs(TMP_PATH, mode=0o777, exist_ok=True)
    write_paths_to_file(
        unclassified_paths,
        TMP_PATH / make_unix_compatible(f"{etablissement_name}_unclassified_path.txt"),
    )
    return


def main(etablissement_name):
    siret = pick_id(etablissement_name, kind="siret")
    SOURCE_FOLDER_PATH = get_source_folder_path(etablissement_name)
    DOCS_TO_CLASSIFY = [p for p in SOURCE_FOLDER_PATH.rglob("*") if p.is_file()]

    for path in DOCS_TO_CLASSIFY:
        if path.suffix == ".json":
            LOGGER.info("it is a json file, not transfered")
        if len(list(DATALAKE_PATH.rglob(make_unix_compatible(path.name)))) == 0:
            LOGGER.debug(path)
            classify_one_document(path, siret)

    create_unclassified_statistics(etablissement_name)


if __name__ == "__main__":

    # etablissement_name = "LE_CHIEN_QUI_FUME"
    # etablissement_name = "CIRO"
    etablissement_name = "AFFRANCHIS"
    main(etablissement_name)
