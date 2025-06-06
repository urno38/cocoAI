import re
from datetime import datetime
from pathlib import Path
from pprint import pprint
from random import sample

import pandas as pd

from cocoAI import bail as bailAPI
from common.convert import yaml_to_dict
from common.folder_tree import (
    get_attio_work_path,
    get_enseigne_folder_path,
    get_mistral_work_path,
)
from common.identifiers import get_entreprise_name, get_etablissement_name, verify_id
from common.logconfig import LOGGER
from common.path import get_df_folder_possibles


def interpret_all_baux(siret):
    bail_folder = (
        get_enseigne_folder_path(siret) / "REFERENCE_DOCUMENTS" / "BAUX_QUITTANCE"
    )
    for bail in list(bail_folder.glob("*.pdf")):
        if "bail" in bail.stem.lower():
            outfolder_path = (
                get_enseigne_folder_path(siret)
                / "WORK_DOCUMENTS"
                / "tmp_bail"
                / bail.stem
            )
            outfolder_path.mkdir(parents=True, exist_ok=True)
            bailAPI.main(bail, output_folder=outfolder_path)

    di_li = []
    for yaml_path in (
        get_enseigne_folder_path(siret) / "WORK_DOCUMENTS" / "tmp_bail"
    ).rglob("output.yaml"):
        try:
            di = yaml_to_dict(yaml_path)
            # print(di)
            di_li.append(di)
            di["durée"]["début"] = datetime.strptime(di["durée"]["début"])
            di["durée"]["fin"] = datetime.strptime(di["durée"]["fin"])
            di["designation"]["surface"] = float(
                di["designation"]["surface"].replace(",", ".").split()[0]
            )
        except:
            LOGGER.debug(f"output non disponible sur {bail}")

    return di_li


def get_last_bail(siret):
    di_li = interpret_all_baux(siret)
    return [
        d
        for d in di_li
        if d["date_signature"] == max([d["date_signature"] for d in di_li])
    ][0]


def get_nombre_total_places(siret):
    # TODO
    # j analyse le bail si je peux
    return 50


def get_nombre_terrasse_places(siret):
    # TODO
    # j analyse le bail si je peux
    return 50


def fill_with(val):
    try:
        return val
    except:
        return ""


def produce_attio_corpo_df(siret):
    company = get_etablissement_name(siret)
    siret = verify_id(siret, kind="siret")
    try:
        last_bail_di = get_last_bail(siret)
    except:
        last_bail_di = {}

    # pprint(last_bail_di)
    # print(last_bail_di["designation"].keys())
    di = {
        "Nom de la société": [get_entreprise_name(siret[:9])],
        "Numéro de SIREN": [siret[:9]],
        "Numéro de SIRET": [siret],
        "Enseigne": [get_etablissement_name(siret)],  # req
        "Activité exercée": [
            (
                last_bail_di["designation"]["activité exercée"]
                if last_bail_di != {}
                else ""
            )
        ],  # req #select
        "Typologie de clientèle": [""],  # impossible a recuperer automatiquement
        "Nombre total de places": [""],  # impossible a recuperer automatiquement
        "Nombre de places de terrasse": [""],  # impossible a recuperer automatiquement
        "Terrasse": [""],  # select
        "Caractéristiques": [""],  # select
        "Information salariale (nb; ancienneté; type de contrat...)": [""],
        "Autres informations": [""],
        "Parent company": [""],  # relationship
        "Local commercial": [""],  # relationship
        "Chiffres d'affaires": [""],
        "Masse salariale": [""],
        "EBITDA retraité": [""],
        "Valorisation": [""],
        "Deal flow - corporation": [""],
        "Prix de vente": [""],
        "Deal flow - gérance": [""],
        "Exploitant actuel": [""],  # rel
        "Redevance de gérance": [
            (
                last_bail_di["loyer"]["annuel"]
                + (" HT" if fill_with(last_bail_di["loyer"]["HT"]) else " (HT ou TTC?)")
                if last_bail_di != {}
                else ""
            )
        ],
        # "Date de renouvellement - Location gérance": [
        #     datetime.strftime(fill_with(last_bail_di["durée"]["fin"], "%d/%m/%Y")
        # ],
        "Date de renouvellement - Location gérance": [
            last_bail_di["durée"]["fin"] if last_bail_di != {} else ""
        ],
    }
    df = pd.DataFrame.from_dict(di)
    # df = pd.DataFrame.from_dict(di, orient="index")

    return df


def main(siret):

    siret = str(siret)
    siren = siret[:-5]
    ent = get_entreprise_name(siren)
    LOGGER.info(f"ENTREPRISE {ent}")

    LOGGER.info(f"siret {siret}")
    et = get_etablissement_name(siret)
    LOGGER.info(f"ETABLISSEMENT {et}")
    ENSEIGNE_FOLDER = get_enseigne_folder_path(siret)
    print(ENSEIGNE_FOLDER)
    MISTRAL_WORK_PATH = get_mistral_work_path(siret)
    ATTIO_WORK_PATH = get_attio_work_path(siret)
    LIASSES_OUTPUT_PATH = get_mistral_work_path(siret) / "OUTPUT_LIASSES"
    WORK_FOLDER = ENSEIGNE_FOLDER / "WORK_DOCUMENTS"
    COMMERCIAL_FOLDER = ENSEIGNE_FOLDER / "COMMERCIAL_DOCUMENTS"
    tmp = WORK_FOLDER / "tmp"

    output_folder = get_attio_work_path(siret)
    df = produce_attio_corpo_df(siret)
    df.to_csv(output_folder / "corporation.csv")

    # di_li = interpret_all_baux(siret)
    return


def main_user():

    print("\n-----------")
    print("Production fichier pour remplir attio")
    print("-----------")
    siret = input("\nEntrer un siret\n")
    verify_id(siret, "siret")

    main(siret)
    print("done")


if __name__ == "__main__":

    # donnees

    ###############

    # siret = 85364205600024
    # get_last_bail(siret)
    # main(siret)
    # di_li = interpret_all_baux(siret)

    # siret = sample(get_df_folder_possibles()["siret"].dropna().values.tolist(), 1)[0]
    for siret in get_df_folder_possibles()["siret"].dropna().values.tolist():
        # print(siret)
        main(siret)
