import datetime
from random import sample

import pypandoc
import win32com.client

from cocoAI import bail, company, masse_salariale
from cocoAI.folder_tree import get_enseigne_folder, get_mistral_work_path
from cocoAI.terrasse import extract_terrace_info_from_siret, generate_beamer_terrasses
from common.convert import add_title_to_markdown
from common.identifiers import get_entreprise_name, get_etablissement_name
from common.logconfig import LOGGER
from common.path import get_df_folder_possibles


def deplace_all_file_in_workpath(folder_path, dst_folder_path):
    dst_folder_path.mkdir(exist_ok=True)
    for p in folder_path.glob("*"):
        p.replace(dst_folder_path / p.name)
    return dst_folder_path


def bloc(siret, name, output_file_name, function, md_tuples):
    enseigne_folder = get_enseigne_folder(siret)
    work_folder = enseigne_folder / "WORK_DOCUMENTS"
    final_folder = work_folder / name
    if not (final_folder / output_file_name).exists():
        output_folder = function(siret)
        final_folder = deplace_all_file_in_workpath(output_folder, final_folder)
    md_tuples.append((name, final_folder / output_file_name))
    return md_tuples


def main(siret):
    # donnees
    siren = siret[:-5]
    ent = get_entreprise_name(siren)
    LOGGER.info(f"ENTREPRISE {ent}")

    LOGGER.info(siret)
    et = get_etablissement_name(siret)
    LOGGER.info(f"ETABLISSEMENT {et}")
    ENSEIGNE_FOLDER = get_enseigne_folder(siret)
    MISTRAL_WORK_PATH = get_mistral_work_path(siret)
    work_folder = ENSEIGNE_FOLDER / "WORK_DOCUMENTS"
    commercial_folder = ENSEIGNE_FOLDER / "COMMERCIAL_DOCUMENTS"
    tmp = work_folder / "tmp"
    tmp.mkdir(exist_ok=True)
    md_tuples = []
    LOGGER.info(tmp)

    # TOUS LES BLOCS

    # company
    output_folder = company.main(siren, get_entreprise_name(siren), tmp)
    md_tuples.append(("summary", tmp / "summary.md"))

    # terrasses
    _, di = extract_terrace_info_from_siret(siret, et, tmp)
    if di is not None:
        _ = generate_beamer_terrasses(et, siret, tmp)
        add_title_to_markdown(tmp / "terrasses.md", title="terrasses")
        md_tuples.append(("terrasses", tmp / "terrasses.md"))

    # masse salariale
    nb_bulletins_salaires = masse_salariale.main(siret)
    if nb_bulletins_salaires > 0:
        add_title_to_markdown(
            tmp / "tableau_total_salaires.md", title="masse salariale"
        )
        md_tuples.append(("salaires", tmp / "tableau_total_salaires.md"))

    # bail
    if 1:
        for bailpath in ENSEIGNE_FOLDER.rglob("*BAIL*"):
            if bailpath.is_file():
                final_folder = work_folder / bailpath.stem
                if (final_folder / (bailpath.stem + ".md")).exists():
                    output_folder = bail.main(bailpath)
                    final_folder = deplace_all_file_in_workpath(
                        output_folder, work_folder, bailpath.stem
                    )
                    md_tuples.append(
                        (bailpath.stem, final_folder / (bailpath.stem + ".md"))
                    )

    # main_bilan.py
    # main_etablissement.py
    # main_liasse_fiscale.py

    # print(md_tuples)
    # je convertis le markdown glob en docx et en pdf
    memorandum_path = (
        commercial_folder
        / f"memorandum_{datetime.datetime.now().strftime("%d-%m-%Y_%Hh%M_%S")}.docx"
    )
    if len(md_tuples) > 0:
        pypandoc.convert_file(
            [str(md[1]) for md in md_tuples],
            "docx",
            outputfile=memorandum_path,
        )
        LOGGER.info(memorandum_path)
        # open the word document
        word_app = win32com.client.Dispatch("Word.Application")
        word_app.Visible = True
        document = word_app.Documents.Open(str(memorandum_path))
    else:
        LOGGER.info("pas de memorandum produit car pas d'infos disponibles")


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

    main("79903742900047")
