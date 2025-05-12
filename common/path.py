import getpass
import json
import logging
import os
import re
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
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


def get_df_folder_possibles():

    # # definition du df qui fait la correspondance
    # df = pd.read_excel(COMMON_PATH / "bdd_SIRET.xlsx").set_index("folder")
    # df2 = (
    #     pd.read_json(COMMON_PATH / "siret_databank.json", orient="index")
    #     .iloc[:, 0]
    #     .apply(str)
    # )
    # df["siret"] = df2
    # df.reset_index(inplace=True)

    df = pd.read_csv(COMMON_PATH / "folder_possibles_completv2.csv", index_col=0)
    df["siret"] = df["siret"].apply(
        lambda x: str(int(x)) if not np.isnan(float(x)) else np.nan
    )

    return df.reset_index()


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


def list_files_in_directory(directory):
    """Liste tous les fichiers dans un répertoire et ses sous-répertoires."""
    return [str(path) for path in Path(directory).rglob("*") if path.is_file()]


# df2 = pd.read_excel(Path(r"C:\Users\lvolat\Documents\cocoAI\common\bdd_SIRET.xlsx"))


# for e, s in df2.reset_index()[["ENSEIGNE", "SIRET"]].dropna().iterrows():
#     print(s["ENSEIGNE"], s["SIRET"])
#     if s["SIRET"] != "Non trouvé":
#         get_infos_from_a_siren(str(s["SIRET"])[:-5])


# di = {
#     "CASA DI MARIO - 75007 PARIS - 132 Rue du BAC": "53119288800018",
#     "BROOKLYN CAFE - 75017 PARIS - 32 Place Saint FERDINAND": "Informations non disponibles",
#     "CAFE DU MEXIQUE - 75016 PARIS - 3 Place de MEXICO": "Informations non disponibles",
#     "CHEZ BEBER  - 75006 PARIS - 71 Bld du MONTPARNASSE": "42507282400011",
#     "CHIEN QUI FUME (Le) - 75001 PARIS - 33 Rue du PONT-NEUF": "31013032300015",
#     "CIAL - 75001 PARIS - rue Mondétour - 16": "Informations non disponibles",
#     "DEI FRATELLI - 75001 PARIS - 10 Rue des PYRAMIDES": "83995102700011",
#     "GENTLEMEN - JARDINS DE L'ARCHE - 92000 NANTERRE": "80449572900035",
#     "GRAND CARNOT (Le) - 75017 PARIS - 32 Avenue CARNOT angle 40 Rue des ACACIAS": "79895243800017",
#     "MANHATTAN TERRAZZA - 108 Av de VILLIERS - 75017 PARIS": "88096301200014",
#     "RALLYE PASSY (BOUILLON PASSY) - 75016 PARIS - 34 Rue de l'ANNONCIATION": "48747486800022",
#     "AFFRANCHIS (Les) - 75012 PARIS - 14 Avenue DAUMESNIL": "84492436500027",
#     "ANDORINHA - 75016 PARIS - 199 Avenue de VERSAILLES - ex VERSAILLES AVENUE - MONTCASTEL": "79903742900014",
#     "AQUABIKE - 75015 PARIS - 45 Avenue de la MOTTE-PICQUET": "43776601700010",
#     "ASCENSION - 75018 - 62 RUE CUSTINE": "79854416900016",
#     "ASIAN KITCHEN - 75007 PARIS - 49 Quai d'ORSAY - 20240925": "42507282400011",
#     "ASSOCIES (Les) - 75012 PARIS - 50 Bld de la BASTILLE": "43472611300013",
#     "AVELLINO - 4 Bld Richard WALLACE - 92800 PUTEAUX": "53862111100013",
#     "AZZURO - 92100 BOULOGNE-BILLANCOURT - 59 Place René CLAIR": "38027351600019",
#     "BAIGNEUSES (Les) - 64200 BIARRITZ - 14 Rue du PORT VIEUX": "40101719900014",
#     "BAR DES SPORT - 75012 - 73 AVENUE DU GENERAL MICHEL BIZOT": "82268394200012",
#     "BARIOLÉ (Le) - 75020 PARIS - 103 Rue de BELLEVILLE": "53792611300013",
#     "BEBER - 75006 PARIS - 71 Bld du MONTPARNASSE": "42507282400011",
#     "BILLY BILLI - 92000 NANTERRE": "89324339400010",
#     "BISTROT BALNÉAIRE (Le) - 40150 SOORTS-HOSSEGOR - 1830 Avenue du TOURING CLUB": "48903161700014",
#     "BISTROT CHARBON (Le) - 75004 PARIS- 131 rue Saint MARTIN": "53739192200013",
#     "BISTROT DE RUNGIS - DEFICIT REPORTABLE": "43792187700043",
#     "BISTROT DU FAUBOURG - 12 Allée de l'ARCHE - 92400 COURBEVOIE": "81531506400023",
#     "BOIS LE VENT (Le) - 75016 PARIS - 59 Rue de BOULAINVILLIERS": "38098071400014",
#     "BON JACQUES (Le) - 75017 - 34 Rue Jouffroy d'ABBANS": "90834751100013",
#     "BOUDOIR (Le) - 75006 PARIS - 202 Bld Saint GERMAIN": "84072367000013",
#     "BOULANGERIE DE L'OLYMPIA": "34027633600014",
#     "BOULEDOGUE (Le) - 75003 PARIS - 20 Rue RAMBUTEAU": "40327792400011",
#     "BRASSERIE LOLA - MURS ET FONDS - 75015 PARIS - 99 rue du THÉÂTRE": "83488996600015",
#     "BRIOCHE DORÉE - 78 Av des CHAMPS ELYSÉES - 75008 PARIS": "31890659100014",
#     "CAFÉ DE L'ÉGLISE - 92110 CLICHY - 100 Bld Jean JAURÈS": "83226626600015",
#     "CANTINA - 75016 - CLAUDE TERRASSE - 16": "48057007600020",
#     "COMPAGNIE (La) - 75017 PARIS - 123 Av de WAGRAM": "Informations non disponibles",
#     "DA ROSA - 75001 PARIS - 7 Rue ROUGET de l'ISLE": "Informations non disponibles",
#     "DIPLOMATE (Le)- 75016 - CLAUDE TERRASSE - 16": "Informations non disponibles",
#     "DODDY'S - 75017 PARIS - 80 Rue Mstislav ROSTROPOVITCH": "Informations non disponibles",
#     "EL SOL - 75008 - 22 RUE DE PONTHIEU": "Informations non disponibles",
#     "FAJITAS - 75006 PARIS - 15 Rue DAUPHINE": "Informations non disponibles",
#     "GERMAIN - 94340 - JOINVILLE LE PONT - quai de la Marne": "Informations non disponibles",
#     "GRILLON - SARL LE SUQUET": "Informations non disponibles",
#     "GROUPE DORR": "Informations non disponibles",
#     "CLAUDIA - 75015 PARIS - 51 Avenue de La MOTTE-PICQUET": "43776601700010",
#     "BRIOCHE DORÉE - 78 Av des CHAMPS ELYSÉES - 75008 PARIS": "Informations non disponibles",
#     "CAFÉ DE L'ÉGLISE - 92110 CLICHY - 100 Bld Jean JAURÈS": "Informations non disponibles",
#     "BRIOCHE DORÉE - 78 Av des CHAMPS ELYSÉES - 75008 PARIS": "31890659100014",
#     "BROOKLYN CAFE - 75017 PARIS - 32 Place Saint FERDINAND": "Informations non disponibles",
#     "CAFE DU MEXIQUE - 75016 PARIS - 3 Place de MEXICO": "Informations non disponibles",
#     "CAFÉ DE L'ÉGLISE - 92110 CLICHY - 100 Bld Jean JAURÈS": "83226626600015",
#     "CHEZ BEBER  - 75006 PARIS - 71 Bld du MONTPARNASSE": "42507282400011",
#     "BROOKLYN CAFE - 75017 PARIS - 32 Place Saint FERDINAND": "Informations non disponibles",
#     "CAFE DU MEXIQUE - 75016 PARIS - 3 Place de MEXICO": "Informations non disponibles",
#     "CHEZ BEBER  - 75006 PARIS - 71 Bld du MONTPARNASSE": "42507282400011",
#     "CHIEN QUI FUME (Le) - 75001 PARIS - 33 Rue du PONT-NEUF": "31013032300015",
#     "CIAL - 75001 PARIS - rue Mondétour - 16": "Informations non disponibles",
#     "CLOS BOURGUIGNON (Le) - 75009 PARIS - 39 Rue CAUMARTIN": "39260504400017",
#     "COMPAGNIE (La) - 75017 PARIS - 123 Av de WAGRAM": "84275832800012",
#     "DA ROSA - 75001 PARIS - 7 Rue ROUGET de l'ISLE": "75239417100017",
#     "DIPLOMATE (Le)- 75016 PARIS - 15 Rue SINGER": "83389469400011",
#     "DODDY'S - 75017 PARIS - 80 Rue Mstislav ROSTROPOVITCH": "84275832800012",
#     "EL SOL - 75008 - 22 RUE DE PONTHIEU": "50186386400028",
#     "BROOKLYN CAFE - 75017 PARIS - 32 Place Saint FERDINAND": "Informations non disponibles",
#     "CAFE DU MEXIQUE - 75016 PARIS - 3 Place de MEXICO": "Informations non disponibles",
#     "CHEZ BEBER  - 75006 PARIS - 71 Bld du MONTPARNASSE": "42507282400011",
#     "CHIEN QUI FUME (Le) - 75001 PARIS - 33 Rue du PONT-NEUF": "31013032300015",
#     "CIAL - 75001 PARIS - rue Mondétour - 16": "Informations non disponibles",
#     "CLOS BOURGUIGNON (Le) - 75009 PARIS - 39 Rue CAUMARTIN": "39260504400017",
#     "COMPAGNIE (La) - 75017 PARIS - 123 Av de WAGRAM": "84275832800012",
#     "DA ROSA - 75001 PARIS - 7 Rue ROUGET de l'ISLE": "75239417100017",
#     "DIPLOMATE (Le)- 75016 PARIS - 15 Rue SINGER": "83389469400011",
#     "DODDY'S - 75017 PARIS - 80 Rue Mstislav ROSTROPOVITCH": "84275832800012",
#     "EL SOL - 75008 - 22 RUE DE PONTHIEU": "50186386400028",
#     "FAJITAS - 75006 PARIS - 15 Rue DAUPHINE": "43426634200014",
#     "GERMAIN - 94340 - JOINVILLE LE PONT - quai de la Marne": "85255555600012",
#     "GRILLON - SARL LE SUQUET": "45361623700013",
#     "GROUPE DORR": "32918652200010",
#     "HIPPOPOTAMUS BASTILLE - 75004 PARIS - 1 Bld BEAUMARCHAIS": "Informations non disponibles",
#     "IL PARADISIO - 75017 PARIS - 30 RUE LEGENDRE": "Informations non disponibles",
# }

# for v in di.values():
#     get_infos_from_a_siren(str(v)[:-5])


def load_json_file(path):
    with open(path, "r", encoding="utf-8") as file:
        di = json.load(file)
    return di


def write_json_file(di, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(di, ensure_ascii=False))
    return


def is_file_empty(file_path):
    """Check if a file is not empty."""
    try:
        # Create a Path object for the file
        path = Path(file_path)
        # Check if the file exists and is not empty
        if path.is_file() and path.stat().st_size > 0:
            return False
        else:
            return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return True
