import os
from pathlib import Path
from urllib.parse import urlencode

import pandas as pd
import requests

from common import execute
from common.convert import dict_to_json, pt_to_cm, yaml_to_dict
from common.folder_tree import get_enseigne_folder_path
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
    load_json_file,
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
    di = yaml_to_dict(json_terrassespath.with_suffix(".yaml"))
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
        LOGGER.debug(response)
        LOGGER.debug("Request successful!")
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
    LOGGER.debug(f"Successfully extracted {len(extracted_images)} images:")
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
        get_enseigne_folder_path(siret) / "WORK_DOCUMENTS" / "tmp" / "request.json"
    )

    url = (
        OPENDATA_PARIS_URL
        + "/catalog"
        + "/datasets/terrasses-autorisations"
        + f"/records?&"
        + urlencode(params)
    )

    response = make_request_with_api_key(url, json_path)
    di = yaml_to_dict(json_path.with_suffix(".yaml"))

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
        + str(pt_to_cm(get_image_size("page1_img1.png")[0]) + 1)
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


def extract_terrace_info_from_siret(siret, etablissement, output_path=None):

    LOGGER.debug(f"Let us extract the infos from the gargote {etablissement}")

    if output_path is None:
        output_path = get_enseigne_folder_path(siret) / "WORK_DOCUMENTS" / "tmp"

    output_csvpath = output_path / "terrasses.csv"
    output_texpath = output_path / "terrasses.tex"
    output_mdpath = output_path / "terrasses.md"

    # let us catch the infos
    di = get_infos_terrasses_etablissement(siret, etablissement)
    if di["total_count"] == 0:
        return output_path, None

    lien_affichette = set(list([t["lien_affichette"] for t in di["results"]]))
    if len(lien_affichette) == 0:
        LOGGER.debug("pas d affichette dispo")
        return None, None
    LOGGER.info(f"lien_affichette {lien_affichette}")
    if len(lien_affichette) > 1:
        LOGGER.warning(
            "attention, dans OPEN DATA il y a des fausses valeurs d'affichettes ou des choses bizarres"
        )
        if None in lien_affichette:
            lien_affichette = [l for l in lien_affichette if l is not None]
            LOGGER.debug("None(s) deleted")

    # PARTIE TERRASSE
    for url in lien_affichette:
        try:
            affichette_path = output_path / f"affichette_terrasses_{siret}.pdf"
            LOGGER.debug(f"{url} {affichette_path}")
            download_pdf(url, affichette_path)

            dossier_images, legende, map_path = create_map_with_legend(
                affichette_path, output_path / "extracted_images"
            )
            dict_to_json(legende, output_path / "extracted_images" / "legend.json")

        except:
            LOGGER.error("affichette non decortiquee")

    # # PARTIE IMPRESSION DES CARACTERISTIQUES
    # Organiser les données par adresse et typologie
    organized_data = {}

    for entry in di["results"]:
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
    df["surface"] = df["largeur"] * df["longueur"]
    df = df.sort_values("surface")

    df = df.loc[:, ["adresse", "typologie", "surface"]]
    df = df.set_index("adresse")

    df.to_csv(output_csvpath)
    LOGGER.info(f"Exported in  {output_csvpath}")
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
    LOGGER.info(f"Exported in  {output_texpath}")

    df = pd.DataFrame(di["results"])
    df["surface"] = df["largeur"] * df["longueur"]
    df[
        [
            c
            for c in df.columns
            if not c
            in [
                "geo_point_2d",
                "geo_shape",
                "nom_societe",
                "nom_enseigne",
                "largeur",
                "longueur",
                "lien_affichette",
                "periode_installation",
                "arrondissement",
                "siret",
            ]
        ]
    ].sort_values(["adresse", "surface"]).set_index("adresse").to_markdown(
        output_mdpath
    )

    LOGGER.info(f"Exported in  {output_mdpath}")

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

    LOGGER.info(f"Output terrasses exported to {output_file.resolve()}")
    return


def generate_beamer_terrasses(etablissement, siret, output_path=None):

    if output_path is None:
        output_path = get_enseigne_folder_path(siret) / "WORK_DOCUMENTS" / "tmp"

    output_csvpath = output_path / "terrasses.csv"
    output_totaltexpath = output_path / "slides_terrasses.tex"
    df = pd.read_csv(output_csvpath)
    generate_beamer_tex(df, output_totaltexpath, standalone=True)
    cwd = Path.cwd()
    os.chdir(output_totaltexpath.parent)
    execute.execute_program("pdflatex", [output_totaltexpath])
    os.chdir(cwd)

    LOGGER.info(
        f"Output terrasses exported to {output_totaltexpath.with_suffix(".pdf").resolve()}"
    )

    return output_path


def create_markdown_with_images(folder_path, markdown_file):
    # Convertir le chemin du dossier en objet Path
    folder_path = Path(folder_path)

    # Vérifier si le dossier existe
    if not folder_path.exists():
        print(f"Le dossier {folder_path} n'existe pas.")
        return
    legend = load_json_file(folder_path / "legend.json")
    # Ouvrir le fichier Markdown en mode écriture
    with open(markdown_file, "w", encoding="utf-8") as md_file:
        for image_path in folder_path.iterdir():
            if image_path.suffix.lower() in [".png", ".jpg", ".jpeg", ".gif", ".bmp"]:
                relative_path = image_path.relative_to(markdown_file.parent)
                leg = (
                    legend[image_path.name]
                    if image_path.name in legend.keys()
                    else "Vue globale"
                )
                rpath = ("./" + str(relative_path).replace("\\", "/")).replace(
                    "./extracted_images/", ""
                )
                print(rpath)
                md_file.write(f"![{leg}]({rpath})\n\n")

    print(f"Fichier Markdown créé: {markdown_file}")


def main(siret, etablissement):

    output_folder, di = extract_terrace_info_from_siret(siret, etablissement)
    output_folder = generate_beamer_terrasses(etablissement, siret)
    create_markdown_with_images(
        output_folder / "extracted_images", output_folder / "images_terrasses.md"
    )
    return output_folder


if __name__ == "__main__":

    etablissement = "BISTROT_VALOIS"
    output_folder = main(48138353700018, etablissement)
