import re
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from cocoAI.company import get_infos_from_a_siren, get_infos_from_a_siret
from common.identifiers import get_entreprise_name, get_etablissement_name
from common.logconfig import LOGGER
from common.path import COMMON_PATH, DATALAKE_PATH, make_unix_compatible


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


def get_entreprise_folder(siren):
    LOGGER.debug(siren)
    return DATALAKE_PATH / (get_entreprise_name(siren) + "_" + str(siren))


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

    df = pd.read_csv(COMMON_PATH / "folder_possibles.csv", index_col=0)
    df["siret"] = df["siret"].apply(
        lambda x: str(int(x)) if not np.isnan(float(x)) else np.nan
    )

    return df


def create_complete_folder_tree(siret):
    # df = get_df_folder_possibles()
    siren = str(int(siret)).strip()[:9]
    LOGGER.debug(siren)
    # root_yaml_file = COMMON_PATH / "folder_structure.yaml"

    dest_entreprise_folder_path = get_entreprise_folder(siren)
    LOGGER.debug(siret)
    enseigne = make_unix_compatible(get_etablissement_name(siret))

    for path in [
        dest_entreprise_folder_path / enseigne,
        dest_entreprise_folder_path / enseigne / "WORK_DOCUMENTS",
        dest_entreprise_folder_path / enseigne / "MISTRAL_FILES",
        dest_entreprise_folder_path / enseigne / "ATTIO_FILES",
        dest_entreprise_folder_path
        / enseigne
        / "COMMERCIAL_DOCUMENTS",  # documents de commercialisation type memorandum d information ou teaser
    ]:
        path.mkdir(parents=True, exist_ok=True)

    return dest_entreprise_folder_path / enseigne


def main(siren):

    siren, entreprise_name, sirets, etablissements = get_infos_from_a_siren(siren)
    dest_folder = create_complete_folder_tree(siren)


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
        entreprise_name, etablissement = get_infos_from_a_siret(siret)
        print(int(str(siret)[:-5]))
        main(int(str(siret)[:-5]))


def get_ser_infos(source_folder_path):

    df = get_df_folder_possibles()

    folder_possibles = df.folder.drop_duplicates().values

    # je cherche le folder correspondant
    for f in folder_possibles:
        if f == source_folder_path.name:
            return df.set_index("folder").loc[f, :]

    return None
