from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import xlsxwriter

from cocoAI.FEC import load_excel_data, load_nomenclature
from common.logconfig import LOGGER
from common.path import COMMON_PATH, DATA_PATH, WORK_PATH

# PRODUCTION DE LA FEUILLE EXCEL du SOLDE INTERMEDIAIRE DE GESTION


def define_formats():
    # je definis mes formats
    formats_dict = {"bold": {"bold": True}, "normal": {"bold": False}}
    return formats_dict


def Solde_intermediaire_de_gestion(
    dfd, workbook, row, col, refyear, curyear, sheet_name="SIG"
):
    # solde intermédiaires de gestion détaillés
    # SAS GALLA pour 2022 p.6/73
    # print(df[df["Classe"] == "7"]["Crédit"].sum())

    formats_dict = define_formats()
    worksheet = workbook.add_worksheet(sheet_name)
    # je stocke les row col initiales

    # dfnom = load_nomenclature(yaml_path=COMMON_PATH / "nomenclature.yaml")

    row_init = row
    col_init = col

    # premiere ligne les entetes
    worksheet.write(row, col, "Solde intermédiaire de gestion")
    col += 1
    # TODO a particulariser
    worksheet.write(row, col, "au 31/12/2023")
    col += 1

    # Marges commerciales
    # NON CODE POUR L INSTANT N APPARAIT PAS DANS LE BILAN DE GALLA
    # worksheet.write(row, col, "au 31/12/2023")

    def add_line_SIG(txt, curvalue, refvalue, format, beginning_row, beginning_col):
        print(curvalue, refvalue)
        row = beginning_row
        col = beginning_col
        worksheet.write(row, col, txt, format)
        col += 1
        worksheet.write(row, col, curvalue, format)
        col += 1
        worksheet.write(row, col, refvalue, format)
        col += 1
        worksheet.write(row, col, float(curvalue) - float(refvalue), format)
        col += 1
        if refvalue != 0:
            worksheet.write(
                row, col, (float(curvalue) / float(refvalue) - 1) * 100, format
            )
        else:
            worksheet.write(row, col, np.nan, format)
        return row, col

    normal = workbook.add_format(formats_dict["normal"])
    bold = workbook.add_format(formats_dict["bold"])

    compte_productions_vendues = ["706310", "706320", "706350", "708000"]

    row, col = add_line_SIG(
        "Production vendue",
        dfd[int(curyear)]["Débit"].sum(),
        dfd[int(refyear)]["Débit"].sum(),
        bold,
        row,
        col_init,
    )
    row += 1

    for Compte in ["706310", "706320", "706350", "708000"]:
        row, col = add_line_SIG(
            f"{Compte} {Compte}",
            dfd[int(curyear)].query(f"Compte=='{Compte}'")["Débit"].sum(),
            dfd[int(refyear)].query(f"Compte=='{Compte}'")["Débit"].sum(),
            normal,
            row,
            col_init,
        )
        row += 1

    # TODO code production stockee
    # TODO code production immobilisee

    # PRODUCTION DE L EXERCICE
    for Compte in ["706310", "706320", "706350", "708000"]:
        row, col = add_line_SIG(
            f"{Compte} {Compte}",
            dfd[int(curyear)].query(f"Compte=='{Compte}'")["Débit"].sum(),
            dfd[int(refyear)].query(f"Compte=='{Compte}'")["Débit"].sum(),
            normal,
            row,
            col_init,
        )
        row += 1

    return row, col


def Comptes_de_resultats_detaille(
    df, workbook, row, col, sheet_name="Compte_resultats"
):
    worksheet = workbook.add_worksheet(sheet_name)
    # solde intermédiaires de gestion détaillés
    # SAS GALLA pour 2022 p.34
    # print(df[df["Classe"] == "7"]["Crédit"].sum())
    return row, col


def Capacite_auto_financement(dfd, workbook, row, col, sheet_name):
    worksheet = workbook.add_worksheet(sheet_name)

    return row, col


def Bilan_actif_detaille(dfd, workbook, row, col, sheet_name):
    # p30 du rapport GALLA In Extenso
    # worksheet = workbook.add_worksheet(sheet_name)
    return row, col


def Bilan_passif_detaille(dfd, workbook, row, col, sheet_name):

    return row, col


def Bilan_detaille(dfd, workbook, row, col, sheet_name):
    # Bilan Actif detaille p.30
    worksheet = workbook.add_worksheet(sheet_name)
    row, col = Bilan_actif_detaille(dfd, workbook, row, col, sheet_name)
    row, col = Bilan_passif_detaille(dfd, workbook, row, col, sheet_name)
    return row, col


def main(dfFEC, test=False):

    xlsx_path = Path(WORK_PATH / "pandas_multiple.xlsx")
    LOGGER.info(f"On ouvre le fichier {xlsx_path.resolve()} ! ")

    # init du fichier

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

    # Solde intermédiaire de gestion
    if 1:
        sheet_name = "SIG"
        refyear = 2022
        curyear = 2023
        row, col = Solde_intermediaire_de_gestion(
            dfd, workbook, row, col, refyear, curyear, "SIG"
        )

    # Analyse des comptes de resultats
    if 0:
        sheet_name = "Comptes_resultats"
        # row = 0
        # column = 0
        # row, column = Comptes_de_resultats_detaille(dfd, workbook, row, column, sheet_name)

    if 0:
        # Analyse financiere
        sheet_name = "Capacite_autofinancement"
        # row = 0
        # column = 0
        # row, column = Capacite_auto_financement(dfd, workbook, row, column, sheet_name)

    LOGGER.info(f"On ferme le fichier {xlsx_path.resolve()} ! ")
    if test:
        workbook.close()
    else:
        writer.close()
    return


if __name__ == "__main__":
    excel_path_list = list(DATA_PATH.glob("202*GL*xls*"))[:2]
    df = load_excel_data(excel_path_list)
    df["Classe"] = df["Compte"].apply(lambda x: str(x[0]))
    df["year"] = df["Date"].apply(lambda x: datetime.strptime(x, "%d/%M/%Y").year)
    # main(df)
    main(df, test=True)
