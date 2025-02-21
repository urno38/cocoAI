from cocoAI.bail import main
from common.path import DATA_PATH

# main(bail_path=list(DATA_PATH.glob("*Annexe*6_b*Bail*pdf"))[0])
main(bail_path=list(DATA_PATH.glob("*GILBERTE*/**/*BAIL*SEINE*.pdf"))[0])
main(bail_path=list(DATA_PATH.glob("*CIAL*BAIL*20150101.pdf"))[0])
main(bail_path=list(DATA_PATH.glob("*CIAL*BAIL*20240101.pdf"))[0])