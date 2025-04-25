from pprint import pprint
import pdfplumber
from transformers import pipeline
import sys

sys.path.append(r"C:\Users\lvolat\Documents\cocoAI")
from common.path import DATA_PATH


def extract_text_from_pdf(pdf_path):
    """
    Extrait le texte d'un fichier PDF.

    :param pdf_path: Chemin vers le fichier PDF.
    :return: Texte extrait du PDF.
    """
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text


def extract_information(text, question):
    """
    Utilise un modèle d'IA pour extraire de l'information pertinente du texte.

    :param text: Texte à partir duquel extraire l'information.
    :param question: Question pour laquelle extraire l'information.
    :return: Réponse extraite.
    """
    # Charger un modèle d'IA pour l'extraction d'information
    nlp = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

    # Extraire l'information
    result = nlp(question=question, context=text)
    return result


def main(pdf_path):

    # Extraire le texte du PDF
    text = extract_text_from_pdf(pdf_path)
    print("Texte extrait du PDF :")
    print(text)

    # Question pour extraire l'information
    question = "Quel est le sujet principal du document ?"

    # Extraire l'information pertinente
    result = extract_information(text, question)
    print("\nRéponse extraite :")
    print(result)


if __name__ == "__main__":
    # Chemin vers le fichier PDF
    PDF_FOLDER_PATH = (
        DATA_PATH
        / "CHIEN QUI FUME (Le) - 75001 PARIS - 33 Rue du PONT-NEUF"
        / "1. DOSSIER AFFAIRE ACC - [SOCIÉTÉ]"
    )
    pdf_path = list(PDF_FOLDER_PATH.glob("*.pdf"))[0]
    # print(DATA_PATH) 
    pprint(pdf_path)
    print(f"Extraction du texte du fichier PDF: {pdf_path}")
    main(pdf_path)
    # extract_pdf(pdf_path, WORK_PATH / "output")
