from common.FEC import extract_df_FEC
from common.path import COMMERCIAL_DOCUMENTS_PATH, TMP_PATH

excel_path_list = [
    (
        COMMERCIAL_DOCUMENTS_PATH
        / "2 - DOSSIERS à l'ETUDE"
        / "CHIEN QUI FUME (Le) - 75001 PARIS - 33 Rue du PONT-NEUF"
        / "3. DOCUMENTATION FINANCIÈRE"
        / "2022 - GALLA - GL.xlsx"
    ),
    (
        COMMERCIAL_DOCUMENTS_PATH
        / "2 - DOSSIERS à l'ETUDE"
        / "CHIEN QUI FUME (Le) - 75001 PARIS - 33 Rue du PONT-NEUF"
        / "3. DOCUMENTATION FINANCIÈRE"
        / "2023 - GALLA - GL.xlsx"
    ),
]
df = extract_df_FEC(excel_path_list)

salaires = df[df.Compte.apply(lambda x: True if x[0] == "S" else False)].query(
    "year==2023"
)
salaires.to_csv(TMP_PATH / "toto.csv")

print(salaires["credit-debit"].sum())
