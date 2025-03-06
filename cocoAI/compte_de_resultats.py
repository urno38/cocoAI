from pathlib import Path

import pandas as pd
import xlsxwriter

from cocoAI.bilan import compte_de_resultats
from common.FEC import extract_df_FEC
from common.logconfig import LOGGER
from common.path import COMMERCIAL_ONE_DRIVE_PATH, WORK_PATH


def main(excel_path_list, test=False):

    df = extract_df_FEC(excel_path_list)
    xlsx_path = Path(WORK_PATH / "Compte_de_resultats_detailles.xlsx")
    LOGGER.info(f"On ouvre le fichier {xlsx_path.resolve()} ! ")

    engine_options = {"nan_inf_to_errors": True}

    if not test:
        writer = pd.ExcelWriter(
            xlsx_path,
            engine="xlsxwriter",
            engine_kwargs={"options": engine_options},
        )
        export_columns = ["Compte", "Intitulé", "Date", "Journal"]
        sorted_columns = export_columns + [
            c for c in df.columns if c not in export_columns
        ]

        df[sorted_columns].to_excel(writer, sheet_name="raw data")
        # Get the xlsxwriter objects from the dataframe writer object.
        workbook = writer.book
        # worksheet = writer.sheets['Sheet1']
    else:
        workbook = xlsxwriter.Workbook(xlsx_path, engine_options)
        # worksheet = workbook.add_worksheet()

    # je cree un dictionnaire qui va servir de colonnes pour mon excel
    dfd = {y: df[df.year == y] for y in df["year"].drop_duplicates()}

    row = 0
    col = 0

    sheet_name = "Compte_de_resultats"
    refyear = 2022
    curyear = 2023
    LOGGER.info("Let us pick up the CR")
    row, col, benefice_curyear, benefice_refyear = compte_de_resultats(
        dfd, df, workbook, row, col, refyear, curyear, sheet_name
    )

    LOGGER.info(f"On ferme le fichier {xlsx_path.resolve()} ! ")
    if test:
        workbook.close()
    else:
        writer.close()
    return


if __name__ == "__main__":

    excel_path_list = [
        (
            COMMERCIAL_ONE_DRIVE_PATH
            / "2 - DOSSIERS à l'ETUDE"
            / "CHIEN QUI FUME (Le) - 75001 PARIS - 33 Rue du PONT-NEUF"
            / "3. DOCUMENTATION FINANCIÈRE"
            / "2022 - GALLA - GL.xlsx"
        ),
        (
            COMMERCIAL_ONE_DRIVE_PATH
            / "2 - DOSSIERS à l'ETUDE"
            / "CHIEN QUI FUME (Le) - 75001 PARIS - 33 Rue du PONT-NEUF"
            / "3. DOCUMENTATION FINANCIÈRE"
            / "2023 - GALLA - GL.xlsx"
        ),
    ]

    main(excel_path_list, test=True)
