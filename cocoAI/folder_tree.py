from pathlib import Path

import yaml

from cocoAI.company import get_infos_from_a_siren
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

        # Create the folder structure
        for folder in folder_structure:
            folder_path = Path(dest_folder) / make_unix_compatible(folder)
            # folder_path = get_unix_compatible_path(folder_path)
            folder_path.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {folder_path}")

        print(f"Folder structure created in {dest_folder}")
    except Exception as e:
        print(f"An error occurred: {e}")


def create_complete_folder_tree(siren):
    siren, entreprise_name, sirets, etablissements = get_infos_from_a_siren(siren)
    root_yaml_file = COMMON_PATH / "folder_structure.yaml"
    dest_folder = DATALAKE_PATH / entreprise_name

    print(etablissements)
    for et in etablissements:
        enseigne = make_unix_compatible(et["enseigne"])
        for path in [
            dest_folder / enseigne,
            dest_folder / enseigne / "WORK_DOCUMENTS",
            dest_folder / enseigne / "MISTRAL_FILES",
            dest_folder / enseigne / "ATTIO_FILES",
        ]:
            path.mkdir(parents=True, exist_ok=True)
        create_folder_structure_from_yaml(
            root_yaml_file, dest_folder / enseigne / "REFERENCE_DOCUMENTS"
        )

    return


def main(siren):
    siren, entreprise_name, sirets, etablissements = get_infos_from_a_siren(siren)
    create_complete_folder_tree(siren)


if __name__ == "__main__":

    main(310130323)
