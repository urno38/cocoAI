from cocoAI.company import get_infos_from_a_siren
from cocoAI.doc_sort import classify_one_document, create_unclassified_statistics
from cocoAI.extract_KBIS import get_real_name, get_SIREN
from cocoAI.folder_tree import create_complete_folder_tree
from common.logconfig import LOGGER
from common.path import (
    COMMERCIAL_DOCUMENTS_PATH,
    DATALAKE_PATH,
    make_unix_compatible,
    rapatrie_file,
)


def retrieve_KBIS_path(source_entreprise_folder_path):
    LOGGER.debug(source_entreprise_folder_path)
    KBIS_path_list = (
        list(source_entreprise_folder_path.rglob("*KBIS*", case_sensitive=False))
        + list(source_entreprise_folder_path.rglob("*K-BIS*", case_sensitive=False))
        + list(source_entreprise_folder_path.rglob("*K_BIS*", case_sensitive=False))
        + list(source_entreprise_folder_path.rglob("*K BIS*", case_sensitive=False))
    )
    new_KBIS_path_list = [rapatrie_file(p) for p in KBIS_path_list if p.is_file()]
    LOGGER.debug("new_KBIS_path_list")
    LOGGER.debug(new_KBIS_path_list)
    return new_KBIS_path_list


def get_infos_from_source_folder(source_entreprise_folder_path):

    KBIS_path_list = retrieve_KBIS_path(source_entreprise_folder_path)
    LOGGER.info(f"le dossier contient {KBIS_path_list}")
    siren_list = list(set([get_SIREN(p) for p in KBIS_path_list]))
    if len(siren_list) > 1:
        raise ValueError("trop de siren stockes")
    siren = siren_list[0]

    siren, entreprise_name, sirets, etablissements_dicts_list = get_infos_from_a_siren(
        siren
    )
    etablissement_name = get_real_name(KBIS_path_list)
    LOGGER.debug(etablissements_dicts_list)
    LOGGER.debug(etablissement_name)
    etablissement_names_list = [d["enseigne"] for d in etablissements_dicts_list]
    for i, etname in enumerate(etablissement_names_list):
        if etname == etablissement_name:
            siret = sirets[i]

    dest_entreprise_folder_path = create_complete_folder_tree(siren)

    return (
        siren,
        siret,
        dest_entreprise_folder_path,
        entreprise_name,
        etablissement_name,
    )


def main():
    EN_COURS = list(COMMERCIAL_DOCUMENTS_PATH.glob("2*/"))[0]

    for source_entreprise_folder_path in EN_COURS.rglob("*BROOKLYN*"):

        (
            siren,
            siret,
            dest_entreprise_folder_path,
            entreprise_name,
            etablissement_name,
        ) = get_infos_from_source_folder(source_entreprise_folder_path)

        DOCS_TO_CLASSIFY = [
            p for p in source_entreprise_folder_path.rglob("*") if p.is_file()
        ]
        for path in DOCS_TO_CLASSIFY:
            if len(list(DATALAKE_PATH.rglob(make_unix_compatible(path.name)))) == 0:
                classify_one_document(path, siret)

        create_unclassified_statistics(etablissement_name)

    return


if __name__ == "__main__":
    main()
