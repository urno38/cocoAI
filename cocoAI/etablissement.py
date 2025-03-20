from cocoAI.terrasse import (
    extract_terrace_info_from_siret,
)
from common.AI_API import get_summary_from_dict
from common.convert import (
    convert_markdown_to_beamer,
    convert_markdown_to_docx,
    convert_markdown_to_latex,
    convert_markdown_to_pdf,
)
from common.identifiers import pick_id
from common.logconfig import LOGGER
from common.path import obtain_output_folder


def main(siret, entreprise):
    params = {"siret": siret}
    output_folder_path = obtain_output_folder(entreprise, kind="siret", number=siret)
    json_path = output_folder_path / "output.json"
    yaml_path = json_path.with_suffix(".yaml")
    summary_mdpath = json_path.with_suffix(".md")
    summary_texpath = json_path.with_suffix(".tex")
    summary_docxpath = json_path.with_suffix(".docx")
    summary_pdfpath = json_path.with_suffix(".pdf")
    beamer_mdpath = json_path.parent / "slides.md"
    beamer_texpath = json_path.parent / "slides.tex"
    beamer_pdfpath = json_path.parent / "slides.pdf"

    output_folder_path = obtain_output_folder(entreprise, kind="siret", number=siret)
    output_path, di = extract_terrace_info_from_siret(entreprise)

    # get_infos_terrasses_etablissement(pick_id(entreprise, "siret"), entreprise)

    summary_mdpath = get_summary_from_dict(di, output_folder_path)
    if not summary_mdpath.exists():
        # je fais differents exports
        convert_markdown_to_latex(summary_mdpath, summary_texpath)
        convert_markdown_to_docx(summary_mdpath, summary_docxpath)
        convert_markdown_to_pdf(summary_mdpath, summary_pdfpath)
        convert_markdown_to_latex(summary_mdpath, summary_texpath)

    if not beamer_mdpath.exists():
        convert_markdown_to_beamer(
            beamer_mdpath,
            beamer_pdfpath,
            beamer_texpath,
            title=f"Résumé entreprise {entreprise}",
        )
        LOGGER.info(f"Global summary available in {beamer_pdfpath}")

    LOGGER.info("Everything is available under " + str(output_folder_path))
    return output_folder_path


if __name__ == "__main__":
    main(
        siret=pick_id("LE_BISTROT_VALOIS", kind="siret"), entreprise="LE_BISTROT_VALOIS"
    )
