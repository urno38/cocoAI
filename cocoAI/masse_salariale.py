import base64
import json
from pathlib import Path

import pandas as pd
from mistralai import Mistral

from common.AI_API import ask_Mistral
from common.folder_tree import (
    get_enseigne_folder_path,
    get_mistral_work_path,
    get_work_path,
)
from common.keys import MISTRAL_API_KEY_PAYANTE
from common.logconfig import LOGGER


def data_uri_to_bytes(data_uri):
    # Assuming the data_uri is in the format: "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA..."
    header, encoded = data_uri.split(",", 1)
    return base64.b64decode(encoded)


def export_image(image):
    try:
        parsed_image = data_uri_to_bytes(image.image_base64)
        with open(outputimage_path, "wb") as file:
            file.write(parsed_image)
        print(f"Image successfully exported to {outputimage_path.resolve()}")
    except Exception as e:
        print(f"An error occurred while exporting the image: {e}")


def export_imagev2(image, doc_path):
    try:
        parsed_image = data_uri_to_bytes(image.image_base64)
        outputimage_path = doc_path.parent / (doc_path.stem + "_" + image.id)
        with open(outputimage_path, "wb") as file:
            file.write(parsed_image)
        print(f"Image successfully exported to {outputimage_path.resolve()}")
    except Exception as e:
        print(f"An error occurred while exporting the image: {e}")


def parse_pdf(file_path, MISTRAL_PATH):
    client = Mistral(api_key=MISTRAL_API_KEY_PAYANTE)
    uploaded_file = client.files.upload(
        file={"file_name": str(file_path), "content": open(str(file_path), "rb")},
        purpose="ocr",
    )
    file_url = client.files.get_signed_url(file_id=uploaded_file.id)
    response = client.ocr.process(
        model="mistral-ocr-latest",
        document={"type": "document_url", "document_url": file_url.url},
        include_image_base64=True,
    )

    md_output_path = MISTRAL_PATH / (file_path.stem + "_output.md")
    with open(md_output_path, "w", encoding="utf-8") as f:
        for page in response.pages:
            f.write(page.markdown)
            for image in page.images:
                export_imagev2(image, md_output_path)
    print(md_output_path)
    return md_output_path


def output_employes_json(request, output_path):

    # response_dict = json.loads(ocr_response.model_dump_json())
    # ocr_markdown = response_dict["pages"][0]["markdown"]
    request_file = output_path.with_suffix(".request")
    with open(request_file, "w", encoding="utf-8") as f:
        f.write(request)
        LOGGER.debug(f"request exported to {request_file}")

    model = "mistral-large-latest"
    chat_response = ask_Mistral(
        api_key=MISTRAL_API_KEY_PAYANTE,
        prompt=request,
        model=model,
        json_only=True,
    )
    json_dict = chat_response.choices[0].message.content

    response_dict2 = json.loads(json_dict)
    json_path = output_path.with_suffix(".json")
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(response_dict2, ensure_ascii=False))
        LOGGER.debug(json_path.resolve())
    # print(json_path)

    return response_dict2


def main(siret):

    # siren = convert_to_siren(siret)
    LOGGER.info(siret)
    ENSEIGNE_FOLDER = get_enseigne_folder_path(siret)
    LOGGER.info(ENSEIGNE_FOLDER)
    MISTRAL_WORK_PATH = get_mistral_work_path(siret)
    TMP_WORK_PATH = get_work_path(siret) / "tmp"
    FILES_TO_ANALYSE = list(ENSEIGNE_FOLDER.rglob("BULLETINS_PAIE/*.pdf"))

    if len(FILES_TO_ANALYSE) == 0:
        LOGGER.info("pas de bulletins de salaires dispos")
        return 0.0

    analysed_files_path_list = []
    for sal in FILES_TO_ANALYSE:
        TABLEAU = MISTRAL_WORK_PATH / (sal.stem + "_tableau_salaires.csv")
        LOGGER.debug(sal)
        if TABLEAU.exists():
            LOGGER.info(f"{TABLEAU.resolve()} existe")
            continue

        # try:
        md_output = parse_pdf(sal, MISTRAL_WORK_PATH)
        # except:
        # LOGGER.warning(f"{sal} n est pas interprete")
        # continue

        with open(md_output, "r", encoding="utf-8") as f:
            ocr_output = "\n".join(f.readlines())

        request = (
            """pour le document joint, extrais : 
    - les salaires net à payer avant impôt sur le revenu
    - les dates
    - les mois concernés
    - les noms des employés
    - les postes occupés
    - les anciennetés
    Présente le résultat sous forme d'un dictionnaire json de la forme 
    "Employés": [
            {
                "Nom": ,
                "Poste": 
                "Salaire net à payer avant impôt sur le revenu": 
                "Date d'entrée":
                "Ancienneté":
                "Mois concernés": pd.datetime().strftime("%Y-%m")
            },
    \n"""
            + ocr_output
        )

        di = output_employes_json(request, MISTRAL_WORK_PATH / (sal.name + "salaires"))

        df = pd.DataFrame(di["Employés"])

        # formatage du df
        df = df.rename(
            columns={"Salaire net à payer avant impôt sur le revenu": "Salaire brut"}
        )
        df["Nom"] = df["Nom"].apply(lambda x: x.title())
        df["Poste"] = df["Poste"].apply(lambda x: x.upper())

        df.to_csv(TABLEAU)
        analysed_files_path_list.append(sal)

    if len(analysed_files_path_list) == 0.0:
        return 0.0

    TABLEAU_LIST = [
        MISTRAL_WORK_PATH / (sal.stem + "_tableau_salaires.csv")
        for sal in analysed_files_path_list
    ]
    df = pd.concat([pd.read_csv(t, index_col=0) for t in TABLEAU_LIST]).sort_values(
        "Nom"
    )

    csv_total = TMP_WORK_PATH / "tableau_total_salaires.csv"
    df.to_csv(csv_total)
    LOGGER.info(csv_total.resolve())
    df[[c for c in df.columns if c not in ["Date d'entrée"]]].sort_values(
        ["Mois concernés", "Nom"]
    ).to_markdown(csv_total.with_suffix(".md"), index=False)
    LOGGER.info(csv_total.with_suffix(".md").resolve())

    csvstat_total = TMP_WORK_PATH / "tableau_total_salaires_stat.csv"
    dfstat = df.groupby(["Nom", "Poste"])["Salaire brut"].mean()
    dfstat.to_csv(csvstat_total)
    LOGGER.info(csvstat_total.resolve())

    return len(analysed_files_path_list)


if __name__ == "__main__":
    # siret = "53446191800037"
    # siret = "33765583100010"
    # siret = "53258418200010"
    # siret = "89918997100018" #bug
    # siret = "48786663400016"  # bug #plusieurs fichiers

    siret = "79903742900047"
    main(siret)

    siret = "79903742900047"
    main(siret)
