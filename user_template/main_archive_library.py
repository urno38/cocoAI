import os
import shutil

import pypandoc
from docx2pdf import convert

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
    make_unix_compatible,
)

# def retrieve_KBIS_path(source_entreprise_folder_path):
#     LOGGER.debug(source_entreprise_folder_path)
#     KBIS_path_list = (
#         list(source_entreprise_folder_path.rglob("*KBIS*", case_sensitive=False))
#         + list(source_entreprise_folder_path.rglob("*K-BIS*", case_sensitive=False))
#         + list(source_entreprise_folder_path.rglob("*K_BIS*", case_sensitive=False))
#         + list(source_entreprise_folder_path.rglob("*K BIS*", case_sensitive=False))
#     )
#     new_KBIS_path_list = [rapatrie_file(p) for p in KBIS_path_list if p.is_file()]
#     LOGGER.debug("new_KBIS_path_list")
#     LOGGER.debug(new_KBIS_path_list)
#     return new_KBIS_path_list


def main():

    # household
    TMP_PATH.mkdir(exist_ok=True)
    if (COCOAI_PATH / "toto").exists():
        shutil.rmtree(COCOAI_PATH / "toto")

    EN_COURS = list(COMMERCIAL_DOCUMENTS_PATH.glob("2*/1*/"))[0]
    LOGGER.debug(EN_COURS)
    df = get_df_folder_possibles().reset_index()
    folder_possibles = df[~df.siret.isna()].folder.values
    # LOGGER.debug(folder_possibles)
    dossiers = (
        [d for d in list(COMMERCIAL_DOCUMENTS_PATH.glob("1 -*/*/"))]
        + [d for d in list(COMMERCIAL_DOCUMENTS_PATH.glob("2*/1*/*/"))]
        + [d for d in list(COMMERCIAL_DOCUMENTS_PATH.glob("10 -*/*/"))]
        + [d for d in list(COMMERCIAL_DOCUMENTS_PATH.glob("100 -*/1 -*/*/"))]
    )
    TO_BE_CLASSIFIED = [d for d in dossiers]
    # LOGGER.debug(TO_BE_CLASSIFIED)
    TO_BE_CLASSIFIED = [d for d in TO_BE_CLASSIFIED if d.name in folder_possibles]
    # LOGGER.debug(TO_BE_CLASSIFIED)
    for source_entreprise_folder_path in TO_BE_CLASSIFIED:

        LOGGER.info(source_entreprise_folder_path)
        ser = get_ser_infos(source_entreprise_folder_path)
        siret = ser["siret"]

        encours_filepath = get_encours_path_filepath(siret)
        if encours_filepath.exists():
            continue
        else:
            encours_filepath.touch()

        dest_etablissement_folder_path = create_complete_folder_tree(siret)
        etablissement_name = make_unix_compatible(get_etablissement_name(siret))

        # pour gerer les en cours
        encours_filepath = get_encours_path_filepath(etablissement_name)
        if encours_filepath.exists():
            continue
        else:
            encours_filepath.touch()

        # pour aller plus vite les prochaines fois
        tmp_filepath = get_unclassified_path_filepath(etablissement_name)
        if tmp_filepath.exists():
            continue

        LOGGER.debug(siret)
        LOGGER.debug(etablissement_name)
        LOGGER.info(dest_etablissement_folder_path)

        # je convertis tous les docx en pdf
        for ipath in (
            list(source_entreprise_folder_path.rglob("*.docx"))
            + list(source_entreprise_folder_path.rglob("*.doc"))
            + list(source_entreprise_folder_path.rglob("*.rtf"))
        ):
            if ipath.with_suffix(".pdf").exists():
                continue
            try:
                LOGGER.info(f'on convertit {ipath} en {ipath.with_suffix(".pdf")}')
                convert(ipath, ipath.with_suffix(".pdf"))

            except:
                LOGGER.warning(
                    f'pb de conversion de {ipath} en {ipath.with_suffix(".pdf")}'
                )
                LOGGER.warning("on essaie une conversion plus fine")
                try:
                    pypandoc.convert_file(
                        rf"{str(ipath)}",
                        to="pdf",
                        outputfile=rf"{str(ipath.with_suffix(".pdf"))}",
                        extra_args=["--pdf-engine=xelatex"],
                    )
                    LOGGER.debug("conversion ok")

                except:
                    LOGGER.warning("echec de la conversion")

        # pypandoc.convert_file(source_entreprise_folder_path.rglob("*.doc"), "pdf")
        # pypandoc.convert_file(source_entreprise_folder_path.rglob("*.rtf"), "pdf")

        for path in source_entreprise_folder_path.rglob("*"):
            if (
                len(list(DATALAKE_PATH.rglob(make_unix_compatible(path.name)))) == 0
                and path.is_file()
            ):
                classify_one_document(path, siret)

        create_unclassified_statistics(etablissement_name)

    return


if __name__ == "__main__":
    main()
    main()
    main()
