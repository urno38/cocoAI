import os
from pathlib import Path
from typing import Dict, List
from urllib.parse import urlencode

import pandas as pd
import requests

from common import execute
from common.convert import convert_pt_to_cm, load_yaml_to_dict
from common.identifiers import pick_id
from common.image import (
    detect_colors_in_image,
    detect_monochrome_images,
    detect_same_size_images,
    get_image_size,
    get_the_biggest_image_in_folder,
)
from common.legendes import TERRASSE_LEGEND_MONOCHROME, TERRASSE_LEGEND_RAYURES
from common.logconfig import LOGGER
from common.path import (
    OPENDATA_PARIS_URL,
    WORK_PATH,
    create_parent_directory,
    obtain_output_folder,
)
from common.pdf_document import download_pdf, extract_images_from_pdf
from common.REST_API import export_request, make_request_with_api_key


def get_all_terraces_from_a_siret(siret):
    params = {"where": f"siret={siret}"}
    json_terrassespath = (
        WORK_PATH / "terrasses_output" / f"output_terrasses_siret_{siret}.json"
    )
    if json_terrassespath.exists():
        os.remove(json_terrassespath)
    url = f"{OPENDATA_PARIS_URL}/catalog/datasets/terrasses-autorisations/records?&{urlencode(params)}"
    # LOGGER.debug(url)
    response = make_request_with_api_key(url, json_terrassespath)
    di = load_yaml_to_dict(json_terrassespath.with_suffix(".yaml"))
    return di


def get_all_gpx_from_a_siret(siret):
    # TODO : a actualiser avec les outputpath
    params = {"where": f"siret={siret}"}
    json_terrassespath = WORK_PATH / "terrasses_output" / f"output_terrasses.gpx"
    if json_terrassespath.exists():
        os.remove(json_terrassespath)
    url = f"{OPENDATA_PARIS_URL}/catalog/datasets/terrasses-autorisations/export/gpx?&{urlencode(params)}"
    # LOGGER.debug(url)

    response = requests.get(url)

    if response.status_code == 200:
        LOGGER.info("Request successful!")
        create_parent_directory(json_terrassespath)
        export_request(response, json_terrassespath)
    else:
        LOGGER.debug(response.text)
        raise ValueError(f"Request failed with status code {response.status_code}")
    return response


def get_terrasse_legend(image_folder_path):
    # TODO : a faire tourner quand le site de la mairie de Paris sera operationnel
    # Exemple d'utilisation
    monochrome_images = detect_monochrome_images(image_folder_path)
    LOGGER.debug(monochrome_images)

    reference_image = list(monochrome_images.keys())[1]
    same_size_images = detect_same_size_images(
        image_folder_path, image_folder_path / reference_image
    )

    autres_images = {}
    for im in same_size_images:
        if im not in list(monochrome_images.keys()):
            num_colors, colors_hex = detect_colors_in_image(image_folder_path / im)
            LOGGER.debug(f"Nombre de couleurs : {num_colors}")
            LOGGER.debug(f"Couleurs : {colors_hex}")
            autres_images[im] = colors_hex

    legend = {}
    for im, color in monochrome_images.items():
        legend[im] = TERRASSE_LEGEND_MONOCHROME[color]
    for im, color_tuple in autres_images.items():
        for tuple, leg in TERRASSE_LEGEND_RAYURES:
            if color_tuple == tuple:
                legend[im] = leg

    LOGGER.info("Got the terrace legend!")
    LOGGER.debug(legend)
    return legend


def create_map_with_legend(
    pdf_path=r"c:\Users\lvolat\Downloads\328311052_004.pdf",
    dossier_images=WORK_PATH / "extracted_images",
):

    extracted_images = extract_images_from_pdf(pdf_path, dossier_images)
    LOGGER.info(f"Successfully extracted {len(extracted_images)} images:")
    for img_path in extracted_images:
        LOGGER.debug(f"- {img_path}")

    legende = get_terrasse_legend(dossier_images)

    map_path = get_the_biggest_image_in_folder(dossier_images)
    LOGGER.info("Got the map image!")
    LOGGER.debug(map_path)
    return dossier_images, legende, map_path


def get_infos_terrasses_etablissement(siret, etablissement):

    params = {"where": f"siret={siret}"}

    json_path = (
        obtain_output_folder(etablissement, kind="siret", number=siret)
        / f"request.json"
    )

    url = (
        OPENDATA_PARIS_URL
        + "/catalog"
        + "/datasets/terrasses-autorisations"
        + f"/records?&"
        + urlencode(params)
    )
    response = make_request_with_api_key(url, json_path)
    di = load_yaml_to_dict(json_path.with_suffix(".yaml"))

    return di


def draw_map_slide_with_legend(
    legend_dict: dict, output_path: Path, map_image_path: Path
):

    latex_content = (
        """
    \\documentclass{beamer}
    \\usepackage[utf8]{inputenc}
    \\usepackage{graphicx}
    \\usepackage{array}

    \\begin{document}

    \\begin{frame}
    \\frametitle{Terrace map}
    \\begin{columns}
        \\begin{column}{0.5\\textwidth}
        \\begin{tabular}{m{"""
        + str(convert_pt_to_cm(get_image_size("page1_img1.png")[0]) + 1)
        + """cm} l}
    """
    )

    for img, legend in legend_dict.items():
        latex_content += f"\\includegraphics[scale=1]{{{img}}} & {legend} \\\\ \n"
    latex_content += (
        """
        \\end{tabular}
        \\end{column}
        \\begin{column}{0.5\\textwidth}
        \\includegraphics[width=\\linewidth]{"""
        + str(map_image_path)
        + """}
        \\end{column}
    \\end{columns}
    \\end{frame}

    \\end{document}
    """
    )

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(latex_content)

    LOGGER.info("Le fichier LaTeX a été généré avec succès.")

    return output_path


def reorganize_and_display(data: List[Dict]) -> pd.DataFrame:
    # Organiser les données par adresse et typologie
    organized_data = {}

    for entry in data["results"]:
        adresse = entry["adresse"]
        typologie = entry["typologie"]
        largeur = entry["largeur"]
        longueur = entry["longueur"]

        if adresse not in organized_data:
            organized_data[adresse] = {}
        if typologie not in organized_data[adresse]:
            organized_data[adresse][typologie] = []

        organized_data[adresse][typologie].append(
            {"largeur": largeur, "longueur": longueur}
        )

    # Convertir les données organisées en DataFrame
    rows = []
    for adresse, typologies in organized_data.items():
        for typologie, dimensions in typologies.items():
            for dimension in dimensions:
                rows.append({"adresse": adresse, "typologie": typologie, **dimension})

    df = pd.DataFrame(rows)
    return df


def extract_terrace_info_from_siret(siret, etablissement: str = "LE_JARDIN_DE_ROME"):
    """_summary_

    Args:
        siret (_type_): _description_
        etablissement (str, optional): _description_. Defaults to "LE_JARDIN_DE_ROME".

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """

    LOGGER.debug(f"Let us extract the infos from the gargote {etablissement}")
    output_path = obtain_output_folder(etablissement, kind="siret", number=siret)
    output_csvpath = output_path / "terrasses.csv"
    output_texpath = output_path / "terrasses.tex"

    # let us catch the infos
    di = get_infos_terrasses_etablissement(siret, etablissement)

    lien_affichette = set(list([t["lien_affichette"] for t in di["results"]]))
    LOGGER.info(f"lien_affichette { lien_affichette}")
    if len(lien_affichette) > 1:
        LOGGER.warning(
            "attention, dans OPEN DATA il y a des fausses valeurs d'affichettes ou des choses bizarres"
        )
        if None in lien_affichette:
            lien_affichette = [l for l in lien_affichette if l is not None]
            LOGGER.debug("None(s) deleted")
        else:
            raise ValueError("haha, OPENDATA aime bien les affichettes")

    # PARTIE TERRASSE
    try:
        for url in lien_affichette:
            affichette_path = output_path / "affichette.pdf"
            LOGGER.debug(f"{url} {affichette_path}")
            download_pdf(url, affichette_path)

        dossier_images, legende, map_path = create_map_with_legend(
            affichette_path, output_path / "extracted_images"
        )
    except:
        LOGGER.error("pdf non téléchargé")

    # # PARTIE IMPRESSION DES CARACTERISTIQUES
    df = reorganize_and_display(di)
    df["surface"] = df["largeur"] * df["longueur"]
    df = df.sort_values("surface")
    df = df.loc[:, ["adresse", "typologie", "surface"]]
    df = df.set_index("adresse")

    df.to_csv(output_csvpath)
    LOGGER.info(f"Exported in  { output_csvpath}")
    df.to_latex(
        buf=output_texpath,
        header=True,
        index=True,
        bold_rows=True,
        caption="infos terrasses",
        label="tab: infos terrasses",
        position="c",
        float_format="%.2f",
    )
    LOGGER.info(f"Exported in  { output_texpath}")

    LOGGER.info(f"Extracted all the needed terrace infos in {output_path}")

    return output_path, di


def generate_beamer_tex(df, output_file=Path("terrasses.tex"), standalone=False):
    with open(output_file, "w", encoding="utf-8") as f:
        if standalone:
            f.write("\\documentclass{beamer}\n")
            f.write("\\usepackage[french]{babel}\n")
            f.write("\\begin{document}\n\n")
        f.write("\\begin{frame}\n")
        f.write("    \\frametitle{Liste des Terrasses par Adresse}\n\n")
        # LOGGER.info(df)
        grouped = (
            df.groupby("adresse")
            .apply(lambda x: x.sort_values("surface"), include_groups=False)
            .reset_index()
        )
        # LOGGER.info(grouped)
        for adresse in grouped["adresse"].drop_duplicates():
            # LOGGER.info(adresse)
            f.write(f"    \\textbf{{{adresse}}}\\\n")
            f.write("    \\begin{itemize}\n")

            terrasse_surfaces = {}
            data = (
                df[df["adresse"] == adresse]
                .sort_values("surface")
                .sort_values("typologie", ascending=False)
            )
            for _, row in data.iterrows():
                if "PLANCHER MOBILE" in row["typologie"].upper():
                    terrasse_surfaces[row["surface"]] = (
                        f" dont  \\textbf{{plancher mobile: {round(float(row['surface']),2)} m$^2$}}\n"
                    )
                else:
                    f.write(
                        f"        \\item {row['typologie'].lower()}: {round(float(row['surface']),2)} m$^2$\n"
                    )

            for surface, plancher in terrasse_surfaces.items():
                if any(
                    row["surface"] == surface
                    for _, row in data.iterrows()
                    if "PLANCHER MOBILE" not in row["typologie"].upper()
                ):
                    f.write(plancher)

            f.write("    \\end{itemize}\n\n")

        f.write("\\end{frame}\n\n")
        if standalone:
            f.write("\\end{document}\n")
        # LOGGER.info(output_file.resolve())

    LOGGER.info(f"Output terrasses exported to { output_file.resolve()}")
    return


def generate_beamer_terrasses(etablissement, siret):
    output_path = obtain_output_folder(etablissement, kind="siret", number=siret)
    output_csvpath = output_path / "terrasses.csv"
    output_totaltexpath = output_path / "slides_terrasses.tex"
    df = pd.read_csv(output_csvpath)
    generate_beamer_tex(df, output_totaltexpath, standalone=True)
    cwd = Path.cwd()
    os.chdir(output_totaltexpath.parent)
    # subprocess.run(["pdflatex", output_totaltexpath])
    execute.execute_program("pdflatex", [output_totaltexpath])
    os.chdir(cwd)

    LOGGER.info(
        "Output terrasses exported to",
        output_totaltexpath.with_suffix(".pdf").resolve(),
    )

    return


def main(siret, etablissement):
    # path, di = extract_terrace_info_from_siret("LE_JARDIN_DE_ROME")
    path, di = extract_terrace_info_from_siret(siret, etablissement)

    # test pour le bouzin complet
    pdf_path = r"c:\Users\lvolat\Downloads\328311052_004.pdf"
    dossier_images, legende, map_path = create_map_with_legend(pdf_path)

    # test generate slides terrasses
    # Exemple d'utilisation
    generate_beamer_terrasses(etablissement, siret)


if __name__ == "__main__":
    # BLOC ENTREPRISE
    etablissement = "LE_BISTROT_VALOIS"
    main(siret=pick_id(etablissement, kind="siret"), etablissement=etablissement)
