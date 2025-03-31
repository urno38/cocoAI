import json
from pathlib import Path

from common.AI_API import ask_Mistral
from common.keys import MISTRAL_API_KEY
from common.logconfig import LOGGER
from common.path import rapatrie_file
from common.pdf_document import convert_pdf_to_ascii


def interpret_KBIS(KBIS_path, export_json_path=None):

    if export_json_path is None:
        export_json_path = KBIS_path.with_suffix(".json")

    output_path, text = convert_pdf_to_ascii(KBIS_path)

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

    print(response_dict2)

    return response_dict2


def get_SIREN(KBIS_PATH):
    new_KBIS_path = rapatrie_file(KBIS_path)
    SIREN_dict = interpret_KBIS(new_KBIS_path)
    return int(SIREN_dict["SIREN"].replace(".", "").replace(" ", ""))


def main(KBIS_path):
    SIREN = get_SIREN(KBIS_path)
    print(SIREN)


if __name__ == "__main__":
    # KBIS_path = Path(
    #     r"C:\Users\lvolat\COMPTOIRS ET COMMERCES\COMMERCIAL - Documents\2 - DOSSIERS à l'ETUDE\CORDONNERIE - 75016 PARIS - 35 Rue de L'ANNONCIATION\KBIS.pdf"
    # )

    # KBIS_path = Path(
    #     r"C:\Users\lvolat\COMPTOIRS ET COMMERCES\COMMERCIAL - Documents\2 - DOSSIERS à l'ETUDE\JAJA - 92500 RUEIL MALMAISON - 181 Avenue du 18 Juin 1940\JAJA - GERANCE\Extrait KBIS - Dossier Complet Jaja.pdf"
    # )

    for KBIS_path in list(
        Path(
            r"C:\Users\lvolat\COMPTOIRS ET COMMERCES\COMMERCIAL - Documents\2 - DOSSIERS à l'ETUDE\JAD - PARIS 75002 - 35 Bld BONNE NOUVELLE\2. JURIDIQUE - SOCIÉTÉ"
        ).glob("*KBIS*")
    ):
        print(KBIS_path)
        main(KBIS_path)

    # TODO : maintenant
    # il peut y avoir plusieurs KBIS corrects dans le dossier donc faire une requete entreprise.gouv.fr pour verifier que l entreprise existe puis stocker les fichiers temporaires dans la base et creer l arborescence
