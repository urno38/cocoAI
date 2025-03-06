import copy
from pathlib import Path

import numpy as np
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
from common.path import COMMERCIAL_ONE_DRIVE_PATH, TMP_PATH, WORK_PATH


def bilan_actif(dfd, df, workbook, refyear, curyear, sheet_name="Bilan actif"):

    LOGGER.info("Let us pick up the bilan actif")

    # definition des formats
    formats_dict = define_formats(workbook)

    data = {
        "dfd": dfd,
        "df": df,
        "curyear": curyear,
        "refyear": refyear,
        "format": formats_dict["normal"],
        "formats_dict": formats_dict,
    }  # data qui ne bougeront jamais, pour rendre les signatures plus courtes

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
    worksheet.write(row, col, f"Année {int(curyear)}", cell_format)
    col += 1
    worksheet.write(row, col, f"Année {int(refyear)}", cell_format)
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
            **data,
        )

    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["208", "280"],
        row,
        col_init,
        **data,
        label="Autres immobilisations incorporelles",
    )

    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["237", "238"],
        row,
        col_init,
        **data,
        label="Avances et acomptes sur immobilisations corporelles",
    )

    worksheet.write(row, col_init, "Immobilisation corporelles", formats_dict["bold"])
    row += 1

    for id in ["211", "212", "213", "215", "218", "231"]:
        row, col = add_macro_categorie_and_detail(
            worksheet, [id], row, col_init, **data, signe="-"
        )

    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["2145", "2814"],
        row,
        col_init,
        **data,
        label="Constructions",
        signe="-",
    )

    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["2154", "2815"],
        row,
        col_init,
        **data,
        label="Installations tech. et outillages industriels",
        signe="-",
    )

    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["218", "2818"],
        row,
        col_init,
        **data,
        label="Autres immobilisations corporelles",
        signe="-",
    )

    row, col, curyear_value, refyear_value = add_line_idlist(
        worksheet, ["231"], row, col_init, **data, signe="-"
    )

    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["237", "238"],
        row,
        col_init,
        **data,
        label="Avances et acomptes",
        signe="-",
    )

    worksheet.write(row, col_init, "Immobilisations financières", formats_dict["bold"])
    row += 1
    row, col = add_macro_categorie_and_detail(
        worksheet, ["271"], row, col_init, **data, signe="-"
    )
    row, col = add_macro_categorie_and_detail(
        worksheet, ["272"], row, col_init, **data, signe="-"
    )

    for id in ["266", "267", "273", "274", "275"]:
        row, col = add_macro_categorie_and_detail(
            worksheet,
            [id],
            row,
            col_init,
            **data,
            signe="-",
        )

    idlist = ["2"]
    row, col, curyear_value_totalI, refyear_value_totalI = add_line_idlist(
        worksheet,
        idlist,
        row,
        col_init,
        dfd,
        df,
        curyear,
        refyear,
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
        worksheet, ids, row, col_init, **data, signe="-"
    )
    id_total_list += ids

    # Avances et acomptes versés sur commande
    ids = ["4091"]
    row, col = add_macro_categorie_and_detail(
        worksheet, ids, row, col_init, **data, signe="-"
    )
    id_total_list += ids

    worksheet.write(row, col_init, "Créances", formats_dict["bold"])
    row += 1

    # Clients et comptes rattachés
    ids = ["41"]
    for id in ids:
        row, col = add_macro_categorie_and_detail(
            worksheet, [id], row, col_init, **data, signe="-"
        )
    id_total_list += ids

    # Autres
    ids = ["40", "42", "43", "44", "45", "46", "47", "48", "49"]
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ids,
        row,
        col_init,
        **data,
        label="Autres",
    )
    id_total_list += ids

    # Capital souscrit - appelé non versé
    # source des comptes
    # https://www.compta-online.com/actif-circulant-notion-et-utilisation-ao4349
    ids = ["4562"]
    for id in ids:
        row, col, curyear_value, refyear_value = add_line_idlist(
            worksheet, [id], row, col_init, **data, signe="-"
        )
    id_total_list += ids

    # Valeurs mobilières de placement
    ids = ["506"]
    for id in ids:
        row, col = add_macro_categorie_and_detail(
            worksheet, [id], row, col_init, **data, signe="-"
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
        **data,
        label="Disponibilités",
        signe="-",
    )
    id_total_list += ids

    # Charges constatées d'avance
    ids = ["486"]
    for id in ids:
        row, col, curyear_value, refyear_value = add_line_idlist(
            worksheet, [id], row, col_init, **data, signe="-"
        )
    id_total_list += ids

    row, col, curyear_value_totalII, refyear_value_totalII = add_line_idlist(
        worksheet,
        id_total_list,
        row,
        col_init,
        dfd,
        df,
        curyear,
        refyear,
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
            worksheet, [id], row, col_init, **data, signe="-"
        )
    # id_total_list += ids

    # Prime de remboursement des obligations
    ids = ["169"]
    for id in ids:
        row, col, curyear_value_totalIV, refyear_value_totalIV = add_line_idlist(
            worksheet, [id], row, col_init, **data, signe="-"
        )
    # id_total_list += ids

    # Ecarts de conversion actif
    ids = ["476", "477"]
    row, col, curyear_value_totalV, refyear_value_totalV = add_line_idlist(
        worksheet,
        ids,
        row,
        col_init,
        **data,
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
    dfd,
    df,
    workbook,
    refyear,
    curyear,
    benefice_total_curyear,
    benefice_total_refyear,
    sheet_name="Bilan passif",
):

    LOGGER.info("Let us pick up the bilan passif")

    # definition des formats
    formats_dict = define_formats(workbook)

    data = {
        "dfd": dfd,
        "df": df,
        "curyear": curyear,
        "refyear": refyear,
        "format": formats_dict["normal"],
        "formats_dict": formats_dict,
    }  # data qui ne bougeront jamais, pour rendre les signatures plus courtes

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
    worksheet.write(row, col, f"Année {int(curyear)}", cell_format)
    col += 1
    worksheet.write(row, col, f"Année {int(refyear)}", cell_format)
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
    row, col = add_macro_categorie_and_detail(worksheet, ids, row, col_init, **data)
    id_total_list += ids

    ids = ["11"]
    row, col = add_macro_categorie_and_detail(worksheet, ids, row, col_init, **data)
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
            **data,
        )
        id_total_list += [id]

    ###################################

    # Affichage special pour tenir compte de la réintegration du benef
    curyear_value = 0
    refyear_value = 0
    for id in ["10", "11", "13", "14"]:
        curyear_value += calcule_balance_cred_moins_deb(
            dfd[int(curyear)].query(f"idlvl{len(id)} == '{id}'")
        )
        refyear_value += calcule_balance_cred_moins_deb(
            dfd[int(refyear)].query(f"idlvl{len(id)} == '{id}'")
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
        **data,
    )
    id_total_list += ids

    row, col, curyear_value_totalIbis, refyear_value_totalIbis = add_line_idlist(
        worksheet,
        id_total_list,
        row,
        col_init,
        dfd,
        df,
        curyear,
        refyear,
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
        **data,
    )
    id_total_list += ids

    row, col, curyear_value_totalII, refyear_value_totalII = add_line_idlist(
        worksheet,
        id_total_list,
        row,
        col_init,
        dfd,
        df,
        curyear,
        refyear,
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
        dfd,
        df,
        curyear,
        refyear,
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
            **data,
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
        dfd,
        df,
        curyear,
        refyear,
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
            **data,
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
        dfd,
        df,
        curyear,
        refyear,
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
            **data,
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
            **data,
        )
    id_total_list += ids

    row, col, curyear_value_totalIII, refyear_value_totalIII = add_line_idlist(
        worksheet,
        id_total_list,
        row,
        col_init,
        dfd,
        df,
        curyear,
        refyear,
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
        **data,
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


def main(excel_path_list, test=False):

    df = extract_df_FEC(excel_path_list)

    global dfdrop
    dfdrop = copy.copy(df)

    xlsx_path = Path(WORK_PATH / "Bilan_detaille.xlsx")
    LOGGER.info(f"On ouvre le fichier {xlsx_path.resolve()} ! ")

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

    row = 0
    col = 0

    refyear = 2022
    curyear = 2023
    row, col, benefice_total_curyear, benefice_total_refyear = compte_de_resultats(
        dfd, df, workbook, row, col, refyear, curyear
    )
    workbook = bilan_actif(dfd, df, workbook, refyear, curyear)
    workbook = bilan_passif(
        dfd,
        df,
        workbook,
        refyear,
        curyear,
        benefice_total_curyear,
        benefice_total_refyear,
    )

    workbook = bilan_simplifiev2(
        df, benefice_total_curyear, benefice_total_refyear, workbook
    )

    LOGGER.info(f"On ferme le fichier {xlsx_path.resolve()} ! ")
    if test:
        workbook.close()
    else:
        writer.close()
    return


def edit_comptes_not_used(excel_path_list):
    dfa = pd.read_csv(
        TMP_PATH / "used_comptes.csv",
        header=None,
    )
    dfa["Compte"] = dfa.iloc[:, 0].apply(lambda x: str(x).strip())

    dfb = extract_df_FEC(excel_path_list)
    dfb["Compte"] = dfb["Compte"].apply(lambda x: str(x).strip())

    np.savetxt(
        TMP_PATH / "used_comptes.txt",
        sorted(list(set(dfa["Compte"].values))),
        fmt="%s",
    )
    unique_comptes = set(dfb["Compte"].values).difference(set(dfa["Compte"].values))
    np.savetxt(TMP_PATH / "unique_comptes.txt", sorted(list(unique_comptes)), fmt="%s")
    LOGGER.info(f"Les comptes non utilisés sont dans {TMP_PATH / 'unique_comptes.txt'}")
    return


def bilan_simplifiev1(
    df,
    benefice_total_curyear,
    benefice_total_refyear,
    workbook,
    sheet_name="Bilan simplifié",
):

    # vu avec Antonin, cette implementation n'est plus valable

    # definition des formats
    formats_dict = define_formats(workbook)

    # minyear = df["year"].min()
    # maxyear = df["year"].max()
    liste_annees_croissante = df["year"].drop_duplicates().sort_values()

    worksheet = workbook.add_worksheet(sheet_name)

    # je dilate mes colonnes
    col = 0
    for nbilans in range(2):  # actif et passif
        worksheet.set_column(col, col, 40)
        for ncol in range(len(liste_annees_croissante)):
            col += 1
            worksheet.set_column(col, col, 15)
        col += 1
        worksheet.set_column(col, col, 5)
        col += 1

    row = 0
    col = 0
    worksheet.write(row, col, "BILAN")
    row += 1
    worksheet.write(row, col, "ACTIF")
    col += 1
    for year in liste_annees_croissante:
        worksheet.write(row, col, int(year))
        col += 1

    row += 1
    # col = 0
    worksheet, row, col, ser = display_ligne_simplifie(
        worksheet,
        row,
        0,
        df,
        get_query_from_id_list(["201", "203", "205", "206", "207", "232", "237"]),
        liste_annees_croissante,
        formats_dict["normal"],
        get_official_nomenclature("20"),
        signe="-",
    )
    ser_total = [ser]

    row += 1
    # col = 0
    worksheet, row, col, ser = display_ligne_simplifie(
        worksheet,
        row,
        0,
        df,
        # get_query_from_id_list(["21"]),
        get_query_from_id_list(["211", "212", "213", "2145", "215", "218", "281"]),
        # get_query_from_id_list(["211", "212", "213", "215", "218", "281"]),
        liste_annees_croissante,
        formats_dict["normal"],
        get_official_nomenclature("21"),
        signe="-",
    )
    ser_total += [ser]

    row += 1
    # col = 0
    worksheet, row, col, ser = display_ligne_simplifie(
        worksheet,
        row,
        0,
        df,
        get_query_from_id_list(
            ["261", "266", "267", "271", "272", "273", "274", "275", "276", "277"]
        ),
        liste_annees_croissante,
        formats_dict["normal"],
        "Immobilisations financières",
        signe="-",
    )
    ser_total += [ser]

    # row += 1
    # # col = 0
    # worksheet, row, col, ser = display_ligne_simplifie(
    #     worksheet,
    #     row,
    #     0,
    #     df,
    #     get_query_from_id_list(["280", "281"]),
    #     liste_annees_croissante,
    #     formats_dict["normal"],
    #     "Amortissements",
    #     signe="-",
    # )
    # ser_total += [ser]

    row += 1
    row += 1

    row += 1
    row, col, worksheet, df_actif_net = imprime_bilan_total(
        ser_total,
        worksheet,
        row,
        0,
        "ACTIF NET IMMOBILISE".upper(),
        formats_dict["bold"],
    )
    # )
    # worksheet, row, col, df_actif_net = display_ligne_simplifie(
    #     worksheet,
    #     row,
    #     0,
    #     df,
    #     get_query_from_id_list(["2"]),
    #     liste_annees_croissante,
    #     formats_dict["normal"],
    #     get_official_nomenclature("2"),
    #     # signe="-",
    # )

    #####################################

    ser_total = []
    row += 1
    row += 1
    # col = 0
    worksheet, row, col, ser = display_ligne_simplifie(
        worksheet,
        row,
        0,
        df,
        get_query_from_id_list(["3"]),
        liste_annees_croissante,
        formats_dict["normal"],
        get_official_nomenclature("3"),
        signe="-",
    )
    ser_total += [ser]

    row += 1
    worksheet, row, col, ser = display_ligne_simplifie(
        worksheet,
        row,
        0,
        df,
        get_query_from_id_list(["4091"]),
        liste_annees_croissante,
        formats_dict["normal"],
        get_official_nomenclature("4091"),
        # signe="-",
    )
    ser_total += [ser]

    # row += 1
    # # col = 0
    # worksheet, row, col, ser = display_ligne_simplifie(
    #     worksheet,
    #     row,
    #     0,
    #     df,
    #     get_query_from_id_list(["4562"]),
    #     liste_annees_croissante,
    #     formats_dict["normal"],
    #     get_official_nomenclature("4562"),
    #     signe="-",
    # )
    # ser_total += [ser]

    row += 1
    col = 0
    worksheet, row, col, ser = display_ligne_simplifie(
        worksheet,
        row,
        col,
        df,
        get_query_from_id_list(["411", "413", "416", "417", "418"]),
        liste_annees_croissante,
        formats_dict["normal"],
        # get_official_nomenclature("41"),
        "Créances clients et comptes rattachés",
        # signe="-",
    )
    ser_total += [ser]

    row += 1
    # col = 0
    worksheet, row, col, ser = display_ligne_simplifie(
        worksheet,
        row,
        0,
        df,
        get_query_from_id_list(["40", "42", "44", "45"]),
        liste_annees_croissante,
        formats_dict["normal"],
        "Autres créances",
    )
    ser_total += [ser]

    # row += 1
    # # col = 0
    # worksheet, row, col, ser = display_ligne_simplifie(
    #     worksheet,
    #     row,
    #     0,
    #     df,
    #     get_query_from_id_list(["51", "53", "56", "58"]),
    #     liste_annees_croissante,
    #     formats_dict["normal"],
    #     "Trésorerie",
    #     signe="-",
    # )
    # ser_total += [ser]

    row += 1
    col = 0
    worksheet, row, col, ser = display_ligne_simplifie(
        worksheet,
        row,
        col,
        df,
        get_query_from_id_list(
            ["501", "502", "503", "504", "505", "506", "507", "508"]
        ),
        liste_annees_croissante,
        formats_dict["normal"],
        "Valeurs mobilières de placement",
    )
    ser_total += [ser]

    row += 1
    col = 0
    worksheet, row, col, ser = display_ligne_simplifie(
        worksheet,
        row,
        col,
        df,
        get_query_from_id_list(["51", "53", "58"]),
        liste_annees_croissante,
        formats_dict["normal"],
        "Disponibilités et insruments de trésorerie",
        signe="-",
    )
    ser_total += [ser]

    row += 1
    col = 0
    worksheet, row, col, ser = display_ligne_simplifie(
        worksheet,
        row,
        col,
        df,
        get_query_from_id_list(["486"]),
        liste_annees_croissante,
        formats_dict["normal"],
        get_official_nomenclature("486"),
        signe="-",
    )
    ser_total += [ser]

    row += 1
    row += 1
    row, col, worksheet, df_actif_circulant = imprime_bilan_total(
        ser_total,
        worksheet,
        row,
        0,
        "ACTIF CIRCULANT".upper(),
        formats_dict["bold"],
    )

    row += 1
    col = 0
    worksheet, row, col, ser = display_ligne_simplifie(
        worksheet,
        row,
        col,
        df,
        get_query_from_id_list(["169", "476", "481"]),
        liste_annees_croissante,
        formats_dict["normal"],
        "Comptes de régularisation",
        # signe="-",
    )
    ser_total += [ser]

    row += 1
    row += 1
    # col = 0
    row, col, worksheet, df_total_actif = imprime_bilan_total(
        [df_actif_net, df_actif_circulant],
        worksheet,
        row,
        0,
        "TOTAL ACTIF".upper(),
        formats_dict["totaux"],
    )

    # header
    row = 2
    col = len(liste_annees_croissante) + 2
    worksheet.write(row, col, "PASSIF")
    col += 1

    for year in liste_annees_croissante:
        worksheet.write(row, col, int(year))
        col += 1

    # contenu

    # CAPITAUX PROPRES
    ser_total = []

    row = 2
    col = len(liste_annees_croissante) + 2
    worksheet, row, col, ser = display_ligne_simplifie(
        worksheet,
        row,
        col,
        df,
        get_query_from_id_list(["101"]),
        liste_annees_croissante,
        formats_dict["normal"],
        get_official_nomenclature("101"),
    )
    ser_total += [ser]

    # Report à nouveau
    row += 1
    col = len(liste_annees_croissante) + 2
    worksheet, row, col, ser = display_ligne_simplifie(
        worksheet,
        row,
        col,
        df,
        get_query_from_id_list(["11"]),
        liste_annees_croissante,
        formats_dict["normal"],
        get_official_nomenclature("11"),
    )
    ser_total += [ser]

    row += 1
    col = len(liste_annees_croissante) + 2
    row, col, worksheet, ser = imprime_ligne_elementary(
        pd.Series([benefice_total_refyear, benefice_total_curyear], index=[2022, 2023]),
        worksheet,
        row,
        col,
        "Resultat de l exercice",
        formats_dict["normal"],
        signe="+",
    )
    ser_total += [ser]

    # trop de dettes
    # get_query_from_id_list(
    #         [
    #             "161",
    #             "162",
    #             "163",
    #             "164",
    #             "167",
    #             "168",
    #             "401",
    #             "408",
    #             "421",
    #             "424",
    #             "425",
    #             "427",
    #             "428",
    #             "43",
    #             "44",
    #         ]

    row += 1
    col = len(liste_annees_croissante) + 2
    worksheet, row, col, ser = display_ligne_simplifie(
        worksheet,
        row,
        col,
        df,
        get_query_from_id_list(["13"]),
        liste_annees_croissante,
        formats_dict["normal"],
        get_official_nomenclature("13"),
    )
    ser_total += [ser]

    row += 1
    col = len(liste_annees_croissante) + 2
    worksheet, row, col, ser = display_ligne_simplifie(
        worksheet,
        row,
        col,
        df,
        get_query_from_id_list(["106"]),
        liste_annees_croissante,
        formats_dict["normal"],
        get_official_nomenclature("106"),
    )
    ser_total += [ser]

    row += 1
    col = len(liste_annees_croissante) + 2
    worksheet, row, col, ser = display_ligne_simplifie(
        worksheet,
        row,
        col,
        df,
        get_query_from_id_list(["105", "110", "14"]),
        liste_annees_croissante,
        formats_dict["normal"],
        "Autres capitaux propres",
    )
    ser_total += [ser]

    row += 1
    col = len(liste_annees_croissante) + 2
    worksheet, row, col, ser = display_ligne_simplifie(
        worksheet,
        row,
        col,
        df,
        get_query_from_id_list(["151", "153", "155", "156", "157", "158"]),
        liste_annees_croissante,
        formats_dict["normal"],
        get_official_nomenclature("151"),
    )
    ser_total += [ser]

    row += 1
    row += 1
    col = len(liste_annees_croissante) + 2
    row, col, worksheet, df_ressources_stables = imprime_bilan_total(
        ser_total,
        worksheet,
        row,
        col,
        "Capitaux propres",
        formats_dict["normal"],
    )

    ser_total = []

    row += 1
    row += 1
    col = len(liste_annees_croissante) + 2
    worksheet, row, col, ser = display_ligne_simplifie(
        worksheet,
        row,
        col,
        df,
        get_query_from_id_list(["4191"]),
        liste_annees_croissante,
        formats_dict["normal"],
        get_official_nomenclature("4191"),
    )
    ser_total += [ser]

    # row += 1
    # col = len(liste_annees_croissante) + 2
    # worksheet, row, col, ser = display_ligne_simplifie(
    #     worksheet,
    #     row,
    #     col,
    #     df,
    #     get_query_from_id_list(["41"]),
    #     liste_annees_croissante,
    #     formats_dict["normal"],
    #     get_official_nomenclature("41"),
    # )
    # ser_total += [ser]

    row += 1
    col = len(liste_annees_croissante) + 2
    worksheet, row, col, ser = display_ligne_simplifie(
        worksheet,
        row,
        col,
        df,
        get_query_from_id_list(
            ["401", "403", "408", "421", "422", "424", "427", "431", "437", "442"]
        ),
        liste_annees_croissante,
        formats_dict["normal"],
        "Dettes fournisseurs - comptes rattachés",
    )
    ser_total += [ser]

    # row += 1
    # col = len(liste_annees_croissante) + 2
    # worksheet, row, col, ser = display_ligne_simplifie(
    #     worksheet,
    #     row,
    #     col,
    #     df,
    #     get_query_from_id_list(["42"]),
    #     liste_annees_croissante,
    #     formats_dict["normal"],
    #     get_official_nomenclature("42"),
    # )
    # ser_total += [ser]

    # je ne fais pas apparaitre la trésorerie

    row += 1
    col = len(liste_annees_croissante) + 2
    worksheet, row, col, ser = display_ligne_simplifie(
        worksheet,
        row,
        col,
        df,
        get_query_from_id_list(["43"]),
        liste_annees_croissante,
        formats_dict["normal"],
        get_official_nomenclature("43"),
    )
    ser_total += [ser]

    row += 1
    col = len(liste_annees_croissante) + 2
    worksheet, row, col, ser = display_ligne_simplifie(
        worksheet,
        row,
        col,
        df,
        get_query_from_id_list(["44"]),
        liste_annees_croissante,
        formats_dict["normal"],
        get_official_nomenclature("44"),
    )
    ser_total += [ser]

    row += 1
    col = len(liste_annees_croissante) + 2
    worksheet, row, col, ser = display_ligne_simplifie(
        worksheet,
        row,
        col,
        df,
        get_query_from_id_list(
            ["161", "163", "164", "165", "166", "1675", "168", "17", "426", "519"]
        ),
        liste_annees_croissante,
        formats_dict["normal"],
        "Emprunts et dettes assimilées",
    )
    ser_total += [ser]

    row += 1
    col = len(liste_annees_croissante) + 2
    worksheet, row, col, ser = display_ligne_simplifie(
        worksheet,
        row,
        col,
        df,
        get_query_from_id_list(["487"]),
        liste_annees_croissante,
        formats_dict["normal"],
        get_official_nomenclature("487"),
    )
    ser_total += [ser]

    row += 1
    col = len(liste_annees_croissante) + 2

    # je saute une ligne
    row += 1
    row, col, worksheet, df_passif_circulant = imprime_bilan_total(
        ser_total,
        worksheet,
        row,
        col,
        "PASSIF CIRCULANT".upper(),
        formats_dict["bold"],
    )

    row += 1
    row += 1
    col = len(liste_annees_croissante) + 2
    # col = 0

    row, col, worksheet, df_total_passif = imprime_bilan_total(
        [df_ressources_stables, df_passif_circulant],
        worksheet,
        row,
        col,
        "TOTAL PASSIF".upper(),
        formats_dict["bold"],
    )
    # edit_comptes_not_used(excel_path_list)


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
