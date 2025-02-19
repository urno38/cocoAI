from common.logconfig import LOGGER
from pathlib import Path
from cocoAI.etablissement import main
from common.identifiers import pick_id


# BLOC ENTREPRISE
entreprise = "LE_BISTROT_VALOIS"
main(siret=pick_id(entreprise, kind="siret"), entreprise=entreprise)
