from common.convert import dict_to_yaml_file, load_yaml_to_dict
from common.logconfig import LOGGER
from common.path import COMMON_PATH, DATABANK_PATH, make_unix_compatible


def pick_id(name, kind="siren"):
    di = load_yaml_to_dict(COMMON_PATH / "databank.yaml")
    verify_id(di[kind][name], kind)
    return di[kind][name]


def verify_id(id, kind="siren"):
    if kind == "siren":
        if len(id) != 9:
            raise ValueError("le siren doit etre long de 9 caracteres")
    elif kind == "siret":
        if len(id) != 14:
            raise ValueError("le siret doit etre long de 14 caracteres")


def load_databank(databank_path=DATABANK_PATH):
    di = load_yaml_to_dict(databank_path)
    return di


def write_databank(di: dict, databank_path=DATABANK_PATH):
    dict_to_yaml_file(di, databank_path)
    return


def load_siren_in_databank(entreprise, siren):
    databank_di = load_databank()
    databank_di["siren"][make_unix_compatible(entreprise)] = siren
    write_databank(databank_di)
    LOGGER.info(f"siren {siren} loaded in databank")
    return databank_di


def load_siret_in_databank(etablissement, siret):
    databank_di = load_databank()
    databank_di["siret"][make_unix_compatible(etablissement)] = siret
    write_databank(databank_di)
    LOGGER.info(f"siret {siret} loaded in databank")
    return databank_di


if __name__ == "__main__":
    from common.logconfig import LOGGER

    LOGGER.info(f"GALLA {pick_id("GALLA", kind="siren")}")
    LOGGER.info(f"LE_JARDIN_DE_ROME {pick_id("LE_JARDIN_DE_ROME", kind="siret")}")
