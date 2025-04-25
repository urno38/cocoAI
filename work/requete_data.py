from pathlib import Path
import fitz  # PyMuPDF
from transformers import pipeline


# Extraction de texte depuis un PDF
def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


# Résumer le texte avec un modèle pré-entrainé
def summarize_text(text, max_length=130, min_length=30):
    summarizer = pipeline("summarization")
    summary = summarizer(
        text, max_length=max_length, min_length=min_length, do_sample=False
    )
    return summary[0]["summary_text"]


# print("toto")
# Exemple d'utilisation
file_path = Path(
    "../data/CSV - Comptes sociaux 2022.pdf"
)  # Remplace avec ton fichier PDF
text = extract_text_from_pdf(file_path)
summary = summarize_text(text)

print("Résumé :")
print(summary)
