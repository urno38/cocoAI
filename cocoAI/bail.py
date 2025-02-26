from pathlib import Path

from common.AI_API import request_Mistral
from common.convert import clean_and_export_file, convert_markdown_to_beamer
from common.keys import MISTRAL_API_KEY
from common.logconfig import LOGGER
from common.path import obtain_output_folder, rapatrie_file, rename_file_unix_compatible
from common.pdf_document import convert_pdf_to_ascii


def interpret_bail_with_sentences(bail_path, output_mdpath):

    output_path, text = convert_pdf_to_ascii(bail_path)
    elements = [
        "s'agit il d'une location ? d'une vente de fond de commerce ? d'une cession de bail ? d'une vente de société ?",
        "y a t-il des droits d'entrée à la location ?",
        "s'agit il d'une location gérance ?",
        "est ce un bail commercial ? dérogatoire ? précaire ? bail mixte ? bail professionnel ? bail notarié ? d'une sous location ?",
        "la date de début",
        "la date de fin",
        "la durée du bail",
        "le loyer HT exprimé en euros par an ou par mois",
        "les charges exprimées en euros par an ou par mois",
        "est ce que le loyer inclut la TVA ?",
        "la périodicité du loyer",
        "la paiement doit être fait à terme échu ? à terme à échoir ?",
        "quel est le dépôt de garantie ?",
        "y a t-il une caution supplémentaire ? solidaire ? bancaire ? de 6 mois ou de 1 an ?",
        "la taxe foncière",
        "qui paie la taxe foncière ? Bailleur / Locataire / partage moitié chacun ? ",
        "qui paie les gros travaux (article 606) le cas échéant ? Bailleur / Locataire / partage moitié chacun ? ",
        "Y a t-il d'autres conditions financières ?",
        "la destination (indiqué dans la partie intitulée 'Destination')",
        "si certaines activités sont autorisées ou non",
        "si certaines activités sont interdites ou non",
        "la désignation avec les surfaces correspondantes en m2",
        "les taxes foncières",
        "si les taxes foncières sont à la charge du preneur ou du bailleur",
        "si la possibilité de mise en gérance libre est possible",
        "les coordonnées du bailleur ou du gestionnaire",
        "si le bailleur est un particulier ou une SCI",
        # "la date de signature du bail",
        "si le loyer est indexé à l'Indice des Loyers Commerciaux",
        "si le loyer est indexé à l'Indice du Coût de la Construction",
    ]
    request = "Extrait de ce bail : \n"
    for el in elements:
        request += f"- {el}\n"
    request += "Ecris uniquement en format markdown en faisant des parties contenant peu de texte."

    request_file_path = output_mdpath.parent / "Mistral_request.txt"
    with open(request_file_path, "w", encoding="utf-8") as f:
        f.write(request)

    LOGGER.info(f"request exported to {request_file_path}")
    LOGGER.info("lets ask Mistral to extract some infos")
    LOGGER.info("request")
    LOGGER.info(request)

    prompt = text + request
    #  model="mistral-embed"  Our state-of-the-art semantic for extracting representation of text extracts
    response = request_Mistral(
        api_key=MISTRAL_API_KEY, prompt=prompt, model="mistral-large-latest"
    )
    txt = response.choices[0].message.content
    LOGGER.debug("reponse")
    LOGGER.debug(txt)

    with open(output_mdpath, "w", encoding="utf-8") as f:
        f.write(txt)

    LOGGER.info(f"Mistral did answer in {output_mdpath}")
    return txt, output_mdpath


def interpret_bail_with_output_yaml(bail_path, output_mdpath):

    output_path, text = convert_pdf_to_ascii(bail_path)
    request = "Extrait de ce bail les informations importantes au format yaml y compris la date de signature du bail"
    prompt = text + request
    request_file_path = output_mdpath.parent / "Mistral_request.txt"

    with open(request_file_path, "w", encoding="utf-8") as f:
        f.write(request)

    with open(
        request_file_path.with_name("Mistral_prompt.txt"), "w", encoding="utf-8"
    ) as f:
        f.write(request)

    LOGGER.info(f"request exported to {request_file_path}")
    LOGGER.info("lets ask Mistral to extract some infos")
    LOGGER.info("request")
    LOGGER.info(request)

    #  model="mistral-embed"  Our state-of-the-art semantic for extracting representation of text extracts
    response = request_Mistral(
        api_key=MISTRAL_API_KEY, prompt=prompt, model="mistral-large-latest"
    )
    txt = response.choices[0].message.content
    LOGGER.debug("reponse")
    LOGGER.debug(txt)

    with open(output_mdpath, "w", encoding="utf-8") as f:
        f.write(txt)

    LOGGER.info(f"Mistral did answer in {output_mdpath}")


def interpret_bail_with_formatted_yaml(bail_path, output_mistralyamlpath):
    """
    La version la plus aboutie de l'interprétation sous Mistral
    """
    output_path, text = convert_pdf_to_ascii(bail_path)
    request = (
        "Extrait de ce bail les informations importantes au format yaml en respectant le formatage suivant:"
        + """
baileur:
  - nom:
    date_naissance:
    lieu_naissance:
    adresse: 
  - nom:
    date_naissance:
    lieu_naissance:
    adresse: 
    gestionnaire: oui/non

preneur:
  - nom:
    date_naissance:
    lieu_naissance:
    adresse: 
  - nom:
    date_naissance:
    lieu_naissance:
    adresse: 
    immatriculation:
    qualité:
    RCS: 
    enseigne:
  

designation:
  adresse: 
  description:
    rez-de-chaussée:
      usage: commercial/non mentionné
      contenu:
      détails:
    premier_étage:
      contenu:
    sous-sol:
      contenu:
    cour:
      usage:
      autorisation: 

durée:
  début: 
  fin: 
  période_initiale: 

loyer:
  annuel:
  HT: 
  période_initiale: 
  révision_triennale: 

charges:
  provision: 
  provision_annuelle:  €
  répartition: 


dépôt_de_garantie:
  montant:  €
  réajustement: 

type_de_paiement: à terme échu/à terme à échoir
mise_en_gerance_libre: interdiction/interdiction sauf autorisation du bailleur/non mentionné

caution_supplementaire: Solidaire/Bancaire(6 mois)/Bancaire(1 an)/non mentionné

taxe_fonciere: €/non indiqué
paiement_taxe_fonciere: Bailleur/Locataire/partagé en deux
paiement_gros_travaux_art_606: Bailleur/Locataire/partagé en deux

conditions:
  état_des_lieux: 
  entretien:
  garnissement: 
  transformations: 
  travaux: 
  assurance:
  changement_d'état: 
  engagement_direct:
  cession_sous_location:
  visite_des_lieux: 
  démolition_immeuble:
  tolérance: 
  solidarité_indivisibilité:
  frais:
  déménagement: 
  démolition_force_majeure: 
  responsabilité: 
  information_travaux:
  tolérance_bailleur: 

autres_conditions:

date_signature: 
"""
    )
    request_file_path = output_mistralyamlpath.parent / "Mistral_request.txt"
    with open(request_file_path, "w", encoding="utf-8") as f:
        f.write(request)

    LOGGER.info(f"request exported to {request_file_path}")
    LOGGER.info("lets ask Mistral to extract some infos")
    LOGGER.info("request")
    LOGGER.info(request)

    prompt = text + request
    #  model="mistral-embed"  Our state-of-the-art semantic for extracting representation of text extracts
    response = request_Mistral(
        api_key=MISTRAL_API_KEY, prompt=prompt, model="mistral-large-latest"
    )
    txt = response.choices[0].message.content
    LOGGER.debug("reponse")
    LOGGER.debug(txt)

    with open(output_mistralyamlpath, "w", encoding="utf-8") as f:
        f.write(txt)

    LOGGER.info(f"Mistral did answer in {output_mistralyamlpath}")

    output_yamlpath = clean_and_export_file(output_mistralyamlpath)

    return txt, output_yamlpath


def global_request_bail(bail_path, output_mdpath):

    output_path, text = convert_pdf_to_ascii(bail_path)

    request = "Ecris le résumé de ce bail en format markdown en excluant les informations concernant la date de signature de ce bail. Fais en sorte que chacune des parties du résumé contiennent peu de texte."
    request_file_path = output_mdpath.parent / "Mistral_global_request.txt"
    with open(request_file_path, "w", encoding="utf-8") as f:
        f.write(request)

    LOGGER.info(f"request exported to {request_file_path}")
    LOGGER.info("lets ask Mistral to summary")
    LOGGER.info("request")
    LOGGER.info(request)

    prompt = text + request
    #  model="mistral-embed"  Our state-of-the-art semantic for extracting representation of text extracts
    response = request_Mistral(
        api_key=MISTRAL_API_KEY, prompt=prompt, model="mistral-large-latest"
    )
    txt = response.choices[0].message.content
    LOGGER.debug("reponse")
    LOGGER.debug(txt)

    with open(output_mdpath, "w", encoding="utf-8") as f:
        f.write(txt)

    LOGGER.info(f"Mistral did answer in {output_mdpath}")
    return txt, output_mdpath


def main(bail_path):
    bail_path = rapatrie_file(bail_path)
    new_bail_path = rename_file_unix_compatible(bail_path)
    output_folder = obtain_output_folder(new_bail_path.stem, kind="bail", number="")

    LOGGER.info("First let us pick some precise infos")

    # output_mdpath = output_folder / "extraction_results.md"
    # beamer_mdpath = output_folder / "slides_results.md"
    # beamer_pdfpath = output_folder / "slides_results.pdf"
    # beamer_texpath = output_folder / "slides_results.tex"

    output_yamlpath = output_folder / "output.yaml"

    if not output_yamlpath.exists():
        txt, output_yamlpath = interpret_bail_with_formatted_yaml(
            new_bail_path, output_yamlpath
        )
        # convert_markdown_to_beamer(
        #     output_mdpath,
        #     beamer_pdfpath,
        #     beamer_texpath,
        #     title=f"Informations {new_bail_path.name}",
        # )

    LOGGER.info(f"Picked infos available in {output_yamlpath}")

    LOGGER.info("Global request")

    output_mdpath = output_folder / "global_extraction_results.md"
    beamer_mdpath = output_folder / "global_slides_results.md"
    beamer_pdfpath = output_folder / "global_slides_results.pdf"
    beamer_texpath = output_folder / "global_slides_results.tex"

    if not output_mdpath.exists():
        txt, output_mdpath = global_request_bail(new_bail_path, output_mdpath)
        convert_markdown_to_beamer(
            output_mdpath,
            beamer_pdfpath,
            beamer_texpath,
            title=f"Summary {new_bail_path.name}",
        )

    LOGGER.info(f"Summary beamer available in {beamer_pdfpath}")

    return


if __name__ == "__main__":

    # main()

    # test output yaml
    bail_path = Path(
        r"C:\Users\lvolat\Documents\cocoAI\data\Annexe_6_b_-_Bail_du_29_mars_2016.pdf"
    )
    new_bail_path = rename_file_unix_compatible(bail_path)
    output_folder = obtain_output_folder(new_bail_path.stem, kind="bail", number="")
    LOGGER.info("First let us pick some precise infos")
    output_mdpath = output_folder / "extraction_results.md"

    interpret_bail_with_formatted_yaml(new_bail_path, output_mdpath)
