from pathlib import Path

from cocoAI.etablissement import main
from common.identifiers import pick_id
from common.logconfig import LOGGER

# BLOC ENTREPRISE
entreprise = "LE_BISTROT_VALOIS"
main(siret=pick_id(entreprise, kind="siret"), etablissement=entreprise)
