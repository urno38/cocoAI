from pathlib import Path

import yaml

from cocoAI.company import get_infos_from_a_siren, get_infos_from_a_siret
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
    siren, entreprise_name, sirets, etablissements = get_infos_from_a_siren(siren)
    return DATALAKE_PATH / (entreprise_name + "_" + str(siren))


def create_complete_folder_tree(siren):
    siren, entreprise_name, sirets, etablissements = get_infos_from_a_siren(siren)
    root_yaml_file = COMMON_PATH / "folder_structure.yaml"
    dest_folder = get_entreprise_folder(siren)
    if dest_folder.exists():
        LOGGER.debug(f"{dest_folder} already exists")
        return dest_folder
    for et in etablissements:
        if et["enseigne"] is None:
            LOGGER.debug(et)
            LOGGER.warning(f"{et["siret"]} n a pas de nom d etablissement dans pappers")
            LOGGER.warning("probablement un siege de holding")
            continue
        enseigne = make_unix_compatible(et["enseigne"])
        for path in [
            dest_folder / enseigne,
            dest_folder / enseigne / "WORK_DOCUMENTS",
            dest_folder / enseigne / "MISTRAL_FILES",
            dest_folder / enseigne / "ATTIO_FILES",
            dest_folder
            / enseigne
            / "COMMERCIAL_DOCUMENTS",  # documents de commercialisation type memorandum d information ou teaser
        ]:
            path.mkdir(parents=True, exist_ok=True)
        create_folder_structure_from_yaml(
            root_yaml_file, dest_folder / enseigne / "REFERENCE_DOCUMENTS"
        )
        LOGGER.debug(f"Created folder tree at {dest_folder}")

    return dest_folder


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
