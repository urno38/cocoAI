import pandas as pd

from cocoAI.company import get_infos_from_a_siren, get_infos_from_a_siret
from common.path import COMMON_PATH

df = pd.read_csv(COMMON_PATH / "folder_possibles_complet.csv")

for siret in df["siret"].dropna().values:
    siren = str(int(siret))[:-5]
    print(siren)
    try:
        get_infos_from_a_siren(siren)
    except:
        pass
