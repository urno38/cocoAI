import os
import shutil
from pathlib import Path

from docx2pdf import convert

from cocoAI.company import get_infos_from_a_siret
from cocoAI.doc_sort import classify_one_document, create_unclassified_statistics
from cocoAI.etablissement import display_infos_on_siret
from common.folder_tree import create_complete_folder_tree, get_enseigne_folder_path
from common.identifiers import get_etablissement_name, verify_id
from common.logconfig import LOGGER
from common.path import (
    DATALAKE_PATH,
    TMP_PATH,
    is_directory_empty,
    main_liste,
    make_unix_compatible,
)


def main(siret, source_folder_path):

    source_folder_path = Path(source_folder_path)
    get_infos_from_a_siret(siret)
    display_infos_on_siret(siret)
    # household
    TMP_PATH.mkdir(exist_ok=True)

    # LOGGER.info(source_folder_path)

    dest_etablissement_folder_path = create_complete_folder_tree(siret)
    etablissement_name = make_unix_compatible(get_etablissement_name(siret))

    # LOGGER.debug(siret)
    # LOGGER.debug(etablissement_name)
    # LOGGER.info(dest_etablissement_folder_path)
    ENSEIGNE_FOLDER = get_enseigne_folder_path(siret)

    for path in source_folder_path.rglob("*"):
        if (
            len(list(ENSEIGNE_FOLDER.rglob(make_unix_compatible(path.name)))) == 0
            and path.is_file()
        ):
            LOGGER.info(f"this doc is not in ENSEIGNE_FOLDER {ENSEIGNE_FOLDER}")
            if path.suffix == ".docx":
                # LOGGER.info(path)
                convert(str(path))
                new_path = classify_one_document(path.with_suffix(".pdf"), siret)
                shutil.copy(path, new_path.with_suffix(".docx"))
                continue

            new_path = classify_one_document(path, siret)

        else:
            LOGGER.info(f"{path} is already in ENSEIGNE_FOLDER {ENSEIGNE_FOLDER}")

    output_path = create_unclassified_statistics(etablissement_name, source_folder_path)
    os.replace(output_path, dest_etablissement_folder_path / output_path.name)
    main_liste(
        dest_etablissement_folder_path,
        dest_etablissement_folder_path / "folder_tree.xlsx",
    )

    return


def main_user(siret=None):

    print("\n-----------")
    print("Classement de document dans le DATALAKE à partir d un siret")
    print("-----------")
    if siret is None:
        siret = input("\nEntrer un siret\n")
        verify_id(siret, "siret")

    DEFAULT_PATH = Path.cwd() / "to_classify"
    DEFAULT_PATH.mkdir(exist_ok=True)
    path = Path(
        input(
            f"\nEntrer le dossier qui contient tous les documents\nPar défaut : {DEFAULT_PATH}\nTaper entrée quand le dossier est plein\n"
        )
    )
    if path.resolve() == Path.cwd().resolve():
        path = DEFAULT_PATH

    print("fichiers dans le dossier")
    for fichier in path.iterdir():
        if fichier.is_file():
            print("- ", fichier.name)

    print("\n")
    print(f"on archive {path.resolve()}")
    main(siret, path)

    if is_directory_empty(path):  # check if it is empty
        LOGGER.info(f"suppressing {path} because it is empty")
        shutil.rmtree(path)


if __name__ == "__main__":
    # ROOT_PATH = (
    #     Path(r"C:\Users\lvolat\COMPTOIRS ET COMMERCES")
    #     / "COMMERCIAL - Documents"
    #     / "2 - DOSSIERS à l'ETUDE"
    #     / "1 - FONDS DE COMMERCES"
    #     / "GROUPE PELAMOURGUES"
    # )

    # main("82795341500011", ROOT_PATH / "1. RENAISSANCE 827953415")
    # main("89800482500011", ROOT_PATH / "2. L'ANNEXE 898004825")
    # main("85073698400012", ROOT_PATH / "3. LE BISTROT 850736984")
    # main("82793163500011", ROOT_PATH / "4. LES COULISSES 827931635")

    # main(
    #     "83995102700011",
    #     Path(
    #         r"C:\Users\lvolat\COMPTOIRS ET COMMERCES\COMMERCIAL - Documents\1 - DOSSIERS EN COURS DE SIGNATURE\DEI FRATELLI - 75001 PARIS - 10 Rue des PYRAMIDES"
    #     ),
    # )

    # 49435285900016
    # main_user()

    # main(
    #     38825528300037,
    #     r"C:\Users\lvolat\COMPTOIRS ET COMMERCES\COMMERCIAL - Documents\2 - DOSSIERS à l'ETUDE\1 - FONDS DE COMMERCES\BISTROT VALOIS (Le) - 75001 PARIS - 1 Bis Place de VALOIS",
    # )
    # main(
    #     53739192200011,
    #     r"C:\Users\lvolat\COMPTOIRS ET COMMERCES\COMMERCIAL - Documents\100 - DOSSIERS ARCHIVÉS\2 - ARCHIVES DOSSIERS SCANNÉS\1 - DOSSIERS SCANNÉS - BRASSERIES & DIVERS\BISTROT CHARBON (Le) - 75004 PARIS- 131 rue Saint MARTIN",
    # )
    main(
        83488996600018,
        r"C:\Users\lvolat\COMPTOIRS ET COMMERCES\COMMERCIAL - Documents\100 - DOSSIERS ARCHIVÉS\2 - ARCHIVES DOSSIERS SCANNÉS\1 - DOSSIERS SCANNÉS - BRASSERIES & DIVERS\BRASSERIE LOLA - MURS ET FONDS - 75015 PARIS - 99 rue du THÉÂTRE",
    )
