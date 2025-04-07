import json
from pathlib import Path

import numpy as np
import pandas as pd

from cocoAI.company import get_infos_from_a_siren
from common.AI_API import ask_Mistral
from common.keys import MISTRAL_API_KEY
from common.logconfig import LOGGER
from common.path import rapatrie_file
from common.pdf_document import convert_pdf_to_ascii
from common.REST_API import export_request, get_sirene_infos_from_SIREN


def interpret_KBIS(KBIS_path, export_json_path=None):

    if export_json_path is None:
        export_json_path = KBIS_path.with_suffix(".json")

    output_path, text = convert_pdf_to_ascii(KBIS_path, with_Mistral=True)

    request = f"Extrais le SIREN de l'établissement de ce document, il peut aussi être enregistré sous la forme d'un numéro d'immatriculation au RCS. Réponds sous forme d'un json dont la clé est 'SIREN'.\n{text}"
    request_file_path = KBIS_path.with_suffix(".request")
    with open(request_file_path, "w", encoding="utf-8") as f:
        f.write(request)

    LOGGER.info(f"request exported to {request_file_path}")

    chat_response = ask_Mistral(
        api_key=MISTRAL_API_KEY,
        prompt=request,
        model="mistral-large-latest",
        json_only=True,
    )
    LOGGER.debug(chat_response)
    json_dict = chat_response.choices[0].message.content
    LOGGER.debug(json_dict)
    response_dict2 = json.loads(json_dict)

    response_dict2["SIREN"] = int(
        response_dict2["SIREN"].replace(".", "").replace(" ", "")
    )
    with open(export_json_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(response_dict2, ensure_ascii=False))
        LOGGER.debug(export_json_path.resolve())

    return response_dict2


def get_SIREN(KBIS_path):
    new_KBIS_path = rapatrie_file(KBIS_path)
    SIREN_dict = interpret_KBIS(new_KBIS_path)
    return int(str(SIREN_dict["SIREN"]).replace(".", "").replace(" ", ""))


def get_infos(SIREN):
    response = get_sirene_infos_from_SIREN(str(SIREN))
    di = response.json()
    if di["header"]["statut"] == 200:
        pass
    elif di["header"]["statut"] == 404:
        LOGGER.debug("request went wrong")
        return None
    else:
        LOGGER.debug("not implemented")
        return None
    export_request(response, Path.cwd() / f"{SIREN}_request_siren.yaml")

    # attention on ne traite que les NAF issus de la rev 2 changement de convention
    dict_list_a_concatener = [
        d
        for d in di["uniteLegale"]["periodesUniteLegale"]
        if d["nomenclatureActivitePrincipaleUniteLegale"] == "NAFRev2"
    ]
    LOGGER.debug(dict_list_a_concatener)
    df = pd.concat(
        [
            pd.DataFrame(d, index=range(len(d.keys())))
            for i, d in enumerate(dict_list_a_concatener)
        ],
        # index=range(len(dict_list_a_concatener)),
    )
    # LOGGER.debug(df["activitePrincipaleUniteLegale"].drop_duplicates())
    df["Activity"] = df["activitePrincipaleUniteLegale"].apply(
        lambda x: transform_NAF_into_activity(x)
    )
    df.loc[:, "SIREN"] = SIREN
    return df


def transform_NAF_into_activity(NAF):
    naf_data_56 = {
        "NAF Code": [
            "5610A",
            "5610B",
            "5610C",
            "5621Z",
            "5629A",
            "5629B",
            "5630Z",
            "6810Z",
            "6820A",
            "6820B",
            "6831Z",
            "6832A",
            "6832B",
            "7010Z",
            "7021Z",
            "7022Z",
        ],
        "Activity": [
            "Restauration traditionnelle",
            "Cafétérias et autres libres-services",
            "Restauration de type rapide",
            "Services des traiteurs",
            "Restauration collective sous contrat",
            "Autres services de restauration n.c.a.",
            "Distribution de repas à domicile",
            "Activités des marchands de biens immobiliers",
            "Location de logements",
            "Location de terrains et d'autres biens immobiliers",
            "Agences immobilières",
            "Administration de biens immobiliers",
            "Supports juridiques de gestion de patrimoine immobilier",
            "Activités des sièges sociaux",
            "Conseil en relations publiques et communication",
            "Conseil pour les affaires et autres conseils de gestion",
        ],
    }
    naf_data_56["NAF Code"] = naf_data_56["NAF Code"] + ["0000Z"]
    naf_data_56["Activity"] = naf_data_56["Activity"] + [np.nan]

    NAF = NAF.replace(".", "").strip()
    naf_df = pd.DataFrame(naf_data_56)

    if NAF not in naf_df["NAF Code"].values:
        LOGGER.debug(naf_df["NAF Code"].values)
        LOGGER.debug(NAF)
        LOGGER.debug(f"{NAF} not in the databank above")
        LOGGER.debug("NAFcode to be implemented")

    activity = naf_df[naf_df["NAF Code"] == NAF].loc[:, "Activity"].values[0]
    # print(activity)
    return activity


def get_name(KBIS_path):
    SIREN = get_SIREN(KBIS_path)
    try:
        df = get_infos(SIREN)
        name = df.dropna(subset=["Activity"]).loc[:, "denomination"].values[0]
        return name
    except:
        return


def get_most_recent_names(KBIS_path_list):
    df = pd.concat([get_infos(get_SIREN(p)) for p in KBIS_path_list])
    dfmax = df[df["dateDebut"] == max(df["dateDebut"])]
    max_name = set((dfmax.loc[:, "denominationUniteLegale"]).values)
    return list(max_name), dfmax


def index_all_KBIS(KBIS_path_list):
    siren_list = [get_SIREN(p) for p in KBIS_path_list]
    for siren in siren_list:
        get_infos_from_a_siren(siren)
    return


def get_real_name(KBIS_path_list):
    parent_folder_name = list(set([str(path.parent) for path in KBIS_path_list]))
    LOGGER.debug(parent_folder_name)
    most_recent_names, dfmax = get_most_recent_names(KBIS_path_list)
    LOGGER.debug("most recent names")
    LOGGER.debug(most_recent_names)
    for name in most_recent_names:
        for folder_name in parent_folder_name:
            if name in folder_name:
                LOGGER.debug(f"{name} is in {folder_name}")
                real_name = name
    if not "real_name" in locals():
        # si on n a pas trouve le real name dans l intitule du dossier on va prendre le usuel du SIRET
        # donc requete Pappers
        # je recupere le SIREN
        if len(dfmax["SIREN"].drop_duplicates()) == 1:
            siren = dfmax["SIREN"].drop_duplicates().values[0]
            siren, entreprise_name, sirets, etablissements_dicts_list = (
                get_infos_from_a_siren(siren)
            )
            if len(sirets) == 1:
                # if only one etablissement
                real_name = etablissements_dicts_list[0]["enseigne"]
            else:
                enseignes_possibles = [
                    e["enseigne"]
                    for e in etablissements_dicts_list
                    if e["enseigne"] is not None
                ]
                if len(enseignes_possibles) == 1:
                    real_name = enseignes_possibles[0]
                else:
                    # c est la merde
                    LOGGER.debug(sirets)
                    raise ValueError("not implemented")
        else:
            LOGGER.debug(dfmax["SIREN"])
            raise ValueError("not implemented")

    return real_name


def main(KBIS_path):
    # SIREN = get_SIREN(KBIS_path)
    # di = get_infos(SIREN)
    name = get_name(KBIS_path)
    print(name)


if __name__ == "__main__":

    KBIS_path_list = list(
        Path(
            r"C:\Users\lvolat\COMPTOIRS ET COMMERCES\COMMERCIAL - Documents\2 - DOSSIERS à l'ETUDE\JAD - PARIS 75002 - 35 Bld BONNE NOUVELLE\2. JURIDIQUE - SOCIÉTÉ"
        ).glob("*KBIS*")
    )

    get_real_name(KBIS_path_list)

    # main(KBIS_path_list[0])
