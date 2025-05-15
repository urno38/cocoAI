from common.folder_tree import get_enseigne_folder_path, get_mistral_work_path


def get_prompt_mistral_resume(siret):

    # prompt = "Etant donnée la liasse fiscale fournie en pièce jointe"

    prompt = """Résume le document fourni en pièce jointe en présentant en particulier : 
- quelle est l'année N
- le bilan actif net de l'exercice N
- le bilan passif net de l'exercice N
- le compte de résultats net de l'exercice N
- le résumé des immobilisations de l'exercice N
Le résumé doit être fourni en français au format markdown. """

    return prompt


def get_prompt_mistral_detaille(siret):

    # prompt = "Etant donnée la liasse fiscale fournie en pièce jointe"

    prompt = """Retranscris de manière détaillée le document fourni en pièce jointe en présentant en particulier : 
- quelle est l'année N
- tous les montants nets du bilan actif net de l'exercice N et son total
- tous les montants nets du bilan passif net de l'exercice N et son total
- tous les montants nets du compte de résultats de l'exercice N et son total
- tous les montants nets des immobilisations de l'exercice N et son total
Le résultat doit être fourni en français au format markdown. """

    return prompt


def get_liasse_md_path(siret, liasse_path):
    return (
        get_mistral_work_path(siret)
        / "OUTPUT_LIASSES"
        / liasse_path.with_suffix(".md").name
    )


def get_liasse_list_in_folder(siret):
    return [
        l
        for l in list(get_enseigne_folder_path(siret).rglob("*.pdf"))
        if "liasse" in l.name.lower()
    ] + [
        l
        for l in list(
            (
                get_enseigne_folder_path(siret)
                / "DOCUMENTATION_FINANCIERE"
                / "BILANS_CA"
            ).glob("*")
        )
        if "liasse" not in l.name.lower()
    ]
