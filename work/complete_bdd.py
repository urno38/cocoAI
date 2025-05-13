from pathlib import Path

import numpy as np
import pandas as pd

from cocoAI.company import clean_all_siren_outputs, get_infos_from_a_siret
from common.identifiers import (
    get_etablissement_name,
    get_infos_from_a_siren,
)
from common.path import COMMON_PATH, WORK_PATH

WORK = WORK_PATH / "remplissage_csv"
WORK.mkdir(exist_ok=True)

# pretraitement
# dforigin = pd.read_csv(COMMON_PATH / "folder_possibles_complet.csv", index_col=0)
# dforigin = dforigin.set_index("folder")
# for col in dforigin.columns:
#     if "Unnamed" in col or "LIBRE" in col or "Colonne" in col:
#         dforigin = dforigin.drop(col, axis=1)
# dforigin = dforigin.drop("CP", axis=1)
# dforigin = dforigin.drop("CP_y", axis=1)
# dforigin = dforigin.drop("TYPE DE VENTE", axis=1)
# dforigin = dforigin.drop("RAISON SOCIAL", axis=1)
# dforigin = dforigin.drop("EN VENTE", axis=1)
# dforigin = dforigin.drop("AFFAIRE", axis=1)

# dforigin = dforigin.rename(
#     columns={
#         "CP_x": "CP",
#     }
# )

# dforigin["CP"] = dforigin["CP"].apply(lambda x: str(int(x)) if not np.isnan(x) else x)
# dforigin["siret"] = dforigin["siret"].apply(
#     lambda x: str(int(x)) if not np.isnan(x) else x
# )
# dforigin.to_csv(WORK / "folder_possibles_completv2.csv")
# print((WORK / "folder_possibles_completv2.csv").resolve())

dforigin = pd.read_csv(WORK / "folder_possibles_completv2.csv")

dforigin = dforigin.drop_duplicates(subset="folder", keep="last").sort_values("folder")
for col in dforigin.columns:
    if "Unnamed" in col or "LIBRE" in col or "Colonne" in col:
        dforigin = dforigin.drop(col, axis=1)

dforigin["siret"] = dforigin["siret"].apply(
    lambda x: str(int(x)) if not np.isnan(x) else x
)
filterser = dforigin.folder.apply(
    lambda x: (
        Path(
            r"C:\Users\lvolat\COMPTOIRS ET COMMERCES\COMMERCIAL - Documents\100 - DOSSIERS ARCHIVÉS\1 - DOSSIERS REALISÉS - ETABLISSEMENTS VENDUS ACC"
        )
        / x
    ).exists()
)

for s in dforigin[filterser]["siret"].dropna().values:
    # print(s)
    try:
        get_infos_from_a_siret(s)
    except:
        clean_all_siren_outputs(str(s)[:-5])
        get_infos_from_a_siret(s)

dforigin["ENSEIGNE"] = dforigin["siret"].apply(
    lambda x: get_etablissement_name(x) if not pd.isnull(x) else x
)

dforigin[filterser][pd.isna(dforigin.siret)].set_index("folder").to_csv(
    WORK / "incomplete_siretv2.csv"
)
dforigin[filterser][~pd.isna(dforigin.siret)].set_index("folder").to_csv(
    WORK / "complete_siretv2.csv"
)

dforigin.set_index("folder").to_csv(WORK / "folder_possibles_completv2.csv")
    WORK / "complete_siretv2.csv"
)

dforigin.set_index("folder").to_csv(WORK / "folder_possibles_completv2.csv")
