import shutil

from cocoAI import etablissement, terrasse
from cocoAI.folder_tree import get_enseigne_folder
from common.logconfig import LOGGER


def deplace_all_file_in_workpath(folder_path, new_work_folder, nom):
    dst_folder_path = new_work_folder / nom
    dst_folder_path.mkdir(exist_ok=True)
    for p in folder_path.glob("*"):
        p.replace(dst_folder_path / p.name)
    return dst_folder_path


# a partir d'un seul siret, je produis un memo blanc
siret = "31013032300028"  # le chien qui fume
enseigne_folder = get_enseigne_folder(siret)
work_folder = enseigne_folder / "WORK_DOCUMENTS"
md_tuples = []
LOGGER.info(work_folder)

# tous les blocs
output_folder = etablissement.main(siret)
final_folder = deplace_all_file_in_workpath(output_folder, work_folder, "etablissement")
md_tuples.append(('etablissement'),final_folder/)

# terrasses
output_folder = terrasse.main(siret)
deplace_all_file_in_workpath(output_folder, work_folder, "terrasses")


# je convertis le markdown glob en docx et en pdf
