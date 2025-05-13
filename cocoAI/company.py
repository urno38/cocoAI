import os
import re
import shutil
from urllib.parse import urlencode

import mermaid as mmd
import pypandoc
import requests
from mermaid.flowchart import FlowChart, Link, Node

from common.AI_API import get_summary_from_yaml
from common.convert import (
    beamer_to_pdf,
    markdown_to_beamer,
    markdown_to_docx,
    markdown_to_pdf,
    test_pappers_data_compliance,
    yaml_to_dict,
)
from common.folder_tree import get_out_path
from common.identifiers import (
    get_entreprise_name,
    get_etablissement_name,
    load_siren_in_databank,
    load_siret_in_databank,
)
from common.keys import PAPPERS_API_KEY_A_BERTUOL, PAPPERS_API_KEY_LVOLAT_FREE
from common.logconfig import LOGGER
from common.path import OUTPUT_PATH, PAPPERS_API_URL, make_unix_compatible
from common.REST_API import make_request_with_api_key

api_key = PAPPERS_API_KEY_LVOLAT_FREE
base_url = PAPPERS_API_URL


# Fonction pour obtenir des informations sur une entreprise, requete simple
def get_company_info(siren):
    endpoint = f"/entreprise/siren={siren}"
    url = base_url + endpoint
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lève une exception pour les erreurs HTTP
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        LOGGER.error(f"Erreur HTTP: {http_err}")
    except requests.exceptions.RequestException as req_err:
        LOGGER.error(f"Erreur de requête: {req_err}")
    return None


def create_beneficiaires_effectifs_diagram(yaml_path):
    di = yaml_to_dict(yaml_path)
    title = ""
    nodes = [Node("MIALANE")]
    links = []
    if di["beneficiaires_effectifs"] != []:
        LOGGER.debug("il existe des beneficiaires effectifs")
        for i, beneff in enumerate(di["beneficiaires_effectifs"]):
            # pLOGGER.info(beneff)
            LOGGER.debug(beneff["prenom_usuel"])
            LOGGER.debug(beneff["nom_usage"])
            # print(type(beneff["prenom_usuel"]), type(beneff["nom_usage"]))
            # try:
            noms = (
                beneff["prenom_usuel"] + " " + beneff["nom_usage"]
                if beneff["nom_usage"] is not None
                else beneff["prenom_usuel"]
            )
            nodes.append(Node(noms))
            links.append(
                Link(
                    nodes[i + 1],
                    nodes[0],
                    message=beneff["pourcentage_parts_indirectes"],
                )
            )
    else:
        LOGGER.debug("pas de beneficiaires effectifs")
        return

    nodes.append(Node(di["denomination"]))
    links.append(Link(nodes[0], nodes[-1], message="propriete"))

    flowchart = FlowChart(
        title,
        nodes,
        links,
    )

    chart = mmd.Mermaid(flowchart)
    chart.to_png(yaml_path.parent / "flowchart.png")
    chart.to_svg(yaml_path.parent / "flowchart.svg")
    LOGGER.debug(f"Produced {yaml_path.parent / 'flowchart.png'}")
    LOGGER.debug(f"Produced {yaml_path.parent / 'flowchart.svg'}")
    return


def modify_beamer_slide(file_path, output_path, diagram_path):
    # Define the pattern to search for the specific frame
    frame_pattern = re.compile(
        r"(\\begin\{frame\}\{Bénéficiaires Effectifs\}\s*"
        r"\\phantomsection\\label\{buxe9nuxe9ficiaires-effectifs\}(.*?)"
        r"\\end\{frame\})",
        re.DOTALL,
    )

    # Define the modified slide template
    modified_slide_template = r"""
    \begin{frame}{Bénéficiaires Effectifs}
    \phantomsection\label{buxe9nuxe9ficiaires-effectifs}
    \begin{columns}
        \begin{column}{0.5\textwidth}
            %s
        \end{column}
        \begin{column}{0.5\textwidth}
            \graphicspath{{%s}}
            \includegraphics[width=\textwidth]{%s}
        \end{column}
    \end{columns}
    \end{frame}
    """

    # Read the content of the file
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Find and replace the frame
    def replace_frame(match):
        frame_content = match.group(2).strip()
        return modified_slide_template % (
            frame_content,
            str(diagram_path.parent).replace("\\", "/"),
            diagram_path.name,
        )

    content = frame_pattern.sub(replace_frame, content)

    # Write the modified content back to the file
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(content)

    return


def get_output_path(entreprise, siren, output_folder_path=None):
    if output_folder_path is None:
        output_folder_path = get_out_path(entreprise, "siren", siren)
    json_path = output_folder_path / "output.json"
    yaml_path = json_path.with_suffix(".yaml")
    return json_path, yaml_path


def produce_yaml(siren, entreprise):
    params = {"siren": siren}
    json_path, yaml_path = get_output_path(entreprise, siren=siren)
    url = f"{PAPPERS_API_URL}/entreprise?&{urlencode(params)}"
    LOGGER.debug("url")
    LOGGER.debug(url)
    make_request_with_api_key(
        url=url,
        outputfile_path=json_path,
        API="PAPPERS",
        api_key=PAPPERS_API_KEY_A_BERTUOL,
    )
    output_folder_path = get_out_path(entreprise, kind="siren", number=siren)
    return output_folder_path


def clean_all_siren_outputs(siren):
    output_list = list(OUTPUT_PATH.glob(f"siren_*_{siren}"))
    for out in output_list:
        print("on supprime", out)
        shutil.rmtree(out)


def charge_yaml(yaml_path):
    di = yaml_to_dict(yaml_path)
    test_pappers_data_compliance(di)
    return (
        di["siren"],
        (
            make_unix_compatible(di["denomination"])
            if di["denomination"] is not None
            else make_unix_compatible(di["nom_entreprise"])
        ),
        [et["siret"] for et in di["etablissements"] if not et["etablissement_cesse"]],
        [et for et in di["etablissements"] if not et["etablissement_cesse"]],
    )


def extract_name_from_etablissement(et):
    if et["enseigne"] is not None:
        return make_unix_compatible(et["enseigne"])
    if et["nom_commercial"] is not None:
        return make_unix_compatible(et["nom_commercial"])
    return None


def get_infos_from_a_siren(siren: int):

    # je nettoie
    yaml_list = list(OUTPUT_PATH.glob(f"siren_*_{siren}/output.yaml"))
    LOGGER.debug(yaml_list)
    if len(yaml_list) != 1 or "siren_fake" in str(yaml_list[0]):
        clean_all_siren_outputs(siren)
        # une fois nettoye, je produis
        LOGGER.debug(siren)
        fake_out_path = produce_yaml(siren, "fake")
        infos = charge_yaml(fake_out_path / "output.yaml")
        denom = infos[1]
        out_path = get_out_path(denom, "siren", siren, create=False)
        os.rename(fake_out_path, out_path)
        load_siren_in_databank(denom, str(siren))
        siren, denom, sirets, ets = charge_yaml(out_path / "output.yaml")
    else:
        siren, denom, sirets, ets = charge_yaml(yaml_list[0])

    LOGGER.debug(ets)
    for et in ets:
        etname = extract_name_from_etablissement(et)
        if etname is not None:
            load_siret_in_databank(etname, et["siret"])
        else:
            if et["siege"]:
                LOGGER.debug(f"on nomme {et['siret']} {denom} car c est le siege")
                load_siret_in_databank(denom, et["siret"])
            else:
                LOGGER.debug(
                    f"on nomme {et['siret']} {denom}_{et['siret'][-5:]} car mal nommes"
                )
                load_siret_in_databank(denom + "_" + et["siret"][-5:], et["siret"])

    return siren, denom, sirets, ets


def get_infos_from_a_siret(siret):
    siret = str(siret)
    siren = siret[:-5]
    get_infos_from_a_siren(siren)
    return get_entreprise_name(siren), get_etablissement_name(siret)


def main(siren, entreprise, output_folder_path=None):

    params = {"siren": siren}
    json_path, yaml_path = get_output_path(entreprise, siren, output_folder_path)

    url = f"{PAPPERS_API_URL}/entreprise?&{urlencode(params)}"

    make_request_with_api_key(
        url=url,
        outputfile_path=json_path,
        API="PAPPERS",
        api_key=PAPPERS_API_KEY_A_BERTUOL,
    )

    di = yaml_to_dict(yaml_path)

    if 1:
        # pas ouf comme maniere de faire
        # summary_mdpath = get_summary_from_dict(di, yaml_path.parent)

        summary_mdpath = get_summary_from_yaml(yaml_path)
        texpath = yaml_path.with_suffix(".tex")

        if not texpath.exists():
            pypandoc.convert_file(
                summary_mdpath,
                "latex",
                outputfile=texpath,
                extra_args=["--standalone"],
            )
            markdown_to_docx(summary_mdpath, yaml_path.with_suffix(".docx"))
            markdown_to_pdf(summary_mdpath, yaml_path.with_suffix(".pdf"))

        if not (yaml_path.parent / "slides.md").exists():
            markdown_to_beamer(
                summary_mdpath,
                yaml_path.parent / "slides.pdf",
                yaml_path.with_suffix(".tex"),
                title=f"Résumé siren {siren}",
            )
            LOGGER.info(
                f"Global summary available in {yaml_path.parent / "slides.pdf"}"
            )

            # beneficiaires effectifs
            try:
                create_beneficiaires_effectifs_diagram(yaml_path)
                diagram_path = (json_path.parent / "flowchart.png").resolve()
                output_pdf = json_path.parent / "slidesv2.pdf"
                output_tex = json_path.parent / "slidesv2.tex"
                modify_beamer_slide(
                    yaml_path.parent / "slides.tex", output_tex, diagram_path
                )
                beamer_to_pdf(output_tex, output_pdf)
            except:
                LOGGER.debug("beneficiaires effectifs not done")

        LOGGER.info(f"Everything is available under {yaml_path.parent}")
    return yaml_path.parent


if __name__ == "__main__":
    # siret = sample(get_df_folder_possibles()["siret"].dropna().values.tolist(), 1)[0]
    # siren = siret[:-5]
    # LOGGER.info(siret)
    # et = get_etablissement_name(siret)
    # LOGGER.info(f"ETABLISSEMENT {et}")
    # entreprise, etablissement = get_infos_from_a_siret(siret)
    # main(siren, entreprise)

    # main(pick_id("GALLA", kind="siren"), "GALLA")

    # siren, entreprise_name, sirets, etablissements = get_infos_from_a_siren(310130323)
    # for s in [
    # "30176296900016",
    # "40413673100019",
    # "48138353700018",
    # "47150251800018",
    # "45229220400024",
    # "34027633600039",
    # "56201528900019",
    # "79903742900047",
    # "32176212200018",
    # "80224059800010",
    # "91795262400026",
    # "81131629800017",
    # "45156961000012",
    # "31677872900012",
    # "79903742900047",
    # "44487749200025",
    # 53258418200010
    # ]:
    #     get_infos_from_a_siret(s)

    get_infos_from_a_siren(532584182)
