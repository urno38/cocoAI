import sys
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
    LOGGER.info("on récupère les formats")
    # je definis mes formats
    formats_dict = {"bold": {"bold": True}, "normal": {"bold": False}}
    return formats_dict


def get_unique_label_in_df(df, identifiant, type="compte"):

    if type == "compte":
        # print(df.columns)
        # print(f"Compte=='{identifiant}'")
        series_du_label = df.query(f"Compte=='{identifiant}'")[
            "Intitulé"
        ].drop_duplicates()
        # print(series_du_label)
        LOGGER.debug(identifiant)
        LOGGER.debug(series_du_label)
        # sys.exit()
        if len(series_du_label) == 1:
            LOGGER.debug(series_du_label)
            return series_du_label.iat[0]
        elif len(series_du_label) > 1:
            LOGGER.debug(
                f"plusieurs labels pour le Compte {identifiant}, je prends l ID du compte"
            )
            return str(identifiant).strip()
        else:
            LOGGER.debug(series_du_label)
            raise ValueError(f"pas d ecriture comptable pour le compte {identifiant}")
    elif type == "idlvl3":
        series_du_label = df.query(f"idlvl3=='{identifiant}'")[
            "Intitulé"
        ].drop_duplicates()
        if len(series_du_label) == 1:
            LOGGER.debug(series_du_label)
            return series_du_label.iat[0]
        elif len(series_du_label) > 1:
            LOGGER.debug(
                f"plusieurs labels pour l idlvl3 {identifiant}, je prends l ID du compte"
            )
            return str(identifiant).strip()
        else:
            LOGGER.debug(series_du_label)
            raise ValueError(f"pas d ecriture comptable pour l'idlvl3 {identifiant}")
    else:
        raise ValueError("not implemented")


def Solde_intermediaire_de_gestion(
    dfd, df, workbook, row, col, refyear, curyear, sheet_name="SIG"
):
    LOGGER.info("Let us pick up the SIG")
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
        # print(curvalue, refvalue)
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

    LOGGER.info("Production vendue")
    row, col = add_line_SIG(
        "Production vendue",
        dfd[int(curyear)].query("idlvl2=='70'")["Débit"].sum(),
        dfd[int(refyear)].query("idlvl2=='70'")["Débit"].sum(),
        bold,
        row,
        col_init,
    )
    row += 1

    LOGGER.info("Détail Production vendue")
    compte_productions_vendues = ["706310", "706320", "706350", "708000"]
    for compte in compte_productions_vendues:
        LOGGER.info(f"Compte {compte}")
        row, col = add_line_SIG(
            f"{compte} {get_unique_label_in_df(df,compte)}",
            dfd[int(curyear)].query(f"Compte=='{compte}'")["Débit"].sum(),
            dfd[int(refyear)].query(f"Compte=='{compte}'")["Débit"].sum(),
            normal,
            row,
            col_init,
        )
        row += 1

    LOGGER.info("Production stockée")
    row, col = add_line_SIG(
        "Production stockée",
        dfd[int(curyear)].query("idlvl2=='71'")["Débit"].sum(),
        dfd[int(refyear)].query("idlvl2=='71'")["Débit"].sum(),
        bold,
        row,
        col_init,
    )
    row += 1

    LOGGER.info("Production immobilisée")
    row, col = add_line_SIG(
        "Production immobilisée",
        dfd[int(curyear)].query("idlvl2=='72'")["Débit"].sum(),
        dfd[int(refyear)].query("idlvl2=='72'")["Débit"].sum(),
        bold,
        row,
        col_init,
    )
    row += 1

    LOGGER.info("Détail Production immobilisée")
    idlvl3_productions_vendues = ["721", "722"]
    for idlvl3 in idlvl3_productions_vendues:
        LOGGER.info(f"idlvl3 {idlvl3}")
        row, col = add_line_SIG(
            f"{idlvl3} {get_unique_label_in_df(df,idlvl3,type='idlvl3')}",
            dfd[int(curyear)].query(f"idlvl3=='{idlvl3}'")["Débit"].sum(),
            dfd[int(refyear)].query(f"idlvl3=='{idlvl3}'")["Débit"].sum(),
            normal,
            row,
            col_init,
        )
        row += 1

    # # PRODUCTION DE L EXERCICE
    # for compte in ["706310", "706320", "706350", "708000"]:
    #     row, col = add_line_SIG(
    #         f"{compte} {compte}",
    #         dfd[int(curyear)].query(f"Compte=='{compte}'")["Débit"].sum(),
    #         dfd[int(refyear)].query(f"Compte=='{compte}'")["Débit"].sum(),
    #         normal,
    #         row,
    #         col_init,
    #     )
    #     row += 1

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
            dfd, df, workbook, row, col, refyear, curyear, "SIG"
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
    df["idlvl2"] = df["Compte"].apply(lambda x: str(x[:2]))
    df["idlvl3"] = df["Compte"].apply(lambda x: str(x[:3]))
    df["year"] = df["Date"].apply(lambda x: datetime.strptime(x, "%d/%M/%Y").year)
    # main(df)
    main(df, test=True)
