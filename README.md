# cocoAI

*co*mptoir et *co*mmerce *AI*

## Installation

### version mac pour Antonin 

1. Exécuter ```install.bash```
2. récupérer les clés et les enregistrer dans common/keys.py
3. Générer une clé ssh et l'envoyer sur le github  

|            |                    | Windows     | Mac          |     |
| ---------- | ------------------ | ----------- | ------------ | --- |
|  | fichier à exécuter | install.ps1 | install.bash |    |




## to do list

- implémenter la charte graphique de CC dans les beamers
- commenter les fonctions et faire des logs d'impression intermédiaires remplacer les print par des logs propres
- les bénéficiaires indirects ont un diagramme à améliorer : pointillés et sans les holdings intermédiaires
- résoudre tous les TODO

## Notes perso

Regarder

- dealmkr :
- alvomarket : concurrent de dealmkr
- Professionnel de la fusion acquisition, suite pro
- Dataiku
- Make
  Webhook, API on y croit ++
  Agent AI voir comment l'implémenter

  Claude.ai aller voir les avantages

## POC Dataiku

### récupérer données brutes

data Pappers téléchargées en [zabal agriculture]

### résumer et faire une présentation à partir de données brutes

Dataiku, ça me semble hasardeux.

### Requête faite avec ChatGPT

<https://chatgpt.com/c/6797984c-5568-8003-9a39-0fae1a7ffdf9>

```bash
Pour accomplir cette tâche, voici une approche systématique combinant des outils logiciels et des techniques d’automatisation. Voici les étapes principales :

Étape 1 : Récupération et chargement des fichiers PDF
Chargement des fichiers PDF :

Vous pouvez utiliser des bibliothèques Python comme PyPDF2, PyMuPDF (fitz), ou PDFplumber pour lire et extraire le texte des fichiers PDF.
Si le PDF contient des images ou du texte non sélectionnable, utilisez un outil d'OCR (Reconnaissance Optique des Caractères) tel que Tesseract-OCR ou des API comme celles d’Adobe Acrobat ou de Google Vision.
Automatisation de la récupération :

Placez tous vos fichiers PDF dans un répertoire spécifique.
Parcourez automatiquement les fichiers du répertoire avec Python, en utilisant la bibliothèque os.
Étape 2 : Extraction et nettoyage des données
Extraction du texte brut :

Lisez chaque page du PDF et extrayez le texte brut.
Divisez le texte en sections structurées en fonction des en-têtes ou des mots-clés (par exemple : « Introduction », « Résumé », « Contexte »).
Nettoyage :

Supprimez les éléments superflus (espaces en trop, caractères spéciaux inutiles, en-têtes de pages répétitifs).
Utilisez des bibliothèques comme re pour le traitement des chaînes.
Étape 3 : Résumé et extraction des informations pertinentes
Résumé automatique :

Utilisez des modèles d’intelligence artificielle comme spaCy, Hugging Face Transformers (par exemple, avec des modèles comme BART ou T5), ou GPT.
Ces modèles peuvent condenser les informations tout en conservant les points clés.
Extraction ciblée :

Recherchez des informations spécifiques (noms, dates, chiffres, faits précis) à l'aide de modèles NLP comme Named Entity Recognition (NER) dans spaCy.
Filtrez des données selon vos besoins en définissant des mots-clés ou des expressions régulières.
Étape 4 : Organisation et stockage
Stockage structuré :

Enregistrez les données extraites et résumées dans un format facilement consultable, comme JSON, CSV, ou une base de données relationnelle (SQLite, PostgreSQL).
Classification :

Ajoutez des métadonnées (nom du fichier, date d’extraction, résumé) pour faciliter la recherche ultérieure.
Étape 5 : Automatisation
Utilisation de scripts :

Développez un script Python ou un workflow dans un outil comme Apache Airflow, qui s’exécute automatiquement chaque fois qu’un nouveau fichier est ajouté dans le répertoire des PDF.
Interface utilisateur (facultatif) :

Créez une interface utilisateur avec des outils comme Streamlit ou Flask pour simplifier les interactions avec l’automatisation.
Outils recommandés
Python Libraries :

Lecture de PDF : PyMuPDF, PDFplumber
OCR : Pytesseract
Traitement NLP : spaCy, Hugging Face Transformers, Sumy
Gestion de fichiers : os, glob
API :

OCR et résumé avancé : Google Cloud Vision, Amazon Textract, OpenAI GPT API
Flux de travail :

Automatisez avec des outils comme Airflow, Zapier ou Make (ex Integromat).
Exemple simplifié de code Python :
python
Copier
Modifier
import os
import fitz  # PyMuPDF
from transformers import pipeline

# Charger le modèle de résumé
summarizer = pipeline("summarization")

# Répertoire contenant les fichiers PDF
pdf_dir = "./pdf_files"

def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as pdf:
        for page in pdf:
            text += page.get_text()
    return text

def summarize_text(text):
    summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
    return summary[0]['summary_text']

def process_pdfs(directory):
    for file_name in os.listdir(directory):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(directory, file_name)
            text = extract_text_from_pdf(file_path)
            summary = summarize_text(text)
            print(f"Résumé pour {file_name} :\n{summary}\n")

process_pdfs(pdf_dir)
En utilisant ces étapes, vous pouvez mettre en place une solution robuste pour analyser et automatiser la gestion de vos fichiers PDF. Avez-vous besoin d’aide pour adapter ce workflow ou d'un autre exemple ?
```

[zabal agriculture]: https://zabal-agriculture.opendata-paysbasque.fr/explore/dataset/pappers/information/
