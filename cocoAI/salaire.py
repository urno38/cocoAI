import json
import re

import pandas as pd
from mistralai import Mistral

from common.keys import MISTRAL_API_KEY_PAYANTE
from common.path import COMMERCIAL_ONE_DRIVE_PATH, rapatrie_file


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


def process_pdf_by_Mistral(pdf_path):
    client = Mistral(api_key=MISTRAL_API_KEY_PAYANTE)
    uploaded_pdf = client.files.upload(
        file={
            "file_name": pdf_file_path.name,
            "content": open(pdf_file_path, "rb"),
        },
        purpose="ocr",
    )
    client.files.retrieve(file_id=uploaded_pdf.id)
    signed_url = client.files.get_signed_url(file_id=uploaded_pdf.id)

    client2 = Mistral(api_key=MISTRAL_API_KEY_PAYANTE)
    ocr_response = client2.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": signed_url.url,
        },
    )
    return ocr_response


def mrkd2df(inp):
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


from mistralai import Mistral, TextChunk


def get_request(request):
    client = Mistral(api_key=MISTRAL_API_KEY_PAYANTE)

    # Get structured response from model
    chat_response = client.chat.complete(
        model="ministral-8b-latest",
        messages=[
            {
                "role": "user",
                "content": [
                    TextChunk(text=request),
                ],
            }
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    return chat_response.choices[0].message.content


CHIEN_QUI_FUME_PATH = (
    COMMERCIAL_ONE_DRIVE_PATH
    / "2 - DOSSIERS à l'ETUDE"
    / "CHIEN QUI FUME (Le) - 75001 PARIS - 33 Rue du PONT-NEUF"
)


# pdf_path = Path(r"C:\Users\lvolat\Desktop\Echeancier def 240507 MAISON MULOT SAS.pdf")
SOCIAL = list(CHIEN_QUI_FUME_PATH.glob("*SOCIAL*"))[0]
PAIE = SOCIAL / "PAIE 10"
pdf_path = list(PAIE.glob("*Djiedji*"))[0]
pdf_file_path = rapatrie_file(pdf_path)
ocr_response = process_pdf_by_Mistral(pdf_file_path)
response_dict = json.loads(ocr_response.model_dump_json())

# display(Markdown(response_dict["pages"][0]["markdown"]))
ocr_markdown = response_dict["pages"][0]["markdown"]
ocr_markdown = replace_figures(ocr_markdown)

request = (
    f"Voici le bulletin de salaire en markdown:\n\n{ocr_markdown}\n.\n"
    "Extrais toutes ces informations au format pandas"
)

tables = extract_markdown_tables(ocr_markdown)
content = get_request(request)
