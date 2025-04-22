# script pour demander un output structuré à partir d'un document
# notamment une liasse fiscale

import json
import os
from pathlib import Path

from PyPDF2 import PdfReader, PdfWriter

from cocoAI.folder_tree import get_enseigne_folder
from common.AI_API import ask_Mistral
from common.keys import MISTRAL_API_KEY_PAYANTE
from common.logconfig import LOGGER
from common.path import rapatrie_file
from common.pdf_document import process_file_by_Mistral_OCR, request_file_nature


def split_pdf(input_pdf_path):
    # Vérifie si le fichier existe
    if not os.path.isfile(input_pdf_path):
        print(f"Le fichier {input_pdf_path} n'existe pas.")
        return

    # Ouvre le fichier PDF
    with open(input_pdf_path, "rb") as input_pdf_file:
        reader = PdfReader(input_pdf_file)
        num_pages = len(reader.pages)

        # Vérifie si le PDF a plusieurs pages
        if num_pages > 1:
            print(
                f"Le fichier {input_pdf_path} contient {num_pages} pages. Division en cours..."
            )

            path_list = []
            # Divise le PDF en fichiers individuels
            for i in range(num_pages):
                writer = PdfWriter()
                writer.add_page(reader.pages[i])

                # Définit le nom du fichier de sortie
                output_pdf_path = (
                    f"{os.path.splitext(input_pdf_path)[0]}_page_{i+1}.pdf"
                )

                # Écrit le fichier PDF de sortie
                with open(output_pdf_path, "wb") as output_pdf_file:
                    writer.write(output_pdf_file)

                print(f"Page {i+1} sauvegardée dans {output_pdf_path}")

                path_list.append(Path(output_pdf_path))
        else:
            print(f"Le fichier {input_pdf_path} contient une seule page.")

        return path_list


pdf_path = Path(
    r"C:\Users\lvolat\COMPTOIRS ET COMMERCES\DATALAKE - Documents\LA_RENAISSANCE_827953415\BISTROT_RENAISSANCE\REFERENCE_DOCUMENTS\DOCUMENTATION_FINANCIERE\BILANS_CA\liasse_23_is_renaissance.pdf"
)
siret = "82795341500011"
dest_enseigne_folder = get_enseigne_folder(siret)
TMP = dest_enseigne_folder / "WORK_DOCUMENTS"


pdf_file_path = rapatrie_file(pdf_path)
del pdf_path  # securite pour eviter de toucher ulterieurement au fichier d'origine


# Exemple d'utilisation
path_list = split_pdf(pdf_file_path)

ocr_response = process_file_by_Mistral_OCR(path_list[0])

response_dict = json.loads(ocr_response.model_dump_json())
ocr_markdown = response_dict["pages"][0]["markdown"]

request = (
    "Extrais toutes les informations de ce document au format markdown"
    + "\n\n\n"
    + ocr_markdown
)

request_file = TMP / pdf_file_path.with_suffix(".request").name
with open(request_file, "w", encoding="utf-8") as f:
    f.write(request)
    LOGGER.debug(f"request exported to {request_file}")

model = "mistral-large-latest"
chat_response = ask_Mistral(
    api_key=MISTRAL_API_KEY_PAYANTE,
    prompt=request,
    model=model,
    # json_only=True,
)


response = chat_response.choices[0].message.content

txt_path = TMP / pdf_file_path.with_suffix(".txt").name
with open(txt_path, "w", encoding="utf-8") as f:
    f.write(response)
    LOGGER.debug(txt_path.resolve())


LOGGER.info(f"Mistral did answer in {txt_path}")
