import logging
import os
import subprocess


def execute_program(program_path, args=None, stdout_path=None, stderr_path=None):
    """
    Exécute un programme externe avec des arguments et redirige les sorties standard et d'erreur vers des fichiers spécifiés.

    :param program_path: Chemin vers le programme externe à exécuter.
    :param args: Liste des arguments à passer au programme.
    :param stdout_path: Chemin vers le fichier où la sortie standard sera redirigée.
    :param stderr_path: Chemin vers le fichier où les erreurs standard seront redirigées.
    """
    if args is None:
        args = []

    with (
        open(stdout_path, "w") if stdout_path else open(os.devnull, "w")
    ) as stdout_file, (
        open(stderr_path, "w") if stderr_path else open(os.devnull, "w")
    ) as stderr_file:

        # Exécuter le programme externe avec les arguments
        result = subprocess.run(
            [program_path] + args, stdout=stdout_file, stderr=stderr_file
        )

    logging.info(program_path, args)
    # Vérifier le code de retour
    if result.returncode == 0:
        logging.info("Le programme s'est exécuté avec succès.")
    else:
        logging.error(
            f"Le programme a échoué avec le code de retour {result.returncode}."
        )


if __name__ == "__main__":
    # Exemple d'utilisation
    program_path = (
        "/chemin/vers/votre/programme"  # Remplacez par le chemin de votre programme
    )
    args = [
        "arg1",
        "arg2",
        "--option",
        "value",
    ]  # Remplacez par les arguments de votre programme
    stdout_path = "sortie_standard.txt"
    stderr_path = "erreurs_standard.txt"

    execute_program(program_path, args, stdout_path, stderr_path)
