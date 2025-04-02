import json
from pathlib import Path
from urllib.parse import urlencode

import requests

from common.convert import json_to_yaml, load_yaml_to_dict
from common.identifiers import pick_id
from common.keys import SIRENE_API_KEY
from common.logconfig import LOGGER
from common.path import OPENDATA_PARIS_URL, WORK_PATH, create_parent_directory


def write_request_to_json(response, outputfile_path):
    create_parent_directory(outputfile_path)
    with open(outputfile_path, "w", encoding="utf-8") as file:
        json.dump(response.json(), file, indent=4, ensure_ascii=False)
    return response


def export_request(response, outputfile_path):
    yaml_outputfile_path = outputfile_path.with_suffix(".yaml")
    write_request_to_json(response, outputfile_path)
    json_to_yaml(outputfile_path, yaml_outputfile_path)
    LOGGER.debug(f"Data has been written to {yaml_outputfile_path.resolve()}")
    return


def make_request_with_api_key(
    url: str,
    outputfile_path: Path,
    API: str = "OPENDATA",
    api_key: str = None,
):
    # check if the file already exists, then we do not recreate it
    if outputfile_path.with_suffix(".yaml").exists():
        LOGGER.debug(
            f'result already available in {outputfile_path.with_suffix(".yaml")}'
        )
        return

    if API in ["PAPPERS"]:
        if api_key is None:
            raise ValueError("please give an api_key")
        headers = {"api-key": api_key}
        response = requests.get(url, headers=headers)
    else:
        response = requests.get(url)

    if response.status_code == 200:
        LOGGER.debug(response)
        LOGGER.info("Request successful!")
        create_parent_directory(outputfile_path)
        export_request(response, outputfile_path)
    else:
        LOGGER.debug(response.text)
        raise ValueError(f"Request failed with status code {response.status_code}")
    return response


def main():

    # #########
    # # Exemple d'utilisation PAPPERS
    # siren = "310130323"
    # json_cartopath = WORK_PATH / "pappers_output" / f"output_cartographie_{siren}.json"
    #

    # params = {"siren": siren, "degre": 4}
    # url = f"{PAPPERS_API_URL}/entreprise/cartographie?&{urlencode(params)}"
    # LOGGER.info(url)
    # response = make_request_with_api_key(url, json_cartopath)
    # dicarto = load_yaml_to_dict(json_cartopath.with_suffix(".yaml"))
    # ##########

    #########
    # Exemple d'utilisation terrasses Paris
    params = {"siren": pick_id("BISTROT_VALOIS", kind="siren")}
    # params = {"limit": "20", "where": "siret=57205690100018"}
    json_terrassespath = WORK_PATH / "terrasses_output" / f"output_terrasses.json"
    # if json_terrassespath.exists():
    #     os.remove(json_terrassespath)
    url = f"{OPENDATA_PARIS_URL}/catalog/datasets/terrasses-autorisations/records?&{urlencode(params)}"
    LOGGER.info(url)
    response = make_request_with_api_key(url, json_terrassespath)
    di = load_yaml_to_dict(json_terrassespath.with_suffix(".yaml"))
    return


def get_sirene_infos_from_SIRET(SIRET: str):
    siret = "/".join(["siret", SIRET])
    url = "https://api.insee.fr/api-sirene/3.11" + "/" + siret
    headers = {"X-INSEE-Api-Key-Integration": SIRENE_API_KEY}
    response = requests.get(url, headers=headers)
    return response


def get_sirene_infos_from_SIREN(SIREN: str):
    siren = "/".join(["siren", SIREN])
    url = "https://api.insee.fr/api-sirene/3.11" + "/" + siren
    headers = {"X-INSEE-Api-Key-Integration": SIRENE_API_KEY}
    response = requests.get(url, headers=headers)
    return response


if __name__ == "__main__":
    main()
