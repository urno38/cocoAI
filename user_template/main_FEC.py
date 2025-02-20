from cocoAI.FEC import load_excel_data, main
from common.path import DATA_PATH

excel_path_list = list(DATA_PATH.glob("202*xls*"))[:2]
df = load_excel_data(excel_path_list)
main(excel_path_list)
