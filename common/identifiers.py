from pprint import pprint

import pandas as pd

from common.convert import dict_to_yaml, yaml_to_dict
from common.logconfig import LOGGER
from common.path import COMMON_PATH, DATABANK_PATH, make_unix_compatible


def pick_id(name, kind="siren"):
    di = yaml_to_dict(COMMON_PATH / "databank.yaml")
    verify_id(di[kind][name], kind)
    return di[kind][name]


def convert_to_siren(siret):
    verify_id(siret, "siret")
    return str(int(siret))[:9]


def get_etablissement_name(siret):
    siret = str(int(siret))
    di = yaml_to_dict(COMMON_PATH / "databank.yaml")
    return [(k, v) for k, v in di["siret"].items() if v == siret][0][0]


def get_entreprise_name(siren):
    siren = str(int(siren))
    LOGGER.debug(siren)
    di = yaml_to_dict(COMMON_PATH / "databank.yaml")
    entreprise = [(k, v) for k, v in di["siren"].items() if v == siren][0][0]
    LOGGER.debug(entreprise)
    return entreprise


def verify_id(id, kind="siren"):
    id = str(int(id))
    if kind == "siren":
        if len(id) != 9:
            raise ValueError("le siren doit etre long de 9 caracteres")
    elif kind == "siret":
        if len(id) != 14:
            raise ValueError("le siret doit etre long de 14 caracteres")


def load_databank(databank_path=DATABANK_PATH):
    di = yaml_to_dict(databank_path)
    return di


def write_databank(di: dict, databank_path=DATABANK_PATH):
    dict_to_yaml(di, databank_path)
    return


def load_siren_in_databank(entreprise, siren, make_unix_compatible_flag=True):

    if make_unix_compatible_flag:
        entreprise = make_unix_compatible(entreprise)

    databank_di = load_databank()
    databank_di["siren"][entreprise] = siren
    write_databank(databank_di)
    LOGGER.debug(f"siren {siren} loaded in databank")
    return databank_di


def load_siret_in_databank(etablissement, siret):
    databank_di = load_databank()
    databank_di["siret"][make_unix_compatible(etablissement).upper()] = siret
    write_databank(databank_di)
    LOGGER.debug(f"siret {siret}")
    LOGGER.debug(f"etablissement {etablissement.upper()}")
    return databank_di


def load_nomenclature(yaml_path=COMMON_PATH / "nomenclature.yaml"):
    df_list = []
    di = yaml_to_dict(yaml_path)
    for k, dict in di.items():
        df_list.append(
            pd.DataFrame(
                {"Classe": str(k), "description": dict["description"]}, index=[k]
            )
        )
        if "subcategories" in dict.keys():
            for kk, dictt in dict["subcategories"].items():
                df_list.append(
                    pd.DataFrame(
                        {
                            "Classe": str(k),
                            "niveau1": str(kk),
                            "description": dictt["description"],
                        },
                        index=[kk],
                    )
                )
                if "subcategories" in dictt.keys():
                    for kkk, dicttt in dictt["subcategories"].items():
                        df_list.append(
                            pd.DataFrame(
                                {
                                    "Classe": str(k),
                                    "niveau1": str(kk),
                                    "niveau2": str(kkk),
                                    "description": dicttt["description"],
                                },
                                index=[kkk],
                            )
                        )
                        if "subcategories" in dicttt.keys():
                            for kkkk, dictttt in dicttt["subcategories"].items():
                                df_list.append(
                                    pd.DataFrame(
                                        {
                                            "Classe": str(k),
                                            "niveau1": str(kk),
                                            "niveau2": str(kkk),
                                            "niveau3": str(kkkk),
                                            "description": dictttt["description"],
                                        },
                                        index=[kkkk],
                                    )
                                )
                            if "subcategories" in dictttt.keys():
                                for kkkkk, dicttttt in dictttt["subcategories"].items():
                                    df_list.append(
                                        pd.DataFrame(
                                            {
                                                "Classe": str(k),
                                                "niveau1": str(kk),
                                                "niveau2": str(kkk),
                                                "niveau3": str(kkkk),
                                                "niveau4": str(kkkkk),
                                                "description": dicttttt["description"],
                                            },
                                            index=[kkkkk],
                                        )
                                    )
    df = pd.concat(df_list, ignore_index=True)
    return df


def load_nomenclature_dict_lvl1(yaml_path=COMMON_PATH / "nomenclature.yaml"):
    return (
        NOM_DF[pd.isna(NOM_DF["niveau1"])].set_index("Classe")["description"].to_dict()
    )


def load_nomenclature_dict_lvl2(yaml_path=COMMON_PATH / "nomenclature.yaml"):
    return (
        NOM_DF[pd.isna(NOM_DF["niveau2"])]
        .dropna(subset=["niveau1"])
        .set_index("niveau1")["description"]
        .to_dict()
    )


def load_nomenclature_dict_lvl3(yaml_path=COMMON_PATH / "nomenclature.yaml"):
    return (
        NOM_DF[pd.isna(NOM_DF["niveau3"])]
        .dropna(subset=["niveau2"])
        .set_index("niveau2")["description"]
        .to_dict()
    )


def load_nomenclature_dict_lvl4(yaml_path=COMMON_PATH / "nomenclature.yaml"):
    return (
        NOM_DF.dropna(subset=["niveau3"]).set_index("niveau3")["description"].to_dict()
    )


# def load_nomenclature_dict_lvl5(yaml_path=COMMON_PATH / "nomenclature.yaml"):
#     return (
#         NOM_DF.dropna(subset=["niveau4"]).set_index("niveau4")["description"].to_dict()
#     )


NOM_DF = load_nomenclature()
NOM_DICT_LVL1 = load_nomenclature_dict_lvl1()
NOM_DICT_LVL2 = load_nomenclature_dict_lvl2()
NOM_DICT_LVL3 = load_nomenclature_dict_lvl3()
NOM_DICT_LVL4 = load_nomenclature_dict_lvl4()
# NOM_DICT_LVL5 = load_nomenclature_dict_lvl5()


def get_max_len_of_the_descriptions():
    maximum = 0
    for di in [NOM_DICT_LVL1, NOM_DICT_LVL2, NOM_DICT_LVL3, NOM_DICT_LVL4]:
        tmp = max([len(des) for des in di.values()])
        if tmp > maximum:
            maximum = tmp
    return maximum


def get_official_nomenclature(id):
    if len(id) == 1:
        return NOM_DICT_LVL1[id]
    elif len(id) == 2:
        return NOM_DICT_LVL2[id]
    elif len(id) == 3:
        return NOM_DICT_LVL3[id]
    elif len(id) == 4:
        return NOM_DICT_LVL4[id]
    # elif len(id) == 5:
    #     return NOM_DICT_LVL5[id]
    else:
        raise ValueError("not implemented")


def get_query_from_id_list(id_list):
    for i, id in enumerate(id_list):
        if len(id) == 1:
            local_query = f"classe=='{id}'"
        elif len(id) == 2:
            local_query = f"idlvl2=='{id}'"
        elif len(id) == 3:
            local_query = f"idlvl3=='{id}'"
        elif len(id) == 4:
            local_query = f"idlvl4=='{id}'"
        else:
            raise ValueError("not implemented")
        if i == 0:
            query = local_query
        else:
            query += " or " + local_query
    LOGGER.debug("on filtre avec la query suivante")
    LOGGER.debug(query)
    return query


if __name__ == "__main__":
    # from common.logconfig import LOGGER

    # LOGGER.info(f'GALLA {pick_id("GALLA", kind="siren")}')
    # LOGGER.info(f'LE_JARDIN_DE_ROME {pick_id("LE_JARDIN_DE_ROME", kind="siret")}')
    # df = load_nomenclature()
    # print(df)
    # pprint(NOM_DICT_LVL3)

    print(get_etablissement_name("31890659101072"))
