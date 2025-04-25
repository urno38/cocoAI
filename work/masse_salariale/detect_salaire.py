import shutil

from cocoAI.folder_tree import get_enseigne_folder
from common.identifiers import convert_to_siren
from common.path import DATALAKE_PATH

siret = 75239417100017
siren = convert_to_siren(siret)
ENSEIGNE_FOLDER = get_enseigne_folder(siret)


# for bull in list(DATALAKE_PATH.rglob("plans*")):
#     try:
#         shutil.rmtree(bull)
#         print(bull)
#     except:
#         pass
