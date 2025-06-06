from numbers import Number

import numpy as np
import pandas as pd

from cocoAI import attio
from cocoAI.etablissement import display_infos_on_siret
from common.folder_tree import get_attio_work_path
from common.path import DATALAKE_PATH, get_df_folder_possibles

if 0:
    # je produis tous les csv possibles
    for siret in get_df_folder_possibles()["siret"].dropna().values.tolist()[:5]:
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
else:

    df = pd.concat(
        [
            pd.read_csv(f, index_col=0)
            for f in list(DATALAKE_PATH.rglob("ATTIO_FILES/corporation.csv"))
        ]
    )

    def modify_activity(activity):
        if isinstance(activity, str):
            if "brasserie" in activity.lower():
                return "Brasserie"
            elif "restaurant" in activity.lower() or "restauration" in activity.lower():
                return "Restaurant"
            elif "pizzeria" in activity.lower():
                return "Pizzeria"
            elif "bar" in activity.lower() or "limonadier" in activity.lower():
                return "Limonade"
            else:
                return activity
        else:
            return activity

    def modify_red(x):
        if isinstance(x, Number):
            if np.isnan(x):
                return np.nan
            else:
                return str(float(x)) + " €"
        else:
            new_x = x.replace("euros", "€")

    wdir = DATALAKE_PATH / "ATTIO_workdir"
    wdir.mkdir(exist_ok=True)
    df.to_csv(wdir / "corporation_global_raw.csv")

    # je mets en forme rapidement pour que ça soit plus lisible dans attio
    df["Nom de la société"] = df["Nom de la société"].apply(
        lambda x: x.replace("_", " ")
    )
    df["Activité exercée"] = df["Activité exercée"].apply(lambda x: modify_activity(x))
    df["Redevance de gérance"] = df["Redevance de gérance"].apply(
        lambda x: modify_red(x)
    )

    wdir = DATALAKE_PATH / "ATTIO_workdir"
    wdir.mkdir(exist_ok=True)

    df.to_csv(wdir / "corporation_global.csv")
    print(wdir / "corporation_global.csv")
