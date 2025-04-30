from cocoAI.terrasse import extract_terrace_info_from_siret
from common.AI_API import get_summary_from_dict
from common.convert import (
    markdown_to_beamer,
    markdown_to_docx,
    markdown_to_latex,
    markdown_to_pdf,
)
from common.identifiers import get_etablissement_name, pick_id
from common.logconfig import LOGGER
from common.path import get_out_path


def main(siret, etablissement=None):

    if etablissement is None:
        etablissement = get_etablissement_name(siret)

    params = {"siret": siret}
    output_folder_path = get_out_path(etablissement, kind="siret", number=siret)
    json_path = output_folder_path / "output.json"
    yaml_path = json_path.with_suffix(".yaml")
    # summary_mdpath = json_path.with_suffix(".md")
    summary_texpath = json_path.with_suffix(".tex")
    summary_docxpath = json_path.with_suffix(".docx")
    summary_pdfpath = json_path.with_suffix(".pdf")
    beamer_mdpath = json_path.parent / "slides.md"
    beamer_texpath = json_path.parent / "slides.tex"
    beamer_pdfpath = json_path.parent / "slides.pdf"

    output_folder_path = get_out_path(etablissement, kind="siret", number=siret)
    output_path, di = extract_terrace_info_from_siret(siret, etablissement)

    # get_infos_terrasses_etablissement(pick_id(entreprise, "siret"), entreprise)

    summary_mdpath = get_summary_from_dict(di, output_folder_path)

    if summary_mdpath.exists():
        markdown_to_latex(summary_mdpath, summary_texpath)
        markdown_to_docx(summary_mdpath, summary_docxpath)
        markdown_to_pdf(summary_mdpath, summary_pdfpath)
        markdown_to_latex(summary_mdpath, summary_texpath)

    if beamer_mdpath.exists():
        markdown_to_beamer(
            beamer_mdpath,
            beamer_pdfpath,
            beamer_texpath,
            title=f"Résumé entreprise {etablissement}",
        )
        LOGGER.info(f"Global summary available in {beamer_pdfpath}")

    LOGGER.info("Everything is available under " + str(output_folder_path))
    return output_folder_path


if __name__ == "__main__":

    main("48138353700018")
