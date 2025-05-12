from random import sample

import pypandoc

from cocoAI.folder_tree import get_enseigne_folder
from cocoAI.terrasse import extract_terrace_info_from_siret
from common.AI_API import get_summary_from_dict
from common.convert import markdown_to_beamer, markdown_to_docx, markdown_to_pdf
from common.identifiers import get_etablissement_name
from common.logconfig import LOGGER
from common.path import get_df_folder_possibles, get_out_path


def main(siret, etablissement=None):

    if etablissement is None:
        etablissement = get_etablissement_name(siret)

    output_folder_path = get_out_path(etablissement, kind="siret", number=siret)
    json_path = output_folder_path / "output.json"
    summary_texpath = json_path.with_suffix(".tex")
    summary_docxpath = json_path.with_suffix(".docx")
    summary_pdfpath = json_path.with_suffix(".pdf")
    beamer_mdpath = json_path.parent / "slides.md"
    beamer_texpath = json_path.parent / "slides.tex"
    beamer_pdfpath = json_path.parent / "slides.pdf"

    output_path, di = extract_terrace_info_from_siret(siret, etablissement)
    try:
        summary_mdpath = get_summary_from_dict(di, output_folder_path)

        pypandoc.convert_file(
            summary_mdpath,
            "latex",
            outputfile=summary_texpath,
            extra_args=["--standalone"],
        )
        markdown_to_docx(summary_mdpath, summary_docxpath)
        markdown_to_pdf(summary_mdpath, summary_pdfpath)

        if beamer_mdpath.exists():
            markdown_to_beamer(
                beamer_mdpath,
                beamer_pdfpath,
                beamer_texpath,
                title=f"Résumé entreprise {etablissement}",
            )
            LOGGER.info(f"Global summary available in {beamer_pdfpath}")
    except:
        pass

    LOGGER.info("Everything is available under " + str(output_folder_path))
    return output_folder_path


def display_infos_on_siret(siret):

    LOGGER.info(f"siret {siret}")
    etablissement = get_etablissement_name(siret)
    LOGGER.info(f"etablissement {etablissement}")
    ENSEIGNE_FOLDER = get_enseigne_folder(siret)

    LOGGER.info(ENSEIGNE_FOLDER)
    if ENSEIGNE_FOLDER.exists():
        LOGGER.info(f"déjà archivé")
        # LOGGER.info("dossier de travail")
        # LOGGER.info(get_enseigne_folder(siret))
    else:
        LOGGER.info(f"à archiver")

    return


if __name__ == "__main__":
    siret = sample(get_df_folder_possibles()["siret"].dropna().values.tolist(), 1)[0]
    for siret in [
        "98247515400018",  # buggué car dictionnaire vide
    ]:
        LOGGER.info(siret)
        et = get_etablissement_name(siret)
        LOGGER.info(f"ETABLISSEMENT {et}")
        main(siret)
