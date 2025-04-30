import pprint

from cocoAI.doc_sort import main
from common.logconfig import LOGGER
from common.path import COMMERCIAL_DOCUMENTS_PATH

if 0:
    siret = "31013032300028"
    CHIEN_QUI_FUME_PATH = list(COMMERCIAL_DOCUMENTS_PATH.glob("*/CHIEN QUI FUME*"))[0]
    SOCIAL = list(CHIEN_QUI_FUME_PATH.glob("*SOCIAL*"))[0]
    PAIE = SOCIAL / "PAIE 10"
    salaires_list = list(PAIE.glob("*Dernier*")) + list(PAIE.glob("*Normal*"))
    DOC_FINANCIERE = list(CHIEN_QUI_FUME_PATH.glob("*DOCUMENTATION FI*"))[0]
    PDF_DOCS = list(DOC_FINANCIERE.glob("*.pdf"))

    LOGGER.info(CHIEN_QUI_FUME_PATH)

    pprint.pprint(PDF_DOCS)
    for path in PDF_DOCS[10:]:
        print(path)
        main(path, siret)

else:
    etablissement_name = "BISTROT_VALOIS"
    main(etablissement_name)


# TODO : coder quelquechose pour assurer le coup où le scan se passe mal
# ex : file:///C:/Users/lvolat/COMPTOIRS%20ET%20COMMERCES/DATALAKE%20-%20Documents/BISTROT_VALOIS/BISTROT_VALOIS/REFERENCE_DOCUMENTS/BAUX_QUITTANCE/Chainel_Carla.pdf
# pour BISTROT VALOIS ça se passe pas très bien ...
