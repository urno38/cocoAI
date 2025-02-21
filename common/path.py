import logging
import os
import re
from pathlib import Path

from common.logconfig import LOGGER

USER = "lvolat"
if os.name == "posix":
    USER_PATH = Path("/Users/") / getpass.getuser()
elif os.name == "nt":
    USER_PATH = Path(r"C:\Users") / USER
DOCUMENTS_PATH = USER_PATH / "Documents"
# DOCUMENTS_PATH = USER_PATH / "OneDrive - COMPTOIRS ET COMMERCES\Documents"
COCOAI_PATH = DOCUMENTS_PATH / "cocoAI"
DATA_PATH = COCOAI_PATH / "data"
WORK_PATH = COCOAI_PATH / "work"
OUTPUT_PATH = COCOAI_PATH / "work" / "output"
COMMON_PATH = COCOAI_PATH / "common"
DATABANK_PATH = COMMON_PATH / "databank.yaml"
PROGRAMFILES_PATH = Path(r"C:\Program Files")
TESSERACT_EXE_PATH = PROGRAMFILES_PATH / "Tesseract-OCR" / "tesseract.exe"
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
        logging.info(f"Created parent directory: {parent_dir}")
    else:
        pass
        # logging.info(f"Parent directory already exists: {parent_dir}")

    return


def obtain_output_folder(label, kind, number):
    if number is None or number == "":
        path = OUTPUT_PATH / f"{kind}_{label}"
    else:
        path = OUTPUT_PATH / f"{kind}_{label}_{number}"
    create_parent_directory(path)
    path.mkdir(exist_ok=True)
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
    name = name.strip()
    # Replace spaces with underscores
    name = name.replace(" ", "_")
    name = name.replace(")", "")
    name = name.replace("(", "")
    # Remove invalid characters for Unix
    name = re.sub(r"[^a-zA-Z0-9._-]", "", name)
    name = name.strip()
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


if __name__ == "__main__":

    """
    path = obtain_output_folder("BISTROT_VALOIS", "siret",siret)
    logging.debug(path)
    logging.debug(USER, DOCUMENTS_PATH)
    """

    # Exemple d'utilisation
    chemin_compatible = get_unix_compatible_path(
        Path(
            r"C:\Users\lvolat\Documents\cocoAI\work\output\bail_Annexe 6 a) - Bail du 1er septembre 1995\slides_results.pdf"
        )
    )
    print(chemin_compatible)
