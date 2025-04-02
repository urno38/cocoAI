import io
import json
import os
import shutil

import fitz
import pytesseract
import requests
from mistralai import Mistral
from PIL import Image

from cocoAI.company import get_infos_from_a_siret
from cocoAI.folder_tree import create_complete_folder_tree
from common.AI_API import ask_Mistral
from common.keys import MISTRAL_API_KEY, MISTRAL_API_KEY_PAYANTE
from common.logconfig import LOGGER
from common.path import (
    COMMERCIAL_DOCUMENTS_PATH,
    TESSERACT_EXE_PATH,
    create_parent_directory,
    make_unix_compatible,
    rapatrie_file,
)

if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = str(TESSERACT_EXE_PATH)


def pdf_to_text(pdf_path):
    # Ouvrir le fichier PDF
    LOGGER.debug(f"Je processe le fichier pdf {pdf_path} avec tesseract")

    pdf_document = fitz.open(pdf_path)
    text = ""

    LOGGER.debug(f"{len(pdf_document)} pages")

    # Parcourir chaque page du PDF
    for page_num in range(len(pdf_document)):

        LOGGER.debug(f"page {page_num}")

        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()

        # Convertir l'image en mode RGB
        image = Image.open(io.BytesIO(pix.tobytes()))

        # Utiliser pytesseract pour effectuer l'OCR sur l'image
        page_text = pytesseract.image_to_string(image)
        text += page_text + "\n"

    LOGGER.info("Scan completed")
    return text


def convert_pdf_to_ascii(pdf_path, output_ascii_path=None, with_Mistral=False):

    if output_ascii_path is None:
        output_ascii_path = pdf_path.with_suffix(".txt")

    if not output_ascii_path.exists():
        if with_Mistral:
            ocr_response = process_file_by_Mistral_OCR(
                pdf_path, api_key=MISTRAL_API_KEY
            )
            response_dict = json.loads(ocr_response.model_dump_json())
            text = response_dict["pages"][0]["markdown"]
        else:
            text = pdf_to_text(pdf_path)
        with open(output_ascii_path, "w", encoding="utf-8") as f:
            f.write(text)
        LOGGER.debug(f"pdf converted to {output_ascii_path}")
    else:
        with open(output_ascii_path, encoding="utf-8") as f:
            text = "\n".join(f.readlines())
        LOGGER.debug(f"{output_ascii_path.resolve()} loaded")

    return output_ascii_path, text


def extract_images_from_pdf(pdf_path, output_dir):
    """
    Extract all images from a PDF file and save them to the specified output directory.

    Args:
        pdf_path (str): Path to the PDF file
        output_dir (str): Directory where images will be saved

    Returns:
        list: List of paths to saved images
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Open the PDF
    pdf_document = fitz.open(pdf_path)
    saved_images = []

    # Iterate through each page
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]

        # Get all images on the page
        image_list = page.get_images()

        # Process each image
        for img_index, img in enumerate(image_list):
            # Get the image data
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]

            # Get image extension
            ext = base_image["ext"]

            # Generate output filename
            image_filename = f"page{page_num + 1}_img{img_index + 1}.{ext}"
            image_path = os.path.join(output_dir, image_filename)

            # Save the image
            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)

            # Open with PIL for potential post-processing
            with Image.open(io.BytesIO(image_bytes)) as img:
                # Save with PIL to ensure proper format
                img.save(image_path, format=ext.upper())

            saved_images.append(image_path)

    pdf_document.close()
    return saved_images


def download_pdf(url, save_path):
    LOGGER.debug(url)
    response = requests.get(url)
    create_parent_directory(save_path)
    if response.status_code == 200:
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        LOGGER.info(f"PDF downloaded successfully: {save_path}")
    elif response.status_code == 404:
        LOGGER.debug(
            "Site de la mairie de Paris en maintenance, pas possible de télécharger le pdf"
        )
    else:
        LOGGER.info(response)
        LOGGER.error(f"Failed to download PDF. Status code: {response.status_code}")


def request_file_nature():

    types_possibles = [
        ("un bail commercial", "BAUX - QUITTANCE"),
        ("une quittance de loyer", "BAUX - QUITTANCE"),
        ("une taxe fonciere", "BAUX - QUITTANCE"),
        ("un appel de charges de copropriété", "BAUX - QUITTANCE"),
        (
            "une attestation de vigilance",
            "DOCUMENTATION_FINANCIERE/ATTESTATIONS DE REGULARITE IMPOTS URSSAF",
        ),
        (
            "une attestation de régularité",
            "DOCUMENTATION_FINANCIERE/ATTESTATIONS DE REGULARITE IMPOTS URSSAF",
        ),
        (
            "une attestation d'urssaf",
            "DOCUMENTATION_FINANCIERE/ATTESTATIONS DE REGULARITE IMPOTS URSSAF",
        ),
        ("un document financier", "DOCUMENTATION_FINANCIERE/BILANS - CA"),
        (
            "une attestation de chiffres d'affaires",
            "DOCUMENTATION_FINANCIERE/BILANS - CA",
        ),
        ("un document issu de la comptabilité", "DOCUMENTATION_FINANCIERE/BILANS - CA"),
        ("un tableau financier", "DOCUMENTATION_FINANCIERE/BILANS - CA"),
        (
            "un tableau d'amortissement d'emprunt bancaire",
            "DOCUMENTATION_FINANCIERE/EMPRUNTS",
        ),
        (
            "une attestation de compte courant d'associés",
            "DOCUMENTATION_FINANCIERE/COMPTES COURANTS",
        ),
        (
            "un document concernant un diagnostic amiante",
            "DOCUMENTATION_FINANCIERE/DIAGNOSTICS",
        ),
        (
            "un document concernant un diagnostic énergétique",
            "DOCUMENTATION_FINANCIERE/DIAGNOSTICS",
        ),
        (
            "un document concernant un diagnostic termites",
            "DOCUMENTATION_FINANCIERE/DIAGNOSTICS",
        ),
        ("un document concernant un emprunt", "DOCUMENTATION_FINANCIERE/EMPRUNTS"),
        ("un acte de vente signé", "JURIDIQUE_CORPORATE/ACTES SIGNES"),
        ("une autorisation bénéficiaire", "JURIDIQUE_CORPORATE/CORPORATE"),
        (
            "un compte rendu de conseil de surveillance ou d'organe de contrôle de la société",
            "JURIDIQUE_CORPORATE/CORPORATE",
        ),
        ("un PV d'Assemblée Générale", "JURIDIQUE_CORPORATE/CORPORATE"),
        ("un PV de décision de l'associé unique", "JURIDIQUE_CORPORATE/CORPORATE"),
        (
            "un document juridique lié à l'administration de la société",
            "JURIDIQUE_CORPORATE/CORPORATE",
        ),
        (
            "une attestation de bénéficiaire de la société",
            "JURIDIQUE_CORPORATE/CORPORATE",
        ),
        (
            "tous les états d'inscription du fond de commerce",
            "JURIDIQUE_CORPORATE/ETATS DES INSCRIPTIONS",
        ),
        (
            "un document qui définit le K bis",
            "JURIDIQUE_CORPORATE/K BIS - INSEE - STATUTS",
        ),
        ("un document INSEE", "JURIDIQUE_CORPORATE/K BIS - INSEE - STATUTS"),
        (
            "une immatriculation au registre SIRENE",
            "JURIDIQUE_CORPORATE/K BIS - INSEE - STATUTS",
        ),
        ("un statut", "JURIDIQUE_CORPORATE/K BIS - INSEE - STATUTS"),
        ("un document concernant les litiges", "JURIDIQUE_CORPORATE/LITIGES"),
        (
            "un acte de cession des titres de la société",
            "JURIDIQUE_CORPORATE/ORIGINE DE PROPRIETE DES TITRES",
        ),
        (
            "un acte de cession des titres de propriété du fonds de commerce",
            "JURIDIQUE_CORPORATE/ORIGINE DE PROPRIETE DU FONDS",
        ),
        (
            "un acte de nantissement des titres des parts sociales",
            "JURIDIQUE_CORPORATE/REGISTRES NANTISSEMENT DES TITRES",
        ),
        (
            "une attestation d'assurance",
            "JURIDIQUE_EXPLOITATION_ET_CONTRATS/ASSURANCE",
        ),
        (
            "une responsabilité civile d'exploitation",
            "JURIDIQUE_EXPLOITATION_ET_CONTRATS/ASSURANCE",
        ),
        (
            "un contrat d'assurance",
            "JURIDIQUE_EXPLOITATION_ET_CONTRATS/ASSURANCE",
        ),
        (
            "attestation de conformité de caisse",
            "JURIDIQUE_EXPLOITATION_ET_CONTRATS/CAISSE",
        ),
        (
            "un contrat de crédit-bail",
            "JURIDIQUE_EXPLOITATION_ET_CONTRATS/CONTRATS CREDITS BAUX",
        ),
        (
            "un contrat de location longue durée",
            "JURIDIQUE_EXPLOITATION_ET_CONTRATS/CONTRATS CREDITS BAUX",
        ),
        (
            "un contrat fournisseurs",
            "JURIDIQUE_EXPLOITATION_ET_CONTRATS/CONTRATS FOURNISSEURS",
        ),
        ("une licence IV", "JURIDIQUE_EXPLOITATION_ET_CONTRATS/LICENCE IV"),
        (
            "un document concernant la terrasse ou la voirie",
            "JURIDIQUE_EXPLOITATION_ET_CONTRATS/TERRASSE - VOIRIE",
        ),
        (
            "un rapport d'urbanisme",
            "JURIDIQUE_EXPLOITATION_ET_CONTRATS/URBANISME",
        ),
        ("un bulletin de paie", "SOCIAL/BULLETINS PAIE"),
        ("un bulletin de salaire", "SOCIAL/BULLETINS PAIE"),
        ("un contrat de travail", "SOCIAL/CONTRATS DE TRAVAIL"),
        ("un document de cotisations", "SOCIAL/COTISATIONS"),
        ("une lettre de démission", "SOCIAL/DEMISSIONS"),
        ("une liste du personnel", "SOCIAL/LISTE DU PERSONNEL"),
        (
            "un document qui concerne la mutuelle d'entreprise mais qui n'est pas un bulletin de salaire",
            "SOCIAL/MUTUELLE - PREVOYANCE",
        ),
        (
            "un document qui concerne la prévoyance d'entreprise mais qui n'est pas un bulletin de salaire",
            "SOCIAL/MUTUELLE - PREVOYANCE",
        ),
        (
            "un journal de paie",
            "SOCIAL/COTISATIONS",
        ),
        (
            "un document comptable relatif aux prestations sociales",
            "SOCIAL/COTISATIONS",
        ),
    ]

    # Trier la liste selon la partie après le slash dans la deuxième chaîne de caractères
    # types_possibles_tries = sorted(types_possibles, key=lambda x: x[1].split('/')[-1] if '/' in x[1] else x[1])

    request = "Soit un dictionnaire python di dont toutes les valeurs sont initialisées à False. Est ce que le document joint est :\n"
    for type, key in types_possibles:
        request += " - "
        request += f"{type} ? si oui, alors mets uniquement la clé '{key}' du dictionnaire di à True\n"

    request += "Ne renvoie que le dictionnaire di sous forme json sans commentaires"

    return request


def get_new_location_dictionary_path(file_path, ocr_response):

    response_dict = json.loads(ocr_response.model_dump_json())
    ocr_markdown = response_dict["pages"][0]["markdown"]

    request = request_file_nature() + "\n\n\n" + ocr_markdown

    request_file = file_path.with_suffix(".request")
    with open(request_file, "w", encoding="utf-8") as f:
        f.write(request)
        LOGGER.debug(f"request exported to {request_file}")

    # model="ministral-8b-latest"
    chat_response = ask_Mistral(
        api_key=MISTRAL_API_KEY_PAYANTE,
        prompt=request,
        model="mistral-large-latest",
        json_only=True,
    )
    json_dict = chat_response.choices[0].message.content

    response_dict2 = json.loads(json_dict)
    json_path = file_path.with_suffix(".json")
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(response_dict2, ensure_ascii=False))
        LOGGER.debug(json_path.resolve())

    return response_dict2


def process_file_by_Mistral_OCR(file_path, api_key=MISTRAL_API_KEY_PAYANTE):
    LOGGER.debug(f"let us give to the OCR {file_path}")
    client = Mistral(api_key=api_key)
    uploaded_file = client.files.upload(
        file={
            "file_name": file_path.name,
            "content": open(file_path, "rb"),
        },
        purpose="ocr",
    )
    client.files.retrieve(file_id=uploaded_file.id)
    signed_url = client.files.get_signed_url(file_id=uploaded_file.id)

    client2 = Mistral(api_key=api_key)
    ocr_response = client2.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": signed_url.url,
        },
    )
    return ocr_response


def analyse_pdf_document(pdf_path, siret):

    siren = int(str(siret)[:-5])
    dest_folder = create_complete_folder_tree(siren)
    entreprise_name, etablissement_name = get_infos_from_a_siret(siret)

    pdf_file_path = rapatrie_file(pdf_path)
    del pdf_path  # securite pour eviter de toucher ulterieurement au fichier d'origine

    ocr_response = process_file_by_Mistral_OCR(pdf_file_path)
    location_dict = get_new_location_dictionary_path(pdf_file_path, ocr_response)

    path_list = []
    for key, value in location_dict.items():
        if value:
            potential_path = (
                dest_folder
                / make_unix_compatible(etablissement_name)
                / "REFERENCE_DOCUMENTS"
            )
            for el in key.split("/"):
                potential_path = potential_path / make_unix_compatible(el)
            path_list.append(potential_path / pdf_file_path.name)

    if len(list(set(path_list))) == 0:
        LOGGER.critical(f"not any new path found for the doc {pdf_file_path}")

    if len(list(set(path_list))) > 1:
        LOGGER.warning(f"several locations foreseen for that document")
        LOGGER.warning(list(set(path_list)))

    for i, path in enumerate(list(set(path_list))):  # remove duplicates
        if i == 0:
            shutil.move(pdf_file_path, path)
            LOGGER.info(path)
            LOGGER.debug(f"new location {path_list[0]}")
        else:
            pass
            # si plusieurs path sont reconnus, alors je fais des symlinks pour gagner de la place
            # path_list[0].symlink_to(path)
            # LOGGER.debug(f"Symlink created at: {path.resolve()}")


def main(pdf_path, siret):
    analyse_pdf_document(pdf_path, siret)
    return


# Example usage
if __name__ == "__main__":

    # test extraction images d'un pdf
    # pdf_path = r"c:\Users\lvolat\Downloads\328311052_004.pdf"
    # output_dir = "extracted_images2"

    # try:
    #     extracted_images = extract_images_from_pdf(pdf_path, output_dir)
    #     LOGGER.debug(f"Successfully extracted {len(extracted_images)} images:")
    #     for img_path in extracted_images:
    #         LOGGER.debug(f"- {img_path}")
    # except Exception as e:
    #     LOGGER.error(f"Error extracting images: {str(e)}")

    # test telechargement pdf
    # pdf_url = "https://affichette-commerce.paris.fr/2015/Q_59/595230061%20002.pdf"  # Replace with the actual PDF URL
    # save_location = (
    #     WORK_PATH / "downloaded_pdf" / "download.pdf"
    # )  # Change the save location if needed
    # create_parent_directory(save_location)
    # download_pdf(pdf_url, save_location)

    # test scan de pdf
    # pdf_path = list(COMMERCIAL_ONE_DRIVE_PATH.rglob("*GILBERTE*/*BAIL*pdf"))[0]
    # print(pdf_path)

    # output_path, text = convert_pdf_to_ascii(pdf_path, Path("result.txt"))

    siret = "31013032300028"

    CHIEN_QUI_FUME_PATH = (
        COMMERCIAL_DOCUMENTS_PATH
        / "2 - DOSSIERS à l'ETUDE"
        / "CHIEN QUI FUME (Le) - 75001 PARIS - 33 Rue du PONT-NEUF"
    )

    SOCIAL = list(CHIEN_QUI_FUME_PATH.glob("*SOCIAL*"))[0]
    PAIE = SOCIAL / "PAIE 10"
    salaires_list = list(PAIE.glob("*Dernier*")) + list(PAIE.glob("*Normal*"))

    DOC_FINANCIERE = list(CHIEN_QUI_FUME_PATH.glob("*DOCUMENTATION FI*"))[0]
    DOCS = list(DOC_FINANCIERE.glob("*.pdf"))

    for path in [DOCS[3]]:
        main(path, siret)
