import getpass
import logging
import os
import re
import shutil
import subprocess
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from common.logconfig import LOGGER

# definition du path vers le one drive comptoirs et commerces
if getpass.getuser() == "lvolat":
    USER_PATH = Path(r"C:\Users") / getpass.getuser()
    PROGRAMFILES_PATH = Path(r"C:\Program Files")
    TESSERACT_EXE_PATH = PROGRAMFILES_PATH / "Tesseract-OCR" / "tesseract.exe"
elif getpass.getuser() == "antoninbertuol":
    USER_PATH = Path("/Users/") / getpass.getuser()
else:
    raise ValueError("not implemented, please write the paths concerning the user")


DOCUMENTS_PATH = USER_PATH / "Documents"
DESKTOP_PATH = USER_PATH / "Desktop"

# One Drive
COMPTOIRS_ET_COMMERCES_PATH = USER_PATH / "COMPTOIRS ET COMMERCES"
COMMERCIAL_DOCUMENTS_PATH = COMPTOIRS_ET_COMMERCES_PATH / "COMMERCIAL - Documents"
DATALAKE_PATH = COMPTOIRS_ET_COMMERCES_PATH / "DATALAKE - Documents"

# CocoAI
COCOAI_PATH = DOCUMENTS_PATH / "cocoAI"
DATA_PATH = COCOAI_PATH / "data"
WORK_PATH = COCOAI_PATH / "work"
TMP_PATH = COCOAI_PATH / "tmp"
OUTPUT_PATH = COCOAI_PATH / "work" / "output"
COMMON_PATH = COCOAI_PATH / "common"
DATABANK_PATH = COMMON_PATH / "databank.yaml"
PPTX_TEMPLATE_PATH = DATA_PATH / "templates" / "template_memorandum.pptx"


# URL d'ACCES AUX API
PAPPERS_API_URL = "https://api.pappers.fr/v2"
OPENDATA_PARIS_URL = "https://opendata.paris.fr/api/explore/v2.1"


def check_extension(path, extension=".json"):
    # logging.debug(path, extension, path.suffix.lower())
    if path.suffix.lower() == extension:
        return True
    else:
        logging.debug(f"{path} is meant to have {extension} as extension")
        return False


def create_parent_directory(path):
    # Check if the parent directory exists, and create it if it doesn't
    parent_dir = path.parent

    if not parent_dir.exists():
        parent_dir.mkdir(parents=True)
        logging.debug(f"Created parent directory: {parent_dir}")
    else:
        pass
        # logging.debug(f"Parent directory already exists: {parent_dir}")

    return


def calculer_taille_fichier_mo(chemin_fichier):
    try:
        taille_octets = os.path.getsize(chemin_fichier)
        taille_mo = taille_octets / (1024 * 1024)  # Conversion en mégaoctets
        return taille_mo
    except OSError as e:
        return f"Erreur : {e}"


def get_out_path(label, kind, number, create=True):
    if number is None or number == "":
        path = OUTPUT_PATH / f"{kind}_{label}"
    else:
        path = OUTPUT_PATH / f"{kind}_{label}_{number}"
    if create:
        path.mkdir(exist_ok=True, parents=True)
    LOGGER.debug(f"output folder is {path}")
    return path


def make_unix_compatible(name):
    """
    Transforms a file or directory name to be Unix-compatible.

    This function replaces spaces with underscores and removes
    any characters that are not valid for Unix systems.

    Args:
        name (str): The name to be transformed.

    Returns:
        str: The transformed Unix-compatible name.
    """
    # Strip spaces
    if "." in name:
        name = ".".join([n.strip() for n in name.split(".")])

    name = name.strip()
    # Replace spaces with underscores
    name = name.replace("'", "_")
    name = name.replace(" ", "_")
    name = name.replace(")", "")
    name = name.replace("(", "")
    name = name.replace(". ", "_")
    name = name.replace("é", "e")
    name = name.replace("è", "e")
    name = name.replace("à", "a")
    # Remove invalid characters for Unix
    # name = re.sub(r"[^a-zA-Z0-9._-]", "", name)
    name = re.sub("_+", "_", name)
    name = re.sub("-+", "-", name)
    name = re.sub("_-_", "_", name)
    name = re.sub("_+", "_", name)
    return name


def get_unix_compatible_path(path_obj):
    """
    Transforms a path into a Unix-compatible path.

    This function takes a Path object and transforms each component of the path
    to be compatible with Unix naming conventions.

    Args:
        path_obj (Path): The Path object representing the path to be transformed.

    Returns:
        Path: A new Path object that is Unix-compatible.
    """
    # Apply transformation to each component of the path
    # [1:] pour ne pas prendre la lettre du lecteur
    unix_compatible_parts = [path_obj.parts[0]] + [
        make_unix_compatible(part) for part in path_obj.parts[1:]
    ]
    # Reconstruct the Unix-compatible path
    unix_compatible_path = Path(*unix_compatible_parts)
    return unix_compatible_path


def rename_file_unix_compatible(path: Path):
    compatible_path = get_unix_compatible_path(Path(path))
    create_parent_directory(compatible_path)
    os.rename(path, compatible_path)
    LOGGER.debug(f"file renamed from {path} to {compatible_path}")
    return compatible_path


def truncate_path_to_parent(path, parent_path):
    # Create a Path object
    if not isinstance(path, Path):
        full_path = Path(path)
    else:
        full_path = path

    # Iterate through the parents to find the desired parent directory
    for parent in full_path.parents:
        if parent == parent_path:
            # The remaining part of the path
            remaining_path = full_path.relative_to(parent)
            return parent, remaining_path

    # If the parent directory is not found, return the original path and an empty remaining path
    return full_path, Path()


def rapatrie_file(filepath, dest_folder=DATA_PATH):
    LOGGER.info(f"source file {filepath}")
    assert filepath.is_file()
    filepath = Path(filepath)
    # y a des fichiers bizarres quelquefois qui trainent, je les convertis arbitrairement
    if filepath.suffix == ".PDF":
        shutil.move(filepath, filepath.with_suffix(".pdf"))

    if not filepath.is_relative_to(dest_folder):
        if filepath.is_relative_to(COMMERCIAL_DOCUMENTS_PATH):
            parent, rel_path = truncate_path_to_parent(
                filepath, COMMERCIAL_DOCUMENTS_PATH
            )
            destpath = get_unix_compatible_path(dest_folder / rel_path)
        else:
            destpath = get_unix_compatible_path(dest_folder / filepath.name)

        if not destpath.exists():
            destpath.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(filepath, destpath)
            LOGGER.debug(f"{filepath} has been copied to {destpath.parent}")
        else:
            LOGGER.debug(f"{filepath.name} already exists in {destpath.parent.name}")
    else:
        destpath = filepath

    LOGGER.info(f"work file {destpath}")
    return destpath


def is_photo(file_path):
    try:
        # Attempt to open the file as an image
        with Image.open(file_path) as img:
            # If successful, it is likely a photo
            return True
    except (UnidentifiedImageError, IOError):
        # If an error occurs, it is not a photo
        return False


def is_video(file_path):
    try:
        # Use ffmpeg to probe the file
        result = subprocess.run(
            ["ffmpeg", "-i", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        # Check the output for video stream information
        return "Video:" in result.stderr
    except Exception as e:
        return False


if __name__ == "__main__":

    """
    path = obtain_output_folder("BISTROT_VALOIS", "siret",siret)
    logging.debug(path)
    logging.debug(USER, DOCUMENTS_PATH)
    """

    # # Exemple d'utilisation
    # chemin_compatible = get_unix_compatible_path(
    #     Path(
    #         r"C:\Users\lvolat\Documents\cocoAI\work\output\bail_Annexe 6 a) - Bail du 1er septembre 1995\slides_results.pdf"
    #     )
    # )
    # print(chemin_compatible)
    # filepath = Path(
    #     r"C:\Users\lvolat\COMPTOIRS ET COMMERCES\COMMERCIAL - Documents\2 - DOSSIERS à l'ETUDE\CHIEN QUI FUME (Le) - 75001 PARIS - 33 Rue du PONT-NEUF\3. DOCUMENTATION FINANCIÈRE\2022 - GALLA - GL.xlsx"
    # ).resolve()
    # print(filepath)
    # print(COMMERCIAL_DOCUMENTS_PATH)
    # new_file_path = rapatrie_file(filepath)

    # # check if a file is a photo
    # # Example usage
    # if is_photo(filepath):
    #     print(f"{filepath} is a photo.")
    # else:
    #     print(f"{filepath} is not a photo.")

    # Example usage
    file_path = Path(
        r"C:\Users\lvolat\COMPTOIRS ET COMMERCES\COMMERCIAL - Documents\2 - DOSSIERS à l'ETUDE\BISTROT VALOIS (Le) - 75001 PARIS - 1 Bis Place de VALOIS\12. PHOTOS\IMG_1400.mov"
    )
    if is_video(file_path):
        print(f"{file_path} is a video.")
    else:
        print(f"{file_path} is not a video.")
