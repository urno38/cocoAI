# script pour demander un output structuré à partir d'un document
# notamment une liasse fiscale

import os
import sys
from pathlib import Path
from random import sample, shuffle

import pyperclip
from PyPDF2 import PdfReader, PdfWriter

from cocoAI.etablissement import display_infos_on_siret
from cocoAI.liasse_fiscale import (
    get_liasse_list_in_folder,
    get_liasse_md_path,
    get_prompt_mistral_detaille,
    get_prompt_mistral_resume,
)
from cocoAI.masse_salariale import parse_pdf
from common.folder_tree import get_enseigne_folder_path
from common.identifiers import verify_id
from common.logconfig import LOGGER
from common.path import get_df_folder_possibles, is_file_empty, rapatrie_file


def split_pdf(input_pdf_path):
    # Vérifie si le fichier existe
    if not os.path.isfile(input_pdf_path):
        print(f"Le fichier {input_pdf_path} n'existe pas.")
        return

    # Ouvre le fichier PDF
    with open(input_pdf_path, "rb") as input_pdf_file:
        reader = PdfReader(input_pdf_file)
        num_pages = len(reader.pages)

        # Vérifie si le PDF a plusieurs pages
        if num_pages > 1:
            print(
                f"Le fichier {input_pdf_path} contient {num_pages} pages. Division en cours..."
            )

            path_list = []
            # Divise le PDF en fichiers individuels
            for i in range(num_pages):
                writer = PdfWriter()
                writer.add_page(reader.pages[i])

                # Définit le nom du fichier de sortie
                output_pdf_path = (
                    f"{os.path.splitext(input_pdf_path)[0]}_page_{i+1}.pdf"
                )

                # Écrit le fichier PDF de sortie
                with open(output_pdf_path, "wb") as output_pdf_file:
                    writer.write(output_pdf_file)

                print(f"Page {i+1} sauvegardée dans {output_pdf_path}")

                path_list.append(Path(output_pdf_path))
        else:
            print(f"Le fichier {input_pdf_path} contient une seule page.")

        return path_list


def main_old():
    pdf_path = Path(
        r"C:\Users\lvolat\COMPTOIRS ET COMMERCES\DATALAKE - Documents\LA_RENAISSANCE_827953415\BISTROT_RENAISSANCE\REFERENCE_DOCUMENTS\DOCUMENTATION_FINANCIERE\BILANS_CA\liasse_23_is_renaissance.pdf"
    )
    siret = "82795341500011"
    dest_enseigne_folder = get_enseigne_folder_path(siret)
    TMP = dest_enseigne_folder / "WORK_DOCUMENTS"
    MISTRAL_TMP = dest_enseigne_folder / "MISTRAL_FILES"

    pdf_file_path = rapatrie_file(pdf_path)
    del pdf_path  # securite pour eviter de toucher ulterieurement au fichier d'origine

    # Exemple d'utilisation
    path_list = split_pdf(pdf_file_path)

    for path in path_list:

        md_output = parse_pdf(path, MISTRAL_TMP)
        # except:
        # LOGGER.warning(f"{sal} n est pas interprete")
        # continue

        with open(md_output, "r", encoding="utf-8") as f:
            ocr_output = "\n".join(f.readlines())

    # ocr_response = process_file_by_Mistral_OCR(path)
    # response_dict = json.loads(ocr_response.model_dump_json())
    # print(response_dict)
    # ocr_markdown = response_dict["pages"][0]["markdown"]
    # print(ocr_markdown)
    # request = (
    #     "Extrais du document joint tous les montants en euros et les codes à deux ou trois caractères situés immédiatement avant. Présente le résultat sous forme d'un json."
    #     + "\n\n\n"
    #     + ocr_markdown
    # )

    # request_file = MISTRAL_TMP / pdf_file_path.with_suffix(".request").name
    # with open(request_file, "w", encoding="utf-8") as f:
    #     f.write(request)
    #     LOGGER.debug(f"request exported to {request_file}")

    # model = "mistral-large-latest"
    # chat_response = ask_Mistral(
    #     api_key=MISTRAL_API_KEY_PAYANTE,
    #     prompt=request,
    #     model=model,
    #     json_only=True,
    # )
    # response = chat_response.choices[0].message.content

    # if 0:
    #     txt_path = MISTRAL_TMP / path.with_suffix(".txt").name
    #     with open(txt_path, "w", encoding="utf-8") as f:
    #         f.write(response)
    #         LOGGER.info(txt_path.resolve())
    # else:
    #     response_dict2 = json.loads(response)
    #     json_path = MISTRAL_TMP / path.with_suffix(".json").name
    #     with open(json_path, "w", encoding="utf-8") as f:
    #         f.write(json.dumps(response_dict2, ensure_ascii=False))
    #         LOGGER.debug(json_path.resolve())

    # # LOGGER.info(f"Mistral did answer in {txt_path}")


def main(siret):

    display_infos_on_siret(siret)

    # ENSEIGNE_FOLDER = get_enseigne_folder(siret)
    # FOLDER_LIASSE = ENSEIGNE_FOLDER / "DOCUMENTATION_FINANCIERE" / "BILANS_CA"
    # print(FOLDER_LIASSE)

    liasse_list = get_liasse_list_in_folder(siret)
    if len(liasse_list) > 0:
        print("\n\nles liasses actuellement présentes sont")
        for liasse in liasse_list:
            print(liasse)

    # docs_list =
    # if len(docs_list) > 0:
    #     print("\n\nles documents actuellement présents sont")
    #     for doc in docs_list:
    #         print(doc)

    # if len(liasse_list) == 0:
    #     print("Pas de liasse présente dans le dossier, exit ...")
    #     return

    print(
        "Suivre scrupuleusement les étapes suivantes pour traiter un document contenant des infos type liasse fiscale"
    )

    default_liasse = liasse_list[0] if len(liasse_list) > 0 else ""
    liasse_path = input(
        f"\n\nQuel est le chemin de la liasse fiscale a interpreter ? [{default_liasse}]"
    )
    if not liasse_path:
        liasse_path = default_liasse

    if liasse_path == "":
        print("\n\n=======")
        print("l'utilisateur n a pas donne de liasse a interpreter, exit ...")
        return

    liasse_path = Path(liasse_path)

    print("\n\n=======")
    print("\n\nCopier coller le prompt suivant avec le document dans mistral")
    print("\n\n=======")
    print("document")
    print(liasse_path)
    prompt = get_prompt_mistral_resume(siret)
    print(prompt)
    pyperclip.copy(prompt)
    print("\n\nle prompt est déjà dans ton clipboard")

    liasse_md_resume = get_liasse_md_path(siret, liasse_path)
    liasse_md_resume.parent.mkdir(exist_ok=True)

    # print("\n=======")
    # print(f"\nCopier l'output de mistral dans le clipboard")
    # inp = input("done ? []")
    # with liasse_md_resume.open(mode="w") as f:
    #     f.write(pyperclip.paste())
    # print(f"clipboard written in {liasse_md_resume.resolve()}")
    # print("\n\n=======")

    # print("\n\n=======")
    # print(f"Tentons l'écriture d un bilan detaille dans le memorandum")
    # print("\n\n=======")

    print("\n=======")
    print("\nCopier coller le prompt suivant avec le document dans mistral")
    print("\n\n=======")
    print("document")
    print(liasse_path)
    prompt = get_prompt_mistral_detaille(siret)
    print(prompt)
    print("le prompt est déjà dans ton clipboard")

    liasse_md_detaille = liasse_md_resume.parent / (
        liasse_md_resume.stem + "_detaille.md"
    )

    liasse_md_detaille.parent.mkdir(exist_ok=True)

    print("\n=======")
    print(f"\nCopier l'output de mistral dans le clipboard")
    inp = input("done ? []")
    with liasse_md_detaille.open(mode="w") as f:
        f.write(pyperclip.paste())
    print(f"clipboard written in {liasse_md_detaille.resolve()}")
    print("\n\n=======")


def main_user():

    print("\n-----------")
    print("Interpretation infos type liasse fiscale")
    print("-----------")
    siret = input("\nEntrer un siret\n")
    verify_id(siret, "siret")

    main(siret)
    print("done")


if __name__ == "__main__":

    if 0:
        siret_list = get_df_folder_possibles()["siret"].dropna().values.tolist()
        shuffle(siret_list)

        for s in siret_list:
            print(s)
            if len(get_liasse_list_in_folder(s)) > 0:
                siret_ok = s
                break

        # siret = sample(get_df_folder_possibles()["siret"].dropna().values.tolist(), 1)[0]
        main(siret_ok)

    # main(90834751100010)
    # main(48138353700018)  # BISTROT VALOIS
    main_user()
