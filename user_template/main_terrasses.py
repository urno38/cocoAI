from cocoAI.terrasse import main
from common.identifiers import pick_id

# # BLOC ENTREPRISE
etablissement = "LE_BISTROT_VALOIS"
main(siret=pick_id(etablissement, kind="siret"), etablissement=etablissement)

# etablissement = "LE_JARDIN_DE_ROME"
# main(siret=pick_id(etablissement, kind="siret"), etablissement=etablissement)

# main(siret="652014754", etablissement="toto")
