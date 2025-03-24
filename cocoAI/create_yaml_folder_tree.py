from pathlib import Path

import yaml

from common.logconfig import LOGGER
from common.path import COMMERCIAL_ONE_DRIVE_PATH, COMMON_PATH, DESKTOP_PATH


def extract_folder_structure(folder_path):
    def recursive_extract(current_path):
        structure = {}
        try:
            for path in current_path.iterdir():
                if path.is_dir():
                    structure[path.name] = recursive_extract(path)
        except:
            pass
        return structure

    folder_path = Path(folder_path)
    return recursive_extract(folder_path)


def save_to_yaml(data, output_file):
    with open(output_file, "w") as file:
        yaml.dump(data, file, default_flow_style=False)


# Example usage
folder_path = (
    COMMERCIAL_ONE_DRIVE_PATH
    / "3 - DOSSIERS REALISÉS - ETABLISSEMENTS VENDUS ACC"
    / "2025 - PETIT BISTROT D'AUTEUIL (Le) - 75016 PARIS - 8 Bis Rue VEEDERET"
    / "15. BIBLE DES ACTES DE CESSION TERRASSE DU GOUL03022025"
    / "Documents"
)

folder_path = DESKTOP_PATH / "Documents"

output_file = COMMON_PATH / "folder_structure.yaml"
LOGGER.info(output_file)
cwd = Path.cwd()
structure = extract_folder_structure(folder_path)
save_to_yaml(structure, output_file)
