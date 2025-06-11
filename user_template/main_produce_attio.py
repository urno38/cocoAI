from cocoAI import attio
from cocoAI.etablissement import display_infos_on_siret
from common.folder_tree import get_attio_work_path
from common.path import get_df_folder_possibles

# CORPORATION

# je produis tous les csv possibles
for siret in get_df_folder_possibles()["siret"].dropna().values.tolist():
    print(siret)
    display_infos_on_siret(siret)
    try:
        ATTIO_WORK_PATH = get_attio_work_path(siret)
        if not (ATTIO_WORK_PATH / "corporation.csv").exists():
            print(siret)
            print(ATTIO_WORK_PATH)
            attio.main(siret)
    except:
        attio.main(siret)



