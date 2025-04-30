from pathlib import Path

from cocoAI.bail import main
from common.path import COMMERCIAL_DOCUMENTS_PATH

# Mettre les paths sous la forme
# bail_path = Path(r"<chemin a copier ici>")

# for bail_path in COMMERCIAL_DOCUMENTS_PATH.glob("**/*Annexe*6_b*Bail*pdf"):
#     main(bail_path=bail_path)

# main(
#     bail_path=list(COMMERCIAL_DOCUMENTS_PATH.glob("**/*GILBERTE*/**/*BAIL*SEINE*.pdf"))[
#         0
#     ]
# )
# main(bail_path=list(COMMERCIAL_DOCUMENTS_PATH.glob("**/*CIAL*BAIL*20150101.pdf"))[0])
# main(bail_path=list(COMMERCIAL_DOCUMENTS_PATH.glob("**/*CIAL*BAIL*20240101.pdf"))[0])


main(
    Path(
        r"C:\Users\lvolat\COMPTOIRS ET COMMERCES\DATALAKE - Documents\GALLA_310130323\LE_CHIEN_QUI_FUME\REFERENCE_DOCUMENTS\BAUX_QUITTANCE\2016_GALLA_BAIL_LOT_1_Boutique_Principale.pdf"
    )
)
