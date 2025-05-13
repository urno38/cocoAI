import json
import shutil

from common.AI_API import ask_Mistral
from common.folder_tree import get_enseigne_folder_path
from common.identifiers import convert_to_siren
from common.keys import MISTRAL_API_KEY_PAYANTE
from common.logconfig import LOGGER
from common.path import DATALAKE_PATH
from common.pdf_document import process_file_by_Mistral_OCR


def output_employes_json(file_path, ocr_response, request, output_path):

    response_dict = json.loads(ocr_response.model_dump_json())
    ocr_markdown = response_dict["pages"][0]["markdown"]

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

    return response_dict2


siret = "53446191800037"
siren = convert_to_siren(siret)
ENSEIGNE_FOLDER = get_enseigne_folder_path(siret)


# for bull in list(DATALAKE_PATH.rglob("plans*")):
#     try:
#         shutil.rmtree(bull)
#         print(bull)
#     except:
#         pass

print(ENSEIGNE_FOLDER)
MISTRAL_PATH = list(ENSEIGNE_FOLDER.rglob("**/MISTRAL_FILES/"))[0]
print(MISTRAL_PATH)

for sal in list(ENSEIGNE_FOLDER.rglob("BULL*/*.pdf")):
    print(sal)
    ocr_response = process_file_by_Mistral_OCR(sal)
    request = """pour le document joint, extrais : 
- les salaires
- les dates
- les mois concernés
- les noms des employés
- les postes occupés
- les anciennetés
 Présente le résultat sous forme d'un dictionnaire json"""
    output_employes_json(
        sal, ocr_response, request, MISTRAL_PATH / sal.name + "salaires"
    )


# for sal in list(DATALAKE_PATH.rglob("BULL*/*.pdf")):
#     print(sal)


# probleme de lecture sur plusieurs pages,  si l'OCR ne reconnait pas bien
# tuto dispo sur https://www.datacamp.com/tutorial/mistral-ocr
