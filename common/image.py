import io
import os
from pathlib import Path
from pprint import pprint

from common.path import WORK_PATH
from common.pdf_document import extract_images_from_pdf
import fitz
import numpy as np
from PIL import Image


def detect_monochrome_images(folder_path, threshold=2):
    """
    Détecte les images contenant peu de variations de couleur dans un dossier et retourne un dictionnaire
    associant le nom du fichier à sa couleur dominante en format hexadécimal.

    Paramètres :
    - folder_path : chemin du dossier contenant les images.
    - threshold : nombre maximum de couleurs uniques pour considérer une image comme quasi-monochrome.
    """
    color_mapping = {}

    # Vérifier si le dossier existe
    if not os.path.isdir(folder_path):
        raise FileNotFoundError(
            f"Le dossier '{folder_path}' n'existe pas ou n'est pas un répertoire valide."
        )

    # Parcourir tous les fichiers du dossier
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        try:
            # Vérifier si c'est un fichier image
            if not os.path.isfile(file_path):
                continue

            # Ouvrir l'image et la convertir en RGB
            with Image.open(file_path).convert("RGB") as img:
                img_array = np.array(img)

                # Trouver les couleurs uniques dans l'image
                unique_colors = np.unique(
                    img_array.reshape(-1, img_array.shape[-1]), axis=0
                )

                # Si le nombre de couleurs uniques est inférieur au seuil, ajouter au dictionnaire
                if len(unique_colors) <= threshold:
                    avg_color = np.mean(unique_colors, axis=0).astype(int)
                    color_hex = "#{:02x}{:02x}{:02x}".format(*avg_color)
                    color_mapping[filename] = color_hex

        except Exception as e:
            logging.error(f"Erreur avec le fichier '{filename}': {e}")

    return color_mapping


def get_image_size(image):
    with Image.open(image) as ref_img:
        return ref_img.size


def detect_same_size_images(folder_path, reference_image_path):
    """
    Détecte les images ayant la même taille qu'une image de référence dans un dossier.

    Paramètres :
    - folder_path : chemin du dossier contenant les images.
    - reference_image_path : chemin de l'image de référence.

    Retourne :
    - Une liste des noms de fichiers ayant la même taille que l'image de référence.
    """
    same_size_images = []

    # Ouvrir l'image de référence pour obtenir sa taille
    try:
        ref_size = get_image_size(reference_image_path)
    except Exception as e:
        raise ValueError(f"Impossible d'ouvrir l'image de référence : {e}")

    # Vérifier si le dossier existe
    if not os.path.isdir(folder_path):
        raise FileNotFoundError(
            f"Le dossier '{folder_path}' n'existe pas ou n'est pas un répertoire valide."
        )

    # Parcourir tous les fichiers du dossier
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        try:
            # Vérifier si c'est un fichier image
            if not os.path.isfile(file_path):
                continue

            # Ouvrir l'image et vérifier sa taille
            with Image.open(file_path) as img:
                if img.size == ref_size:
                    same_size_images.append(filename)
        except Exception as e:
            logging.error(f"Erreur avec le fichier '{filename}': {e}")

    return same_size_images


def detect_colors_in_image(image_path):
    """
    Détecte le nombre de couleurs uniques dans une image et retourne ce nombre avec la liste des couleurs en hexadécimal.

    Paramètres :
    - image_path : chemin de l'image à analyser.

    Retourne :
    - Un tuple (nombre de couleurs, liste des couleurs en hexadécimal)
    """
    try:
        with Image.open(image_path).convert("RGB") as img:
            img_array = np.array(img)

        unique_colors = np.unique(img_array.reshape(-1, img_array.shape[-1]), axis=0)
        color_hex_list = [
            "#{:02x}{:02x}{:02x}".format(*color) for color in unique_colors
        ]

        return len(unique_colors), color_hex_list
    except Exception as e:
        raise ValueError(f"Impossible d'analyser l'image : {e}")


def get_the_biggest_image_in_folder(folder_path):
    max_size = 0
    for image_path in folder_path.glob("*.png"):
        with Image.open(image_path) as im:
            if im.size[0] * im.size[1] > max_size:
                max_size = im.size[0] * im.size[1]
                path = image_path
    return path


def main():

    pdf_path = r"c:\Users\lvolat\Downloads\328311052_004.pdf"
    dossier_images = WORK_PATH / "extracted_images"

    extracted_images = extract_images_from_pdf(pdf_path, dossier_images)
    logging.debug(f"Successfully extracted {len(extracted_images)} images:")
    for img_path in extracted_images:
        logging.debug(f"- {img_path}")

    monochrome_images = detect_monochrome_images(dossier_images)

    reference_image = list(monochrome_images.keys())[1]
    same_size_images = detect_same_size_images(
        dossier_images, dossier_images / reference_image
    )

    for im in same_size_images:
        if im not in list(monochrome_images.keys()):
            num_colors, colors_hex = detect_colors_in_image(dossier_images / im)
            logging.debug(f"Nombre de couleurs : {num_colors}")
            logging.debug(f"Couleurs : {colors_hex}")

    logging.debug(same_size_images)


if __name__ == "__main__":
    main()
