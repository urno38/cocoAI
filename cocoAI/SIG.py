from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import xlsxwriter

from common.FEC import load_excel_data
from common.logconfig import LOGGER
from common.path import DATA_PATH, WORK_PATH

# PRODUCTION DE LA FEUILLE EXCEL du SOLDE INTERMEDIAIRE DE GESTION


def calcule_balance_cred_moins_deb(df):
    # pour rendre le code compact
    return df["Crédit"].sum() - df["Débit"].sum()


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


def add_line_SIG(
    worksheet,
    txt,
    curvalue,
    refvalue,
    format,
    beginning_row,
    beginning_col,
    signe="+",
):
    if signe not in ["+", "-", ""]:
        raise ValueError("not implemented")
    if signe == "-":
        refvalue = (-1) * refvalue
        curvalue = (-1) * curvalue
    row = beginning_row
    col = beginning_col

    worksheet.write(row, col, signe + txt, format)
    col += 1
    # Affichage de l oppose de la valeur
    worksheet.write_number(row, col, curvalue, format)
    col += 1
    worksheet.write_number(row, col, refvalue, format)
    col += 1
    worksheet.write_number(row, col, float(curvalue) - float(refvalue), format)
    col += 1
    if refvalue != 0:
        worksheet.write_number(
            row, col, (float(curvalue) / float(refvalue) - 1) * 100, format
        )
    else:
        worksheet.write_number(row, col, np.nan, format)
    return row, col


def Solde_intermediaire_de_gestion(
    dfd, df, workbook, row, col, refyear, curyear, sheet_name="SIG"
):
    # solde intermédiaires de gestion détaillés
    # SAS GALLA pour 2022 p.6/73
    # print(df[df["Classe"] == "7"]["Crédit"].sum())

    # definition des formats
    formats_dict = define_formats()
    normal = workbook.add_format(formats_dict["normal"])
    bold = workbook.add_format(formats_dict["bold"])

    worksheet = workbook.add_worksheet(sheet_name)

    row_init = row
    col_init = col

    # ENTETES DE PREMIERE LIGNE
    worksheet.write(row, col, "Solde intermédiaire de gestion")
    col += 1
    worksheet.write(row, col, f"Année {int(curyear)}")
    col += 1
    worksheet.write(row, col, f"Année {int(refyear)}")
    col += 1
    worksheet.write(row, col, f"Variation absolue")
    col += 1
    worksheet.write(row, col, f"Variation %")
    col += 1
    row += 1

    # Marges commerciales
    # TODO NON CODE POUR L INSTANT N APPARAIT PAS DANS LE BILAN DE GALLA
    marge_commerciale_curyear = 0
    marge_commerciale_refyear = 0
    # worksheet.write(row, col, "au 31/12/2023")

    LOGGER.info("Production vendue")
    productions_vendues_curyear = calcule_balance_cred_moins_deb(
        dfd[int(curyear)].query("idlvl2=='70'")
    )
    productions_vendues_refyear = calcule_balance_cred_moins_deb(
        dfd[int(refyear)].query("idlvl2=='70'")
    )
    row, col = add_line_SIG(
        worksheet,
        "\tProduction vendue",
        productions_vendues_curyear,
        productions_vendues_refyear,
        bold,
        row,
        col_init,
    )
    row += 1
    LOGGER.info("Détail Production vendue")
    compte_productions_vendues = ["706310", "706320", "706350", "708000"]
    for compte in compte_productions_vendues:
        LOGGER.info(f"Compte {compte}")
        label = f"\t\t{compte} {get_unique_label_in_df(df,compte)}"
        LOGGER.info(label)
        row, col = add_line_SIG(
            worksheet,
            label,
            calcule_balance_cred_moins_deb(
                dfd[int(curyear)].query(f"Compte=='{compte}'")
            ),
            calcule_balance_cred_moins_deb(
                dfd[int(refyear)].query(f"Compte=='{compte}'")
            ),
            normal,
            row,
            col_init,
        )
        row += 1
    LOGGER.info("Production stockée")
    production_stockee_curyear = calcule_balance_cred_moins_deb(
        dfd[int(curyear)].query("idlvl2=='71'")
    )
    production_stockee_refyear = calcule_balance_cred_moins_deb(
        dfd[int(refyear)].query("idlvl2=='71'")
    )
    row, col = add_line_SIG(
        worksheet,
        "\tProduction stockée",
        production_stockee_curyear,
        production_stockee_refyear,
        bold,
        row,
        col_init,
    )
    row += 1
    LOGGER.info("Production immobilisée")
    productions_immobilisees_curyear = calcule_balance_cred_moins_deb(
        dfd[int(curyear)].query("idlvl2=='72'")
    )
    productions_immobilisees_refyear = calcule_balance_cred_moins_deb(
        dfd[int(refyear)].query("idlvl2=='72'")
    )
    row, col = add_line_SIG(
        worksheet,
        "\tProduction immobilisée",
        productions_immobilisees_curyear,
        productions_immobilisees_refyear,
        bold,
        row,
        col_init,
    )
    row += 1

    try:
        LOGGER.info("Détail Production immobilisée")
        idlvl3_productions_vendues = ["721", "722"]
        for idlvl3 in idlvl3_productions_vendues:
            LOGGER.info(f"idlvl3 {idlvl3}")
        label = f"\t\t{idlvl3} {get_unique_label_in_df(df,idlvl3,type='idlvl3')}"
        LOGGER.info(label)
        row, col = add_line_SIG(
            worksheet,
            label,
            calcule_balance_cred_moins_deb(
                dfd[int(curyear)].query(f"idlvl3=='{idlvl3}'")
            ),
            calcule_balance_cred_moins_deb(
                dfd[int(refyear)].query(f"idlvl3=='{idlvl3}'")
            ),
            normal,
            row,
            col_init,
        )
        row += 1
    except:
        LOGGER.debug(f"pas d ecriture comptable pour l'idlvl3 {idlvl3}")

    # PRODUCTION DE L EXERCICE
    production_exercice_curyear = (
        productions_vendues_curyear
        - production_stockee_curyear
        - productions_immobilisees_curyear
    )
    production_exercice_refyear = (
        productions_vendues_refyear
        - production_stockee_refyear
        - productions_immobilisees_refyear
    )
    row, col = add_line_SIG(
        worksheet,
        f"\t\t\tProduction de l'exercice",
        production_exercice_curyear,
        production_exercice_refyear,
        bold,
        row,
        col_init,
        signe="",
    )
    row += 1

    # variation des matières premières
    LOGGER.info("Matières premières et approvisionnements consommés")
    raw_mat_columns = ["601", "603"]
    raw_mat_appro_consommes_curyear = calcule_balance_cred_moins_deb(
        dfd[int(curyear)].query("idlvl3 in @raw_mat_columns")
    )
    raw_mat_appro_consommes_refyear = calcule_balance_cred_moins_deb(
        dfd[int(refyear)].query("idlvl3 in @raw_mat_columns")
    )
    row, col = add_line_SIG(
        worksheet,
        "\tMatières premières et approvisionnements consommés",
        raw_mat_appro_consommes_curyear,
        raw_mat_appro_consommes_refyear,
        bold,
        row,
        col_init,
        signe="-",
    )
    row += 1
    LOGGER.info("Détail Matières premières et approvisionnements consommés")
    compte_productions_vendues = ["601100", "601200", "603100", "609000", "609100"]
    for compte in compte_productions_vendues:
        LOGGER.info(f"Compte {compte}")
        label = f"\t\t\t{compte} {get_unique_label_in_df(df,compte)}"
        LOGGER.info(label)
        row, col = add_line_SIG(
            worksheet,
            label,
            calcule_balance_cred_moins_deb(
                dfd[int(curyear)].query(f"Compte=='{compte}'")
            ),
            calcule_balance_cred_moins_deb(
                dfd[int(refyear)].query(f"Compte=='{compte}'")
            ),
            normal,
            row,
            col_init,
            signe="-",
        )
        row += 1
    LOGGER.info("Sous traitance directe")
    sous_traitance_columns = ["604"]
    sous_traitance_directe_curyear = calcule_balance_cred_moins_deb(
        dfd[int(curyear)].query("idlvl3 in @sous_traitance_columns")
    )
    sous_traitance_directe_refyear = calcule_balance_cred_moins_deb(
        dfd[int(curyear)].query("idlvl3 in @sous_traitance_columns")
    )
    row, col = add_line_SIG(
        worksheet,
        "\tSous traitance directe",
        sous_traitance_directe_curyear,
        sous_traitance_directe_refyear,
        bold,
        row,
        col_init,
        signe="-",
    )
    row += 1
    LOGGER.info("Détail Sous-traitance directe")
    compte_productions_vendues = list(
        (df.query("idlvl3 in @raw_mat_columns")["Compte"].drop_duplicates().values)
    )
    for compte in compte_productions_vendues:
        LOGGER.info(f"Compte {compte}")
        label = f"\t\t\t{compte} {get_unique_label_in_df(df,compte)}"
        LOGGER.info(label)
        row, col = add_line_SIG(
            worksheet,
            label,
            calcule_balance_cred_moins_deb(
                dfd[int(curyear)].query(f"Compte=='{compte}'")
            ),
            calcule_balance_cred_moins_deb(
                dfd[int(refyear)].query(f"Compte=='{compte}'")
            ),
            normal,
            row,
            col_init,
            signe="-",
        )
        row += 1

    # MARGE BRUTE SUR PRODUCTION (II)
    LOGGER.info("Marge brute sur production (II)")
    marge_brute_curyear = (
        production_exercice_curyear
        + raw_mat_appro_consommes_curyear
        + sous_traitance_directe_curyear
    )
    marge_brute_refyear = (
        production_exercice_refyear
        + raw_mat_appro_consommes_refyear
        + sous_traitance_directe_refyear
    )
    row, col = add_line_SIG(
        worksheet,
        f"\t\t\tMARGE brute sur production (II)",
        marge_brute_curyear,
        marge_brute_refyear,
        bold,
        row,
        col_init,
        signe="",
    )
    row += 1

    # MARGE BRUTE GLOBALE (I+II)
    LOGGER.info("MARGE BRUTE GLOBALE")
    marge_brute_globale_curyear = marge_commerciale_curyear + marge_brute_curyear
    marge_brute_globale_refyear = marge_commerciale_refyear + marge_brute_refyear
    row, col = add_line_SIG(
        worksheet,
        f"\t\t\tMarge brute globale (I+II)",
        marge_brute_globale_curyear,
        marge_brute_globale_refyear,
        bold,
        row,
        col_init,
        signe="",
    )
    row += 1

    # Services extérieurs et autres charges externes
    LOGGER.info("Services extérieurs et autres charges externes")
    services_ext_columns = ["61", "62"]
    services_ext_curyear = calcule_balance_cred_moins_deb(
        dfd[int(curyear)].query("idlvl2 in @services_ext_columns")
    )
    services_ext_refyear = calcule_balance_cred_moins_deb(
        dfd[int(refyear)].query("idlvl2 in @services_ext_columns")
    )
    row, col = add_line_SIG(
        worksheet,
        "\tServices extérieurs et autres charges externes",
        services_ext_curyear,
        services_ext_refyear,
        bold,
        row,
        col_init,
        signe="-",
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

    xlsx_path = Path(WORK_PATH / "Solde_intermediaire_de_gestion.xlsx")
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
        LOGGER.info("Let us pick up the SIG")
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
