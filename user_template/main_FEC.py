from cocoAI.FEC import main
from common.path import DATA_PATH

excel_path_list = list(DATA_PATH.glob("202*xls*"))[:2]
main(excel_path_list)
