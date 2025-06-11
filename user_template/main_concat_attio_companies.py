import pandas as pd

from common.convert import yaml_to_dict
from common.path import COMMON_PATH, DATALAKE_PATH

di = yaml_to_dict(COMMON_PATH / "databank.yaml")
# df = pd.DataFrame.from_dict(di)
df = pd.DataFrame.from_dict(di["siren"], orient="index")


df.reset_index(inplace=True)
df.columns = ["Nom de la holding", "n° de SIREN - holding"]
df["Name"] = df["Nom de la holding"]
wdir = DATALAKE_PATH / "ATTIO_workdir"
wdir.mkdir(exist_ok=True)

df.to_csv(wdir / "companies_global.csv")
print(wdir / "companies_global.csv")
