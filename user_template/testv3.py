# script pour demander un output structuré à partir d'un document
# notamment une liasse fiscale

import base64
import json
import os
from io import BytesIO

# Import required libraries
from pathlib import Path

import pandas as pd
from mistralai import DocumentURLChunk, ImageURLChunk, Mistral, TextChunk
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter

from cocoAI.masse_salariale import data_uri_to_bytes, parse_pdf
from common.AI_API import ask_Mistral
from common.folder_tree import get_enseigne_folder_path
from common.keys import MISTRAL_API_KEY_PAYANTE
from common.logconfig import LOGGER
from common.path import load_json_file, rapatrie_file
from common.pdf_document import process_file_by_Mistral_OCR, request_file_nature


def encode_image(image_obj):
    if isinstance(image_obj, Image.Image):  # Check if it's already a PIL Image
        img = image_obj
    else:  # Otherwise, try opening it as a path
        img = Image.open(image_obj)
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


# Function to perform inference for image description
def interpret_image(image_path, prompt=None):

    client = Mistral(api_key=MISTRAL_API_KEY_PAYANTE)

    # Load and encode the image
    image_base64 = encode_image(image_path)  # Prompt for the Pixtral model
    if prompt is None:
        prompt = "Extrais du document joint les codes à deux ou trois caractères et tous les montants en euros à sa droite. Les codes sont situés à gauche du montant. Présente le résultat sous forme d'un json dont les clés sont les codes et les valeurs les montants."
    # Prepare input for the Pixtral API
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                },
            ],
        }
    ]
    # Perform inference
    response = client.chat.complete(
        model="pixtral-large-latest",
        messages=messages,
        max_tokens=300,
        response_format={
            "type": "json_object",
        },
    )
    # Return the model's output
    return response.choices[0].message.content


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


def export_image(image, origindoc_path):
    try:
        parsed_image = data_uri_to_bytes(image.image_base64)
        outputimage_path = origindoc_path.parent / (
            origindoc_path.stem + "_" + image.id
        )
        with open(outputimage_path, "wb") as file:
            file.write(parsed_image)
        print(f"Image successfully exported to {outputimage_path.resolve()}")
    except Exception as e:
        print(f"An error occurred while exporting the image: {e}")


def analyse_with_ocr(pdf_file, mistral_tmp_folder):

    api_key = MISTRAL_API_KEY_PAYANTE  # Replace with your API key
    client = Mistral(api_key=api_key)
    # Upload PDF file to Mistral's OCR service
    uploaded_file = client.files.upload(
        file={
            "file_name": pdf_file.stem,
            "content": pdf_file.read_bytes(),
        },
        purpose="ocr",
    )

    # Get URL for the uploaded file
    signed_url = client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)

    # Process PDF with OCR, including embedded images
    pdf_response = client.ocr.process(
        document=DocumentURLChunk(document_url=signed_url.url),
        model="mistral-ocr-latest",
        include_image_base64=True,
    )

    # Convert response to JSON format
    response_dict = json.loads(pdf_response.model_dump_json())

    # j exporte toutes les images dans un dossier temporaire
    md_output_path = mistral_tmp_folder / (pdf_file.stem + "_output.md")
    with open(md_output_path, "w", encoding="utf-8") as f:
        for page in pdf_response.pages:
            f.write(page.markdown)
            for image in page.images:
                export_image(image, md_output_path)

    return pdf_response


pdf_path = Path(
    r"C:\Users\lvolat\COMPTOIRS ET COMMERCES\DATALAKE - Documents\LA_RENAISSANCE_827953415\BISTROT_RENAISSANCE\REFERENCE_DOCUMENTS\DOCUMENTATION_FINANCIERE\BILANS_CA\liasse_23_is_renaissance.pdf"
)
siret = "82795341500011"
dest_enseigne_folder = get_enseigne_folder_path(siret)
TMP = dest_enseigne_folder / "WORK_DOCUMENTS"
MISTRAL_TMP = dest_enseigne_folder / "MISTRAL_FILES" / pdf_path.stem
MISTRAL_TMP.mkdir(exist_ok=True)


# pdf_file_path = rapatrie_file(pdf_path)
# del pdf_path  # securite pour eviter de toucher ulterieurement au fichier d'origine


# # Exemple d'utilisation
# path_list = split_pdf(pdf_file_path)


# # je fais passer l'OCR une fois
# for path in path_list:
#     assert path.is_file()
#     pdf_response = analyse_with_ocr(path, MISTRAL_TMP)

# # les images sont produites
# # je les interprete via pixtral
# for jpeg_path in list(MISTRAL_TMP.glob("*.jpeg"))[:2]:
#     LOGGER.debug(f"Analysis {jpeg_path}")
#     prompt = "Extrais du document joint les codes à deux ou trois caractères et tous les montants en euros à sa droite. Les codes sont situés à gauche du montant. Présente le résultat sous forme d'un json dont les clés sont les codes et les valeurs les montants."
#     output = interpret_image(jpeg_path, prompt)
#     with open(jpeg_path.with_suffix(".json"), "w", encoding="utf-8") as f:
#         f.write(output.rstrip('"') + "}" if not output.endswith("}") else output)

dfl = []
for i, json_path in enumerate(MISTRAL_TMP.glob("*.json")):
    LOGGER.debug(json_path)
    print(load_json_file(json_path))
    tmp = pd.DataFrame.from_dict(load_json_file(json_path), orient="index")
    dfl.append(tmp)

df = pd.concat(dfl)
print(dest_enseigne_folder / "MISTRAL_FILES" / "dftotal.csv")
df.to_csv(dest_enseigne_folder / "MISTRAL_FILES" / "dftotal.csv")
