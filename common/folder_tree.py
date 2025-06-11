from pathlib import Path

import yaml

from common.identifiers import get_entreprise_name, get_etablissement_name
from common.logconfig import LOGGER
from common.path import (
    DATALAKE_PATH,
    OUTPUT_PATH,
    get_df_folder_possibles,
    make_unix_compatible,
)


def create_folder_structure_from_yaml(yaml_file, dest_folder):
    """
    Creates a folder structure based on a YAML file using pathlib.

    :param yaml_file: The path to the YAML file containing the folder structure.
    :param dest_folder: The destination folder path where the structure will be created.
    """
    try:
        # Load the YAML file
        with open(yaml_file, "r") as file:
            folder_structure = yaml.safe_load(file)
        # print(folder_structure)
        # sys.exit()
        # Create the folder structure
        for key, folder in folder_structure.items():
            folder_path = Path(dest_folder) / make_unix_compatible(key)
            folder_path.mkdir(parents=True, exist_ok=True)
            LOGGER.debug(folder_path)
            if folder != {}:
                for skey, sfolder in folder.items():
                    sfolder_path = folder_path / make_unix_compatible(skey)
                    sfolder_path.mkdir(parents=True, exist_ok=True)
                    LOGGER.debug(sfolder_path)
                    if sfolder != {}:
                        for sskey, ssfolder in sfolder.items():
                            ssfolder_path = sfolder_path / make_unix_compatible(
                                ssfolder
                            )
                            ssfolder_path.mkdir(parents=True, exist_ok=True)
                            LOGGER.debug(ssfolder_path)

            LOGGER.debug(f"Created directory: {folder_path}")

        LOGGER.info(f"Folder structure created in {dest_folder}")
    except Exception as e:
        LOGGER.info(f"An error occurred: {e}")


def get_entreprise_folder_path(siren):
    return DATALAKE_PATH / (get_entreprise_name(siren) + "_" + str(siren))


def get_enseigne_folder_path(siret):
    siren = str(int(siret)).strip()[:9]
    dest_entreprise_folder_path = get_entreprise_folder_path(siren)
    enseigne = get_etablissement_name(siret)
    return dest_entreprise_folder_path / enseigne


def create_complete_folder_tree(siret):

    siren = str(int(siret)).strip()[:9]
    LOGGER.debug(siren)
    LOGGER.debug(siret)

    enseigne_folder = get_enseigne_folder_path(siret)

    for path in [
        enseigne_folder,
        enseigne_folder / "WORK_DOCUMENTS",
        enseigne_folder / "MISTRAL_FILES",
        enseigne_folder / "ATTIO_FILES",
        enseigne_folder / "COMMERCIAL_DOCUMENTS",
    ]:
        path.mkdir(parents=True, exist_ok=True)

    return enseigne_folder


def main(siren):

    siren, entreprise_name, sirets, etablissements = get_infos_from_a_siren(siren)
    dest_folder = create_complete_folder_tree(siren)


def get_ser_infos(source_folder_path):

    df = get_df_folder_possibles()

    folder_possibles = df.folder.drop_duplicates().values

    # je cherche le folder correspondant
    for f in folder_possibles:
        if f == source_folder_path.name:
            return df.set_index("folder").loc[f, :]

    return None


def get_attio_work_path(siret):
    ENSEIGNE_FOLDER = get_enseigne_folder_path(siret)
    ATTIO_PATH = list(ENSEIGNE_FOLDER.rglob("**/ATTIO_FILES/"))[0]
    return ATTIO_PATH


def get_mistral_work_path(siret):
    ENSEIGNE_FOLDER = get_enseigne_folder_path(siret)
    MISTRAL_PATH = list(ENSEIGNE_FOLDER.rglob("**/MISTRAL_FILES/"))[0]
    return MISTRAL_PATH


def get_work_path(siret):
    ENSEIGNE_FOLDER = get_enseigne_folder_path(siret)
    WORK_PATH = list(ENSEIGNE_FOLDER.rglob("**/WORK_DOCUMENTS/"))[0]
    return WORK_PATH


def get_out_path(label, kind, number, create=True):
    # deprecated, utiliser plutôt get_enseigne_folder_path pour travailler directement sur DATAPATH
    if kind == "siren" or kind == "bail":
        # path = get_enseigne_folder_path(number) / "WORK_DOCUMENTS" / (kind + "_" + label)
        if number is None or number == "":
            path = OUTPUT_PATH / f"{kind}_{label}"
        else:
            path = OUTPUT_PATH / f"{kind}_{label}_{number}"
    elif kind == "siret":
        path = get_enseigne_folder_path(number) / "WORK_DOCUMENTS" / "tmp"
    else:
        raise ValueError("not implemented")
    if create:
        path.mkdir(exist_ok=True, parents=True)
    LOGGER.debug(f"output folder is {path}")
    return path


if __name__ == "__main__":

    # recherche par siren
    for siren in [
        818114456,  # SIAM-POMPE
        310130323,  # GALLA
        481383537,  # BISTROT VALOIS
    ]:
        main(siren)

    # recherche par siret
    for siret in [
        65201475400012,  # LE ROI DE SIAM
    ]:
        # entreprise_name, etablissement = get_infos_from_a_siret(siret)
        print(int(str(siret)[:-5]))
        main(int(str(siret)[:-5]))
