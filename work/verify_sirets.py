import json
import pprint

import pyperclip

from cocoAI.company import get_infos_from_a_siren
from common.path import WORK_PATH


def load_json_file(path):
    with open(path, "r", encoding="utf-8") as file:
        di = json.load(file)
    return di


siret_db_path = WORK_PATH / "siret_databank.json"
di = load_json_file(siret_db_path)

for k, v in list(di.items())[:]:
    siren, entreprise_name, sirets, etablissements = get_infos_from_a_siren(
        str(v.strip().replace(" ", ""))[:9]
    )
    print("\n\n-----")
    print(k)
    print("-----")
    pprint.pprint(siren)
    pprint.pprint(entreprise_name)
    pprint.pprint(sirets)
    pprint.pprint(
        [
            (et["enseigne"], et["siret"], et["adresse_ligne_1"], et["ville"])
            for et in etablissements
        ]
    )

    if len(etablissements) == 1:
        if v == etablissements[0]["siret"]:
            print("ok, on change rien")
        else:
            st = f'"{k}":"{etablissements[0]["siret"]}",'
            print(st)
            pyperclip.copy(st)
            print("copied in clipboard")
    else:
        st = f'"{k}":"{etablissements[0]["siret"]}",'
        print(st)
        pyperclip.copy(st)
        print("first line copied in clipboard")

    s = input("")
