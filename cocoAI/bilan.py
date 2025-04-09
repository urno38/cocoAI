import copy
from pathlib import Path

import pandas as pd
import xlsxwriter

from cocoAI.bilan_simplifie import bilan_simplifiev2
from cocoAI.compte_de_resultats import compte_de_resultats
from common.FEC import (
    add_line_elementary,
    add_line_idlist,
    add_macro_categorie_and_detail,
    calcule_balance_cred_moins_deb,
    define_formats,
    export_raw_data_by_year,
    extract_df_FEC,
)
from common.identifiers import get_official_nomenclature, get_query_from_id_list
from common.logconfig import LOGGER
from common.path import COMMERCIAL_DOCUMENTS_PATH, WORK_PATH


def bilan_actif(
    dfdbilan, df, workbook, refbilanyear, curbilanyear, sheet_name="Bilan actif"
):

    LOGGER.info("Bilan actif")

    # definition des formats
    formats_dict = define_formats(workbook)
    worksheet = workbook.add_worksheet(sheet_name)
    worksheet.freeze_panes(1, 0)

    row = 0
    col = 0
    row_init = 0
    col_init = 0

    # Let us define the width of the columns one time pour toutes
    # worksheet.set_column(0, 0, get_max_len_of_the_descriptions() / 2)
    # col_format = workbook.add_format({"bg_color": "#BCE3F1"})
    worksheet.set_column(0, 0, 40)
    worksheet.set_column(1, 1, 15)
    worksheet.set_column(2, 2, 15)
    worksheet.set_column(3, 3, 20)
    worksheet.set_column(4, 4, 20)

    # ENTETES DE PREMIERE LIGNE
    worksheet.write(row, col, "Bilan actif détaillé")
    col += 1
    cell_format = workbook.add_format({"bold": False, "align": "center"})
    worksheet.write(row, col, f"Année {int(curbilanyear)}", cell_format)
    col += 1
    worksheet.write(row, col, f"Année {int(refbilanyear)}", cell_format)
    col += 1
    worksheet.write(row, col, f"Variation absolue", cell_format)
    col += 1
    worksheet.write(row, col, f"Variation %", cell_format)
    col += 1
    row += 1
    row += 1

    worksheet.write(row, col_init, "Actif immobilisé".upper(), formats_dict["bigtitle"])
    row += 1

    worksheet.write(row, col_init, "Immobilisation incorporelles", formats_dict["bold"])
    row += 1

    for id in ["201", "203", "205", "206", "207"]:
        row, col = add_macro_categorie_and_detail(
            worksheet,
            [id],
            row,
            col_init,
            dfdbilan,
            df,
            curbilanyear,
            refbilanyear,
            formats_dict=formats_dict,
        )

    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["208", "280"],
        row,
        col_init,
        dfdbilan,
        df,
        curbilanyear,
        refbilanyear,
        format=formats_dict["normal"],
        formats_dict=formats_dict,
        label="Autres immobilisations incorporelles",
    )

    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["237", "238"],
        row,
        col_init,
        dfdbilan,
        df,
        curbilanyear,
        refbilanyear,
        format=formats_dict["normal"],
        formats_dict=formats_dict,
        label="Avances et acomptes sur immobilisations corporelles",
    )

    worksheet.write(row, col_init, "Immobilisation corporelles", formats_dict["bold"])
    row += 1

    for id in ["211", "212", "213", "215", "218", "231"]:
        row, col = add_macro_categorie_and_detail(
            worksheet,
            [id],
            row,
            col_init,
            dfdbilan,
            df,
            curbilanyear,
            refbilanyear,
            format=formats_dict["normal"],
            formats_dict=formats_dict,
            signe="-",
        )

    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["2145", "2814"],
        row,
        col_init,
        dfdbilan,
        df,
        curbilanyear,
        refbilanyear,
        format=formats_dict["normal"],
        formats_dict=formats_dict,
        label="Constructions",
        signe="-",
    )

    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["2154", "2815"],
        row,
        col_init,
        dfdbilan,
        df,
        curbilanyear,
        refbilanyear,
        format=formats_dict["normal"],
        formats_dict=formats_dict,
        label="Installations tech. et outillages industriels",
        signe="-",
    )

    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["218", "2818"],
        row,
        col_init,
        dfdbilan,
        df,
        curbilanyear,
        refbilanyear,
        format=formats_dict["normal"],
        formats_dict=formats_dict,
        label="Autres immobilisations corporelles",
        signe="-",
    )

    row, col, curyear_value, refyear_value = add_line_idlist(
        worksheet,
        ["231"],
        row,
        col_init,
        dfdbilan,
        df,
        curbilanyear,
        refbilanyear,
        format=formats_dict["normal"],
        formats_dict=formats_dict,
        signe="-",
    )

    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["237", "238"],
        row,
        col_init,
        dfdbilan,
        df,
        curbilanyear,
        refbilanyear,
        format=formats_dict["normal"],
        formats_dict=formats_dict,
        label="Avances et acomptes",
        signe="-",
    )

    worksheet.write(row, col_init, "Immobilisations financières", formats_dict["bold"])
    row += 1
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["271"],
        row,
        col_init,
        dfdbilan,
        df,
        curbilanyear,
        refbilanyear,
        format=formats_dict["normal"],
        formats_dict=formats_dict,
        signe="-",
    )
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["272"],
        row,
        col_init,
        dfdbilan,
        df,
        curbilanyear,
        refbilanyear,
        format=formats_dict["normal"],
        formats_dict=formats_dict,
        signe="-",
    )

    for id in ["266", "267", "273", "274", "275"]:
        row, col = add_macro_categorie_and_detail(
            worksheet,
            [id],
            row,
            col_init,
            dfdbilan,
            df,
            curbilanyear,
            refbilanyear,
            format=formats_dict["normal"],
            formats_dict=formats_dict,
            label=None,
            LOGGER_msg=None,
            signe="-",
        )

    idlist = ["2"]
    row, col, curyear_value_totalI, refyear_value_totalI = add_line_idlist(
        worksheet,
        idlist,
        row,
        col_init,
        dfdbilan,
        df,
        curbilanyear,
        refbilanyear,
        format=formats_dict["totaux"],
        formats_dict=formats_dict,
        label="TOTAL (I)",
        signe="-",
    )
    row += 1

    worksheet.write(row, col_init, "Actif circulant".upper(), formats_dict["bigtitle"])
    row += 1
    id_total_list = []

    # worksheet.write(row, col_init, "Stocks et en-cours", formats_dict["bold"])
    # row += 1
    ids = ["3"]
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ids,
        row,
        col_init,
        dfdbilan,
        df,
        curbilanyear,
        refbilanyear,
        format=formats_dict["normal"],
        formats_dict=formats_dict,
        signe="-",
    )
    id_total_list += ids

    # Avances et acomptes versés sur commande
    ids = ["4091"]
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ids,
        row,
        col_init,
        dfdbilan,
        df,
        curbilanyear,
        refbilanyear,
        format=formats_dict["normal"],
        formats_dict=formats_dict,
        signe="-",
    )
    id_total_list += ids

    worksheet.write(row, col_init, "Créances", formats_dict["bold"])
    row += 1

    # Clients et comptes rattachés
    ids = ["41"]
    for id in ids:
        row, col = add_macro_categorie_and_detail(
            worksheet,
            [id],
            row,
            col_init,
            dfdbilan,
            df,
            curbilanyear,
            refbilanyear,
            format=formats_dict["normal"],
            formats_dict=formats_dict,
            signe="-",
        )
    id_total_list += ids

    # Autres
    ids = ["40", "42", "43", "44", "45"]
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ids,
        row,
        col_init,
        dfdbilan,
        df,
        curbilanyear,
        refbilanyear,
        format=formats_dict["normal"],
        formats_dict=formats_dict,
        label="Autres créances",
    )
    id_total_list += ids

    ids = ["46", "47", "49"]
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ids,
        row,
        col_init,
        dfdbilan,
        df,
        curbilanyear,
        refbilanyear,
        format=formats_dict["normal"],
        formats_dict=formats_dict,
        label="Autres",
        signe="-",
    )
    id_total_list += ids

    # Capital souscrit - appelé non versé
    # source des comptes
    # https://www.compta-online.com/actif-circulant-notion-et-utilisation-ao4349
    ids = ["4562"]
    for id in ids:
        row, col, curyear_value, refyear_value = add_line_idlist(
            worksheet,
            [id],
            row,
            col_init,
            dfdbilan,
            df,
            curbilanyear,
            refbilanyear,
            format=formats_dict["normal"],
            formats_dict=formats_dict,
            signe="-",
        )
    id_total_list += ids

    # Valeurs mobilières de placement
    ids = ["506"]
    for id in ids:
        row, col = add_macro_categorie_and_detail(
            worksheet,
            [id],
            row,
            col_init,
            dfdbilan,
            df,
            curbilanyear,
            refbilanyear,
            format=formats_dict["normal"],
            formats_dict=formats_dict,
            signe="-",
        )
    id_total_list += ids

    # Instruments de trésorerie
    worksheet.write(row, col_init, "Instruments de trésorerie", formats_dict["bold"])
    row += 1
    # Disponibilités
    ids = ["51", "53", "58"]
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ids,
        row,
        col_init,
        dfdbilan,
        df,
        curbilanyear,
        refbilanyear,
        format=formats_dict["normal"],
        formats_dict=formats_dict,
        label="Disponibilités",
        signe="-",
    )
    id_total_list += ids

    # Charges constatées d'avance
    ids = ["486"]
    for id in ids:
        row, col, curyear_value, refyear_value = add_line_idlist(
            worksheet,
            [id],
            row,
            col_init,
            dfdbilan,
            df,
            curbilanyear,
            refbilanyear,
            format=formats_dict["normal"],
            formats_dict=formats_dict,
            signe="-",
        )
    id_total_list += ids

    row, col, curyear_value_totalII, refyear_value_totalII = add_line_idlist(
        worksheet,
        id_total_list,
        row,
        col_init,
        dfdbilan,
        df,
        curbilanyear,
        refbilanyear,
        format=formats_dict["totaux"],
        formats_dict=formats_dict,
        label="TOTAL (II)",
        signe="-",
    )
    row += 1

    # id_total_list = []

    # Frais d'emission d'emprunts à étaler
    ids = ["4816"]
    for id in ids:
        row, col, curyear_value_totalIII, refyear_value_totalIII = add_line_idlist(
            worksheet,
            [id],
            row,
            col_init,
            dfdbilan,
            df,
            curbilanyear,
            refbilanyear,
            format=formats_dict["normal"],
            formats_dict=formats_dict,
            signe="-",
        )
    # id_total_list += ids

    # Prime de remboursement des obligations
    ids = ["169"]
    for id in ids:
        row, col, curyear_value_totalIV, refyear_value_totalIV = add_line_idlist(
            worksheet,
            [id],
            row,
            col_init,
            dfdbilan,
            df,
            curbilanyear,
            refbilanyear,
            format=formats_dict["normal"],
            formats_dict=formats_dict,
            signe="-",
        )
    # id_total_list += ids

    # Ecarts de conversion actif
    ids = ["476", "477"]
    row, col, curyear_value_totalV, refyear_value_totalV = add_line_idlist(
        worksheet,
        ids,
        row,
        col_init,
        dfdbilan,
        df,
        curbilanyear,
        refbilanyear,
        format=formats_dict["normal"],
        formats_dict=formats_dict,
        label="Ecart de conversion actif",
        signe="-",
    )
    # id_total_list += ids

    LOGGER.debug("TOTAL GENERAL (I à V)")

    row, col = add_line_elementary(
        worksheet,
        "TOTAL GENERAL (I à V)",
        (
            curyear_value_totalI
            + curyear_value_totalII
            + curyear_value_totalIII
            + curyear_value_totalIV
            + curyear_value_totalV
        ),
        (
            refyear_value_totalI
            + refyear_value_totalII
            + refyear_value_totalIII
            + refyear_value_totalIV
            + refyear_value_totalV
        ),
        formats_dict["totaux"],
        row,
        col_init,
        signe="-",
    )

    return workbook


def bilan_passif(
    dfdbilan,
    df,
    workbook,
    refbilanyear,
    curbilanyear,
    benefice_total_curyear,
    benefice_total_refyear,
    sheet_name="Bilan passif",
):

    LOGGER.info("Bilan passif")

    # definition des formats
    formats_dict = define_formats(workbook)
    worksheet = workbook.add_worksheet(sheet_name)
    worksheet.freeze_panes(1, 0)

    row = 0
    col = 0
    row_init = 0
    col_init = 0

    # Let us define the width of the columns one time pour toutes
    # worksheet.set_column(0, 0, get_max_len_of_the_descriptions() / 2)
    # col_format = workbook.add_format({"bg_color": "#BCE3F1"})
    worksheet.set_column(0, 0, 40)
    worksheet.set_column(1, 1, 15)
    worksheet.set_column(2, 2, 15)
    worksheet.set_column(3, 3, 20)
    worksheet.set_column(4, 4, 20)

    # ENTETES DE PREMIERE LIGNE
    worksheet.write(row, col, "Bilan passif détaillé")
    col += 1
    cell_format = workbook.add_format({"bold": False, "align": "center"})
    worksheet.write(row, col, f"Année {int(curbilanyear)}", cell_format)
    col += 1
    worksheet.write(row, col, f"Année {int(refbilanyear)}", cell_format)
    col += 1
    worksheet.write(row, col, f"Variation absolue", cell_format)
    col += 1
    worksheet.write(row, col, f"Variation %", cell_format)
    col += 1
    row += 1
    row += 1

    worksheet.write(row, col_init, "Capitaux propres".upper(), formats_dict["bigtitle"])
    row += 1

    id_total_list = []

    ids = ["10"]
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ids,
        row,
        col_init,
        dfdbilan,
        df,
        curbilanyear,
        refbilanyear,
        format=formats_dict["normal"],
        formats_dict=formats_dict,
    )
    id_total_list += ids

    ids = ["11"]
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ids,
        row,
        col_init,
        dfdbilan,
        df,
        curbilanyear,
        refbilanyear,
        format=formats_dict["normal"],
        formats_dict=formats_dict,
    )
    id_total_list += ids

    # Attention pour la ligne Résultats de l'exercice bénéfice ou pertes, je reporte le obtenu dans les soldes intermédiaires de gestion, le bénéfice ou la perte totale
    # du coup, je ne tiens pas compte de 12000
    row, col = add_line_elementary(
        worksheet,
        "Résultat de l'exercice (bénéfice ou perte)",
        benefice_total_curyear,
        benefice_total_refyear,
        formats_dict["normal"],
        row,
        col_init,
    )

    for id in ["13", "14"]:
        row, col = add_macro_categorie_and_detail(
            worksheet,
            [id],
            row,
            col_init,
            dfdbilan,
            df,
            curbilanyear,
            refbilanyear,
            format=formats_dict["normal"],
            formats_dict=formats_dict,
            label=None,
            LOGGER_msg=None,
        )
        id_total_list += [id]

    ###################################

    # Affichage special pour tenir compte de la réintegration du benef
    curyear_value = 0
    refyear_value = 0
    for id in ["10", "11", "13", "14"]:
        curyear_value += calcule_balance_cred_moins_deb(
            dfdbilan[int(curbilanyear)].query(f"idlvl{len(id)} == '{id}'")
        )
        refyear_value += calcule_balance_cred_moins_deb(
            dfdbilan[int(refbilanyear)].query(f"idlvl{len(id)} == '{id}'")
        )

    curyear_value_totalI = curyear_value + benefice_total_curyear
    refyear_value_totalI = refyear_value + benefice_total_refyear

    row, col = add_line_elementary(
        worksheet,
        "TOTAL (I)",
        curyear_value_totalI,
        refyear_value_totalI,
        formats_dict["totaux"],
        row,
        0,
    )

    ######################################

    row += 1

    worksheet.write(
        row, col_init, "Autres fonds propres".upper(), formats_dict["bigtitle"]
    )
    row += 1
    id_total_list = []

    ids = ["167"]
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ids,
        row,
        col_init,
        dfdbilan,
        df,
        curbilanyear,
        refbilanyear,
        format=formats_dict["normal"],
        formats_dict=formats_dict,
        label=None,
        LOGGER_msg=None,
    )
    id_total_list += ids

    row, col, curyear_value_totalIbis, refyear_value_totalIbis = add_line_idlist(
        worksheet,
        id_total_list,
        row,
        col_init,
        dfdbilan,
        df,
        curbilanyear,
        refbilanyear,
        format=formats_dict["totaux"],
        formats_dict=formats_dict,
        label="TOTAL (I bis)",
        signe="-",
    )
    row += 1

    worksheet.write(
        row,
        col_init,
        "Provisions pour risques et charges".upper(),
        formats_dict["bigtitle"],
    )
    row += 1
    id_total_list = []

    ids = ["15"]
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ids,
        row,
        col_init,
        dfdbilan,
        df,
        curbilanyear,
        refbilanyear,
        format=formats_dict["normal"],
        formats_dict=formats_dict,
        label=None,
        LOGGER_msg=None,
    )
    id_total_list += ids

    row, col, curyear_value_totalII, refyear_value_totalII = add_line_idlist(
        worksheet,
        id_total_list,
        row,
        col_init,
        dfdbilan,
        df,
        curbilanyear,
        refbilanyear,
        format=formats_dict["totaux"],
        formats_dict=formats_dict,
        label="TOTAL (II)",
        signe="-",
    )
    row += 1

    worksheet.write(
        row,
        col_init,
        "Emprunts et dettes".upper(),
        formats_dict["bigtitle"],
    )
    row += 1
    id_total_list = []

    ids = [
        "161",
        "162",
        "163",
        "164",
        "167",
        "168",
    ]
    row, col, curyearvalue, refyearvalue = add_line_idlist(
        worksheet,
        ids,
        row,
        col_init,
        dfdbilan,
        df,
        curbilanyear,
        refbilanyear,
        format=formats_dict["normal"],
        formats_dict=formats_dict,
        label="Dettes auprès des établissements de crédit",
    )
    for id in ids:
        row, col = add_macro_categorie_and_detail(
            worksheet,
            [id],
            row,
            col_init,
            dfdbilan,
            df,
            curbilanyear,
            refbilanyear,
            format=formats_dict["normal"],
            formats_dict=formats_dict,
            label=None,
            LOGGER_msg=None,
        )
    id_total_list += ids

    ids = [
        "401",
        "408",
    ]
    row, col, curyearvalue, refyearvalue = add_line_idlist(
        worksheet,
        ids,
        row,
        col_init,
        dfdbilan,
        df,
        curbilanyear,
        refbilanyear,
        format=formats_dict["normal"],
        formats_dict=formats_dict,
        label="Dettes fournisseurs et comptes rattachés",
    )

    for id in ids:
        row, col = add_macro_categorie_and_detail(
            worksheet,
            [id],
            row,
            col_init,
            dfdbilan,
            df,
            curbilanyear,
            refbilanyear,
            format=formats_dict["normal"],
            formats_dict=formats_dict,
            label=None,
            LOGGER_msg=None,
        )
    id_total_list += ids

    row += 1
    ids = [
        "421",
        "424",
        "425",
        "427",
        "428",
        "43",
        "44",
    ]
    row, col, curyearvalue, refyearvalue = add_line_idlist(
        worksheet,
        ids,
        row,
        col_init,
        dfdbilan,
        df,
        curbilanyear,
        refbilanyear,
        format=formats_dict["normal"],
        formats_dict=formats_dict,
        label="Dettes fiscales et sociales",
    )
    for id in ids:
        row, col = add_macro_categorie_and_detail(
            worksheet,
            [id],
            row,
            col_init,
            dfdbilan,
            df,
            curbilanyear,
            refbilanyear,
            format=formats_dict["normal"],
            formats_dict=formats_dict,
            label=None,
            LOGGER_msg=None,
        )
    id_total_list += ids

    # je n'ai pas affiché les instruments de trésorerie, vu avec Antonin

    ids = [
        "487",
        "448",
    ]
    for id in ids:
        row, col = add_macro_categorie_and_detail(
            worksheet,
            [id],
            row,
            col_init,
            dfdbilan,
            df,
            curbilanyear,
            refbilanyear,
            format=formats_dict["normal"],
            formats_dict=formats_dict,
            label=None,
            LOGGER_msg=None,
        )
    id_total_list += ids

    row, col, curyear_value_totalIII, refyear_value_totalIII = add_line_idlist(
        worksheet,
        id_total_list,
        row,
        col_init,
        dfdbilan,
        df,
        curbilanyear,
        refbilanyear,
        format=formats_dict["totaux"],
        formats_dict=formats_dict,
        label="TOTAL (III)",
        # signe="-",
    )
    row += 1

    ids = [
        "487",
    ]
    row, col, curyear_value_totalIV, refyear_value_totalIV = add_line_idlist(
        worksheet,
        ids,
        row,
        col_init,
        dfdbilan,
        df,
        curbilanyear,
        refbilanyear,
        format=formats_dict["normal"],
        formats_dict=formats_dict,
        label="Ecart de conversion passif (IV)",
        signe="-",
    )
    id_total_list += ids

    LOGGER.debug("TOTAL GENERAL (I à IV)")

    row, col = add_line_elementary(
        worksheet,
        "TOTAL GENERAL (I à IV)",
        (
            curyear_value_totalI
            + curyear_value_totalII
            + curyear_value_totalIII
            + curyear_value_totalIV
        ),
        (
            refyear_value_totalI
            + refyear_value_totalII
            + refyear_value_totalIII
            + refyear_value_totalIV
        ),
        formats_dict["totaux"],
        row,
        col_init,
        signe="-",
    )

    return workbook


def display_ligne_simplifie(
    worksheet, row, col, df, query, liste_annees_croissante, format, label, signe="+"
):
    worksheet.write(row, col, label, format)
    col += 1
    ser = pd.Series()
    for year in liste_annees_croissante:
        if signe == "-":
            number = (-1) * calcule_balance_cred_moins_deb(
                df[df.year == year].query(query)
            )
        else:
            number = calcule_balance_cred_moins_deb(df[df.year == year].query(query))
        worksheet.write(
            row,
            col,
            number,
            format,
        )
        col += 1
        ser[year] = number
    return worksheet, row, col, ser


def imprime_ligne_elementary(
    ser,
    worksheet,
    row,
    col,
    label,
    format,
    signe="+",
):
    worksheet.write(row, col, label)
    col += 1
    for val in ser.values:
        if signe == "-":
            val = (-1) * val
        worksheet.write(row, col, val, format)
        col += 1
    return row, col, worksheet, ser


def imprime_bilan_total(
    serlist,
    worksheet,
    row,
    col,
    label,
    format,
    signe="+",
):
    worksheet.write(row, col, label)
    col += 1
    dftmp = pd.concat(serlist, axis=1)
    for val in dftmp.T.sum().values:
        if signe == "-":
            val = (-1) * val
        worksheet.write(row, col, val, format)
        col += 1
    return row, col, worksheet, dftmp.T.sum()


def main(path_list, test=False, refyear=2022, curyear=2023):

    df = extract_df_FEC(path_list)
    global dfdrop
    dfdrop = copy.copy(df)

    xlsx_path = Path(WORK_PATH / "Bilan_detaille.xlsx")

    LOGGER.debug(f"On ouvre le fichier {xlsx_path.resolve()} ! ")

    engine_options = {"nan_inf_to_errors": True}

    if not test:
        writer = pd.ExcelWriter(
            xlsx_path,
            engine="xlsxwriter",
            engine_kwargs={"options": engine_options},
        )
        writer = export_raw_data_by_year(df, writer)
        workbook = writer.book
    else:
        workbook = xlsxwriter.Workbook(xlsx_path, engine_options)

    # je cree un dictionnaire qui va servir de colonnes pour mon excel
    dfd = {y: df[df.year == y] for y in df["year"].drop_duplicates()}
    dfdbilan = {y: df[df.Bilanyear == y] for y in df["Bilanyear"].drop_duplicates()}

    row = 0
    col = 0

    row, col, benefice_total_curyear, benefice_total_refyear = compte_de_resultats(
        dfd, df, workbook, row, col, refyear, curyear
    )
    # workbook = bilan_actif(dfdbilan, df, workbook, refyear, curyear)
    # workbook = bilan_passif(
    #     dfdbilan,
    #     df,
    #     workbook,
    #     refyear,
    #     curyear,
    #     benefice_total_curyear,
    #     benefice_total_refyear,
    # )

    workbook = bilan_simplifiev2(
        df,
        dfdbilan,
        benefice_total_curyear,
        benefice_total_refyear,
        workbook,
        curyear,
        refyear,
    )

    LOGGER.debug(f"On ferme le fichier {xlsx_path.resolve()} ! ")
    if test:
        workbook.close()
    else:
        writer.close()

    LOGGER.info(f"Fichier des écritures comptables {xlsx_path.resolve()}")
    return
