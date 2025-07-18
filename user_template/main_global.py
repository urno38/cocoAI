import datetime
import os
import shutil
import sys

import pypandoc

from cocoAI import bail, bilan, company, masse_salariale
from cocoAI.terrasse import extract_terrace_info_from_siret, generate_beamer_terrasses
from common.convert import add_title_to_markdown
from common.folder_tree import get_enseigne_folder_path, get_mistral_work_path
from common.identifiers import get_entreprise_name, get_etablissement_name, verify_id
from common.logconfig import LOGGER


def deplace_all_file_in_workpath(folder_path, dst_folder_path):
    dst_folder_path.mkdir(exist_ok=True)
    for p in folder_path.glob("*"):
        p.replace(dst_folder_path / p.name)
    return dst_folder_path


def bloc(siret, name, output_file_name, function, md_tuples):
    enseigne_folder = get_enseigne_folder_path(siret)
    work_folder = enseigne_folder / "WORK_DOCUMENTS"
    final_folder = work_folder / name
    if not (final_folder / output_file_name).exists():
        output_folder = function(siret)
        final_folder = deplace_all_file_in_workpath(output_folder, final_folder)
    md_tuples.append((name, final_folder / output_file_name))
    return md_tuples


def main(siret, open_word=False):
    # donnees
    siret = str(siret)
    siren = siret[:-5]
    ent = get_entreprise_name(siren)
    LOGGER.info(f"ENTREPRISE {ent}")

    LOGGER.info(f"siret {siret}")
    et = get_etablissement_name(siret)
    LOGGER.info(f"ETABLISSEMENT {et}")
    ENSEIGNE_FOLDER = get_enseigne_folder_path(siret)
    MISTRAL_WORK_PATH = get_mistral_work_path(siret)
    LIASSES_OUTPUT_PATH = get_mistral_work_path(siret) / "OUTPUT_LIASSES"
    WORK_FOLDER = ENSEIGNE_FOLDER / "WORK_DOCUMENTS"
    COMMERCIAL_FOLDER = ENSEIGNE_FOLDER / "COMMERCIAL_DOCUMENTS"
    tmp = WORK_FOLDER / "tmp"
    tmp.mkdir(exist_ok=True)
    md_tuples = []
    LOGGER.info(tmp)

    # TOUS LES BLOCS
    print("\n\n-----------")
    print("Production de memorandum")
    print("-----------")

    # company
    output_folder = company.main(siren, get_entreprise_name(siren), tmp)
    md_tuples.append(("summary", tmp / "summary.md"))

    # terrasses
    _, di = extract_terrace_info_from_siret(siret, et, tmp)
    if di is not None:
        _ = generate_beamer_terrasses(et, siret, tmp)
        add_title_to_markdown(tmp / "terrasses.md", title="terrasses")
        md_tuples.append(("Terrasses", tmp / "terrasses.md"))

    # A DEBUGGUER
    # create_markdown_with_images(tmp / "extracted_images", tmp / "images_terrasses.md")
    # md_tuples.append(("Plan terrasses", tmp / "images_terrasses.md"))

    # masse salariale
    nb_bulletins_salaires = masse_salariale.main(siret)
    tableau_salaires_path = tmp / "tableau_total_salaires.md"
    if tableau_salaires_path.is_file():
        add_title_to_markdown(tableau_salaires_path, title="masse salariale")
        md_tuples.append(("salaires", tableau_salaires_path))

    # bail
    if 1:
        for bailpath in ENSEIGNE_FOLDER.rglob("*BAIL*"):
            if bailpath.is_file():
                final_folder = WORK_FOLDER / bailpath.stem
                if (final_folder / (bailpath.stem + ".md")).exists():
                    output_folder = bail.main(bailpath)
                    final_folder = deplace_all_file_in_workpath(
                        output_folder, WORK_FOLDER, bailpath.stem
                    )
                    md_tuples.append(
                        (bailpath.stem, final_folder / (bailpath.stem + ".md"))
                    )

    # main_bilan.py
    # produits avec le bilan detaille dans COMMERCIAL_DOCUMENTS

    # liasse
    for liasse in [l for l in LIASSES_OUTPUT_PATH.glob("*.md")]:
        print(liasse)
        md_tuples.extend([(liasse.stem, liasse)])

    # print(md_tuples)

    # MEMORANDUM GLOBAL !!!

    # je convertis le markdown glob en docx et en pdf
    memorandum_path = (
        tmp / f'memorandum_{datetime.datetime.now().strftime("%d-%m-%Y_%Hh%M_%S")}.docx'
    )
    print(md_tuples)
    if len(md_tuples) > 0:
        pypandoc.convert_file(
            [str(md[1]) for md in md_tuples],
            "docx",
            outputfile=memorandum_path,
        )
        # LOGGER.info(memorandum_path)

        if open_word and os.name == "nt" and "3.10" in sys.version:
            import win32com

            # open the word document
            word_app = win32com.client.Dispatch("Word.Application")
            word_app.Visible = True
            document = word_app.Documents.Open(str(memorandum_path))
    else:
        LOGGER.info("pas de memorandum produit car pas d'infos disponibles")

    shutil.move(memorandum_path, COMMERCIAL_FOLDER)
    LOGGER.info("\n\n-----------\n")
    LOGGER.info("OUTPUT")
    LOGGER.info(COMMERCIAL_FOLDER / memorandum_path.name)
    LOGGER.info("\n\n-----------")


def main_user(siret=None):

    print("\n-----------")
    print("Script global production memorandum")
    print("-----------")

    if siret is None:
        siret = input("\nEntrer un siret\n")
        verify_id(siret, "siret")

    main(siret)
    print("done")

    ENSEIGNE_FOLDER = get_enseigne_folder_path(siret)
    FEC_DIR = (
        ENSEIGNE_FOLDER / "REFERENCE_DOCUMENTS" / "DOCUMENTATION_FINANCIERE" / "FEC"
    )
    COMMERCIAL_FOLDER = ENSEIGNE_FOLDER / "COMMERCIAL_DOCUMENTS"
    if FEC_DIR.is_dir():
        print("Production des bilans comptables à partir des FEC")
        FEClist = list(FEC_DIR.glob("*"))
        for p in FEClist:
            print(p)
        refyear = input("\nAnnee de reference [format : 2023]\n")
        curyear = input("\nAnnee courante [format : 2024]\n")

        print("\n\n")

        bilan.main(
            FEClist,
            refyear=refyear,
            curyear=curyear,
            xlsx_path=COMMERCIAL_FOLDER / "FEC_Bilan_detaille.xlsx",
        )

        print("done")


if __name__ == "__main__":

    # a partir d'un seul siret, je produis un memo blanc
    # siret = "31013032300028"  # le chien qui fume
    # siret = "82795341500011"  # le renaissance
    # siret = "89800482500011"  # l annexe
    # siret = "85073698400012"  # le bistrot
    # siret = "82793163500011"  # les coulisses

    # siret = sample(get_df_folder_possibles()["siret"].dropna().values.tolist(), 1)[0]

    # siret = "53258418200010"

    # for siret in [
    #     "82795341500011",  # pelamourgues bistrot renaissance 1
    #     "89800482500011",  # pelamourgues 2 l annexe
    #     "85073698400012",  # pelamourgues 3 le bistrot
    #     "82793163500011",  # pelamourgues 4 les coulisses
    # ]:
    #     main(siret)

    # main("90834751100010")

    # for s in get_df_folder_possibles()["siret"].dropna().values.tolist():
    #     main(s)

    # main(48138353700018)
    # main_user()
    main(85364205600024)

    # li = get_df_folder_possibles()["siret"].dropna().values.tolist()
    # shuffled_list = random.sample(li, len(li))
    # for s in shuffled_list:
    #     main(s)
