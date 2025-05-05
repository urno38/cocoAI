import os
import shutil
from pathlib import Path

import pandas as pd
from docx2pdf import convert

from cocoAI.company import get_infos_from_a_siret
from cocoAI.doc_sort import (
    classify_one_document,
    create_unclassified_statistics,
    get_encours_path_filepath,
    get_unclassified_path_filepath,
)
from cocoAI.folder_tree import create_complete_folder_tree, get_ser_infos
from common.identifiers import get_etablissement_name
from common.logconfig import LOGGER
from common.path import (
    COCOAI_PATH,
    COMMERCIAL_DOCUMENTS_PATH,
    DATALAKE_PATH,
    TMP_PATH,
    get_df_folder_possibles,
    list_files_in_directory,
    make_unix_compatible,
)


def split_path_into_components(file_path):
    """Décompose un chemin de fichier en ses composants."""
    path = Path(file_path)
    return [*path.parent.parts, "", path.name]


def save_to_excel(file_paths, output_file):
    """Enregistre la liste des fichiers dans un fichier Excel avec chaque composant du chemin dans une colonne."""
    # Trouver le nombre maximum de colonnes nécessaires
    max_depth = max(len(split_path_into_components(path)) for path in file_paths)
    print(max_depth)

    # Créer une liste de dictionnaires pour chaque fichier
    data = []
    for path in file_paths:
        components = split_path_into_components(path)
        # Remplir avec des valeurs vides si nécessaire
        components += [""] * (max_depth - len(components))
        data.append(components)

    # Créer un DataFrame avec des colonnes numérotées
    columns = [f"Niveau {i}" for i in range(1, max_depth)] + ["Fichier"]
    df = pd.DataFrame(data, columns=columns)

    # Enregistrer dans un fichier Excel
    df.to_excel(output_file, index=False)


def main_liste(directory, output_file):
    """Fonction principale pour lister les fichiers et les enregistrer dans un fichier Excel."""
    file_paths = list_files_in_directory(directory)
    save_to_excel(file_paths, output_file)
    print(f"Liste des fichiers enregistrée dans {output_file}")


def main(siret, source_folder_path):

    get_infos_from_a_siret(siret)

    # household
    TMP_PATH.mkdir(exist_ok=True)

    LOGGER.info(source_folder_path)

    dest_etablissement_folder_path = create_complete_folder_tree(siret)
    etablissement_name = make_unix_compatible(get_etablissement_name(siret))

    LOGGER.debug(siret)
    LOGGER.debug(etablissement_name)
    LOGGER.info(dest_etablissement_folder_path)

    for path in source_folder_path.rglob("*"):
        if (
            len(list(DATALAKE_PATH.rglob(make_unix_compatible(path.name)))) == 0
            and path.is_file()
        ):
            if path.suffix == ".docx":
                LOGGER.info(path)
                convert(str(path))
                new_path = classify_one_document(path.with_suffix(".pdf"), siret)
                shutil.copy(path, new_path.with_suffix(".docx"))
                continue

            new_path = classify_one_document(path, siret)

    output_path = create_unclassified_statistics(etablissement_name, source_folder_path)
    os.replace(output_path, dest_etablissement_folder_path / output_path.name)
    # if (dest_etablissement_folder_path/output_path.name).exists():

    # os.shutil.move(output_path, dest_etablissement_folder_path)
    # os.rename()

    main_liste(
        dest_etablissement_folder_path,
        dest_etablissement_folder_path / "folder_tree.xlsx",
    )

    return


if __name__ == "__main__":
    ROOT_PATH = (
        Path(r"C:\Users\lvolat\COMPTOIRS ET COMMERCES")
        / "COMMERCIAL - Documents"
        / "2 - DOSSIERS à l'ETUDE"
        / "1 - FONDS DE COMMERCES"
        / "GROUPE PELAMOURGUES"
    )

    main("82795341500011", ROOT_PATH / "1. RENAISSANCE 827953415")
    main("89800482500011", ROOT_PATH / "2. L'ANNEXE 898004825")
    main("85073698400012", ROOT_PATH / "3. LE BISTROT 850736984")
    main("82793163500011", ROOT_PATH / "4. LES COULISSES 827931635")

    # main(
    #     "83995102700011",
    #     Path(
    #         r"C:\Users\lvolat\COMPTOIRS ET COMMERCES\COMMERCIAL - Documents\1 - DOSSIERS EN COURS DE SIGNATURE\DEI FRATELLI - 75001 PARIS - 10 Rue des PYRAMIDES"
    #     ),
    # )
