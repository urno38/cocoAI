import os
import shutil
from pathlib import Path

from cocoAI.company import get_infos_from_a_siret
from cocoAI.doc_sort import (
    classify_one_document,
    create_unclassified_statistics,
    get_encours_path_filepath,
    get_unclassified_path_filepath,
)
from cocoAI.folder_tree import (
    create_complete_folder_tree,
    get_df_folder_possibles,
    get_ser_infos,
)
from common.identifiers import get_etablissement_name
from common.logconfig import LOGGER
from common.path import (
    COCOAI_PATH,
    COMMERCIAL_DOCUMENTS_PATH,
    DATALAKE_PATH,
    TMP_PATH,
    make_unix_compatible,
)


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
            classify_one_document(path, siret)

    create_unclassified_statistics(etablissement_name, source_folder_path)

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
