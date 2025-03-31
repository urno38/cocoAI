import json
import re

import pandas as pd

from common.AI_API import ask_Mistral
from common.keys import MISTRAL_API_KEY_PAYANTE
from common.logconfig import LOGGER
from common.path import COMMERCIAL_DOCUMENTS_PATH, rapatrie_file
from common.pdf_document import process_file_by_Mistral_OCR


def mrkd2json(inp):
    lines = inp.split("\n")
    ret = []
    keys = []
    for i, l in enumerate(lines):
        if i == 0:
            keys = [_i.strip() for _i in l.split("|")]
        elif i == 1:
            continue
        else:
            ret.append(
                {
                    keys[_i]: v.strip()
                    for _i, v in enumerate(l.split("|"))
                    if _i > 0 and _i < len(keys) - 1
                }
            )
    return json.dumps(ret, indent=4)


def replace_figures(text):
    # Regular expression pattern to match figures in the form $number$
    pattern = re.compile(r"\$(-?[0-9]+(\.[0-9]+)?)\$")

    # Replace the matched pattern with just the number
    replaced_text = pattern.sub(r"\1", text)

    return replaced_text


def mrkd2df(inp):
    lines = inp.split("\n")
    ret = []
    keys = []
    for i, l in enumerate(lines):
        if i == 0:
            keys = [_i.strip() for _i in l.split("|")]
            # print(keys)
            # print(len(keys))
        elif i == 1:
            continue
        else:
            # print(l)
            # print(l.split("|"))
            # print(len(l.split("|")))
            ret.append(
                {
                    keys[_i]: v.strip()
                    for _i, v in enumerate(l.split("|"))
                    if _i < len(keys)
                }
            )
    # print(json.dumps(ret, indent = 4))
    # return pd.DataFrame.from_dict(json.dumps(ret, indent = 4))
    return pd.DataFrame.from_dict(ret)


def extract_markdown_tables(text):
    # Regular expression pattern to match Markdown tables with optional alignment
    table_pattern = re.compile(r"(\|.*\|\n\|[-:| ]+\|\n(\|.*\|*\n?)+)", re.MULTILINE)

    # Find all matches of the pattern in the text
    tables = table_pattern.findall(text)

    # Extract the full table strings from the matches
    extracted_tables = [match[0] for match in tables]

    return extracted_tables


# def get_mistral_answer(request, model="ministral-8b-latest"):

#     client = Mistral(api_key=MISTRAL_API_KEY_PAYANTE)

#     LOGGER.debug(f"we ask Mistral with the model {model}")
#     chat_response = client.chat.complete(
#         model=model,
#         messages=[
#             {
#                 "role": "user",
#                 "content": [
#                     TextChunk(text=request),
#                 ],
#             }
#         ],
#         response_format={"type": "json_object"},
#         temperature=0,
#     )
#     LOGGER.debug(f"the answer is {chat_response.choices[0].message.content}")

#     return chat_response.choices[0].message.content


def main(salaire_path):

    pdf_file_path = rapatrie_file(salaire_path)

    ocr_response = process_file_by_Mistral_OCR(pdf_file_path)
    response_dict = json.loads(ocr_response.model_dump_json())

    ocr_markdown = response_dict["pages"][0]["markdown"]
    ocr_markdown = replace_figures(ocr_markdown)

    request = (
        f"Voici le bulletin de salaire en markdown:\n\n{ocr_markdown}\n.\n"
        "Extrais toutes les informations au format pandas"
    )

    tables = extract_markdown_tables(ocr_markdown)

    # model="ministral-8b-latest"
    content = ask_Mistral(api_key=MISTRAL_API_KEY_PAYANTE, prompt=request)
    df = mrkd2df(tables[0])

    response_dict2 = json.loads(content)
    json_path = pdf_file_path.with_suffix(".json")
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(response_dict2, ensure_ascii=False))
        LOGGER.debug(json_path.resolve())


if __name__ == "__main__":

    CHIEN_QUI_FUME_PATH = (
        COMMERCIAL_DOCUMENTS_PATH
        / "2 - DOSSIERS à l'ETUDE"
        / "CHIEN QUI FUME (Le) - 75001 PARIS - 33 Rue du PONT-NEUF"
    )

    # pdf_path = Path(r"C:\Users\lvolat\Desktop\Echeancier def 240507 MAISON MULOT SAS.pdf")
    SOCIAL = list(CHIEN_QUI_FUME_PATH.glob("*SOCIAL*"))[0]
    PAIE = SOCIAL / "PAIE 10"

    salaires_list = list(PAIE.glob("*Dernier*")) + list(PAIE.glob("*Normal*"))

    for salaire_path in [salaires_list[3]]:
        main(salaire_path)
