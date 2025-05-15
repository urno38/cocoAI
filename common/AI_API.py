import json

from flatten_json import flatten
from mistralai import Mistral

from common.keys import MISTRAL_API_KEY, MISTRAL_API_KEY_PAYANTE
from common.logconfig import LOGGER


def ask_Mistral(api_key, prompt, model="mistral-large-latest", json_only=True):

    LOGGER.debug("Let us ask Mistral")
    LOGGER.debug(f"model {model}")
    LOGGER.debug(prompt)

    client = Mistral(api_key=api_key)

    try:
        if json_only:
            chat_response = client.chat.complete(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                response_format={
                    "type": "json_object",
                },
            )
        else:
            chat_response = client.chat.complete(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )
        # LOGGER.debug(f"the answer is {chat_response}")
    except:
        LOGGER.warning(chat_response)

    return chat_response


def generate_summary_with_mistral(dict_data, api_key=MISTRAL_API_KEY):

    # Initialiser le prompt
    prompt = ""

    # Boucler sur les clés du JSON pour construire le prompt
    for key, value in dict_data.items():
        if isinstance(value, dict):
            # Si la valeur est un dictionnaire, boucler sur ses clés
            prompt += f"{key} :\n"
            for sub_key, sub_value in value.items():
                prompt += f"  {sub_key} : {sub_value}\n"
        elif isinstance(value, list):
            # Si la valeur est une liste, la joindre en une chaîne
            prompt += f"{key} : {', '.join(map(str, value))}\n"
        else:
            # Sinon, ajouter directement la clé et la valeur
            prompt += f"{key} : {value}\n"

    # prompt = "\n".join(
    #     [
    #         f"-{key}: {value}"
    #         for key, value in flatten(
    #             {f"terrasse_{i}": t for i, t in enumerate(dict_data["results"])}
    #         ).items()
    #     ]
    # )

    LOGGER.debug(prompt)
    # LOGGER.debug(prompt)

    # LOGGER.debug(prompt)
    # Ajouter une instruction pour générer un résumé
    prompt = f"""Génère un résumé cohérent basé sur les informations : 
    '''
    {prompt}
    '''
    Ecris le en format markdown.
    Fais en sorte que chacune des parties du résumé contiennent peu de texte."""

    chat_response = ask_Mistral(api_key, prompt, model="mistral-small-latest")

    return chat_response.choices[0].message.content


def get_summary_from_dict(dictionary, output_path):
    summary_path = output_path / "summary.md"

    if summary_path.exists():
        LOGGER.info("Summary has already been produced")
        LOGGER.info(str(summary_path))
        return summary_path

    summary = generate_summary_with_mistral(dictionary, api_key=MISTRAL_API_KEY)
    if summary:
        LOGGER.debug(f"Résumé généré avec Mistral AI : {summary}")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary)

    return summary_path


def get_summary_from_yaml(yaml_path):
    summary_path = yaml_path.parent / "summary.md"

    if summary_path.exists():
        LOGGER.info("Summary has already been produced")
        LOGGER.info(str(summary_path))
        return summary_path

    with yaml_path.open() as f:
        lines = "".join(f.readlines())

    message = f"""
Dans un langage clair et concis résume les points saillants de cette liste. Ecris la réponse au format Markdown.
{lines}
"""
    LOGGER.info("summary generation...wait plz...")
    client = Mistral(api_key=MISTRAL_API_KEY_PAYANTE)
    messages = [{"role": "user", "content": message}]
    chat_response = client.chat.complete(
        model="mistral-large-latest", messages=messages
    )
    summary = chat_response.choices[0].message.content

    if summary:
        LOGGER.debug(f"Résumé généré avec Mistral AI : {summary}")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary)

    return summary_path


def main():

    #######
    # pour l etablissement LE JARDIN DE ROME
    #######

    # etablissement = "LE_JARDIN_DE_ROME"
    # siret = pick_id(etablissement, "siret")
    # terrace_output_path, di = extract_terrace_info_from_siret(
    #     siret=siret, etablissement=etablissement
    # )
    # file_path = get_summary_from_dict(di, terrace_output_path)

    # summary_mdpath = file_path.with_suffix(".md")
    # summary_texpath = file_path.with_suffix(".tex")
    # summary_docxpath = file_path.with_suffix(".docx")
    # summary_pdfpath = file_path.with_suffix(".pdf")
    # beamer_path = file_path.with_name("beamer.tex")

    # convert_output = pypandoc.convert_file(
    #     summary_mdpath, "latex", outputfile= summary_texpath, extra_args=["--standalone"]
    # )
    # convert_markdown_to_docx(summary_mdpath, summary_docxpath)
    # convert_markdown_to_pdf(summary_mdpath, summary_pdfpath)
    # convert_output = pypandoc.convert_file(
    #     summary_mdpath, "latex", outputfile= summary_texpath, extra_args=["--standalone"]
    # )

    # add_header_to_beamer_markdown(
    #     summary_mdpath,
    #     beamer_path,
    #     title=f"Résumé des terrasses de l'établissement {etablissement}",
    # )

    # beamer_pdfpath = beamer_path.with_suffix(".pdf")
    # convert_beamer_to_pdf(beamer_path, beamer_pdfpath, engine="pypandoc")

    #######
    # pour les bulletins de salaire
    #######

    return


if __name__ == "__main__":
    main()
