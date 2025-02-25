from datetime import datetime
from pathlib import Path

import pandas as pd
import xlsxwriter

from cocoAI.FEC import load_excel_data
from common.identifiers import (
    NOM_DICT_LVL1,
    NOM_DICT_LVL2,
    NOM_DICT_LVL3,
    NOM_DICT_LVL4,
    get_official_nomenclature,
)
from common.logconfig import LOGGER
from common.path import DATA_PATH, WORK_PATH


def calcule_balance_cred_moins_deb(df):
    # pour rendre le code compact
    return df["Crédit"].sum() - df["Débit"].sum()


def define_formats(workbook):

    formats_dict = {
        "title": workbook.add_format(
            {"bold": False, "text_wrap": True, "num_format": "#,##0.00"}
        ),
        "bold": workbook.add_format({"bold": True, "num_format": "#,##0.00"}),
        "normal": workbook.add_format({"bold": False, "num_format": "#,##0.00"}),
        "compte": workbook.add_format(
            {"bold": False, "num_format": "#,##0.00", "font_size": 9, "italic": True}
        ),
        "totals": workbook.add_format(
            {
                "bold": True,
                "font_color": "blue",
                "num_format": "#,##0.00",
                # "bottom": 2,
                # "top": 2,
            }
        ),
        "row_intercalaire": workbook.add_format(
            {
                "bold": False,
                "num_format": "#,##0.00",
            }
        ),
    }
    return formats_dict


def get_unique_label_in_df(df, identifiant, type="compte"):

    if type == "compte":
        series_du_label = df.query(f"Compte=='{identifiant}'")[
            "Intitulé"
        ].drop_duplicates()
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


def add_line_CR(
    worksheet,
    txt,
    curvalue,
    refvalue,
    format,
    beginning_row,
    beginning_col,
    signe="+",
):

    # print(worksheet, txt, curvalue, refvalue, format, beginning_row, beginning_col)

    if signe not in ["+", "-", ""]:
        raise ValueError("not implemented")
    if signe == "-":
        refvalue = (-1) * refvalue
        curvalue = (-1) * curvalue

    row = beginning_row
    col = beginning_col

    # worksheet.write(row, col, signe + txt, format)
    worksheet.write(row, col, txt, format)  # no sign
    col += 1

    format.set_bg_color("#BCE3F1")  # curyear value
    if curvalue != 0:
        format.set_align("right")
        worksheet.write_number(row, col, curvalue, format)
    else:
        format.set_align("right")
        worksheet.write(row, col, "-", format)
        format.set_align("left")
    col += 1

    format.set_bg_color("#BCE3F1")  # refyear value
    if refvalue != 0:
        format.set_align("right")
        worksheet.write_number(row, col, refvalue, format)
    else:
        format.set_align("right")
        worksheet.write(row, col, "-", format)
        format.set_align("left")
    col += 1
    format.set_bg_color("#FFFFFF")  # blanc

    if curvalue != 0 and refvalue != 0:
        format.set_align("right")
        worksheet.write_number(row, col, float(curvalue) - float(refvalue), format)
    col += 1
    if refvalue != 0 and curvalue != 0:
        format.set_align("right")
        worksheet.write_number(
            row, col, (float(curvalue) / float(refvalue) - 1) * 100, format
        )
    else:
        format.set_align("right")
        worksheet.write(row, col, "-", format)
        format.set_align("left")
        # pass
    return row, col


def add_line_lvl2_CR(
    worksheet,
    idlvl2,
    beginning_row,
    beginning_col,
    dfd,
    df,
    curyear,
    refyear,
    format=None,
    LOGGER_msg=None,
    signe="+",
):

    LOGGER.info(NOM_DICT_LVL2 if LOGGER_msg is None else LOGGER_msg)

    curyear_value = calcule_balance_cred_moins_deb(
        dfd[int(curyear)].query(f"idlvl2 == '{idlvl2}'")
    )
    refyear_value = calcule_balance_cred_moins_deb(
        dfd[int(refyear)].query(f"idlvl2 == '{idlvl2}'")
    )

    row, col = add_line_CR(
        worksheet,
        NOM_DICT_LVL2[idlvl2],
        curyear_value,
        refyear_value,
        format,
        beginning_row,
        beginning_col,
        signe=signe,
    )
    row += 1
    return row, col


def add_line_lvl3_CR(
    worksheet,
    idlvl3,
    beginning_row,
    beginning_col,
    dfd,
    df,
    curyear,
    refyear,
    format=None,
    formats_dict=None,
    LOGGER_msg=None,
    signe="+",
):

    LOGGER.info(NOM_DICT_LVL3[idlvl3] if LOGGER_msg is None else LOGGER_msg)

    curyear_value = calcule_balance_cred_moins_deb(
        dfd[int(curyear)].query(f"idlvl3 == '{idlvl3}'")
    )
    refyear_value = calcule_balance_cred_moins_deb(
        dfd[int(refyear)].query(f"idlvl3 == '{idlvl3}'")
    )

    row, col = add_line_CR(
        worksheet,
        NOM_DICT_LVL3[idlvl3],
        curyear_value,
        refyear_value,
        format,
        beginning_row,
        beginning_col,
        signe=signe,
    )
    row += 1
    return row, col


def add_line_lvl4_CR(
    worksheet,
    idlvl4,
    beginning_row,
    beginning_col,
    dfd,
    df,
    curyear,
    refyear,
    format=None,
    formats_dict=None,
    LOGGER_msg=None,
    signe="+",
):

    LOGGER.info(NOM_DICT_LVL4[idlvl4] if LOGGER_msg is None else LOGGER_msg)

    curyear_value = calcule_balance_cred_moins_deb(
        dfd[int(curyear)].query(f"idlvl4 == '{idlvl4}'")
    )
    refyear_value = calcule_balance_cred_moins_deb(
        dfd[int(refyear)].query(f"idlvl4 == '{idlvl4}'")
    )

    row, col = add_line_CR(
        worksheet,
        NOM_DICT_LVL4[idlvl4],
        curyear_value,
        refyear_value,
        format,
        beginning_row,
        beginning_col,
        signe=signe,
    )
    row += 1
    return row, col


def add_line_compte_CR(
    worksheet,
    compte,
    beginning_row,
    beginning_col,
    dfd,
    df,
    curyear,
    refyear,
    format=None,
    formats_dict=None,
    LOGGER_msg=None,
    signe="+",
):

    label = f"{compte} {get_unique_label_in_df(df,compte)}"
    LOGGER.info(label if LOGGER_msg is None else LOGGER_msg)

    curyear_value = calcule_balance_cred_moins_deb(
        dfd[int(curyear)].query(f"Compte == '{compte}'")
    )
    refyear_value = calcule_balance_cred_moins_deb(
        dfd[int(refyear)].query(f"Compte == '{compte}'")
    )
    # print(signe)
    row, col = add_line_CR(
        worksheet,
        f"    {label}",
        curyear_value,
        refyear_value,
        formats_dict["compte"],
        beginning_row,
        beginning_col,
        signe=signe,
    )
    row += 1
    return row, col


def add_line_idlist_CR(
    worksheet,
    idlist,
    beginning_row,
    beginning_col,
    dfd,
    df,
    curyear,
    refyear,
    format=None,
    formats_dict=None,
    label=None,
    LOGGER_msg=None,
    signe="+",
):

    LOGGER.info(
        "je concatene tous les id " + " ".join(idlist)
        if LOGGER_msg is None
        else LOGGER_msg
    )

    curyear_value = 0
    refyear_value = 0
    for id in idlist:
        if len(id) == 1:
            curyear_value += calcule_balance_cred_moins_deb(
                dfd[int(curyear)].query(f"classe == '{id}'")
            )
            refyear_value += calcule_balance_cred_moins_deb(
                dfd[int(refyear)].query(f"classe == '{id}'")
            )
        else:
            curyear_value += calcule_balance_cred_moins_deb(
                dfd[int(curyear)].query(f"idlvl{len(id)} == '{id}'")
            )
            refyear_value += calcule_balance_cred_moins_deb(
                dfd[int(refyear)].query(f"idlvl{len(id)} == '{id}'")
            )

    row, col = add_line_CR(
        worksheet,
        label,
        curyear_value,
        refyear_value,
        format,
        beginning_row,
        beginning_col,
        signe=signe,
    )
    row += 1
    return row, col, curyear_value, refyear_value


def add_macro_categorie_and_detail(
    worksheet,
    idlist,
    beginning_row,
    beginning_col,
    dfd,
    df,
    curyear,
    refyear,
    format=None,
    formats_dict=None,
    label=None,
    LOGGER_msg=None,
    signe="+",
):

    if len(idlist) == 1 and label is None:
        label = get_official_nomenclature(idlist[0])

    row, col, curyear_value, refyear_value = add_line_idlist_CR(
        worksheet,
        idlist,
        beginning_row,
        beginning_col,
        dfd,
        df,
        curyear,
        refyear,
        format=formats_dict["title"],
        formats_dict=formats_dict,
        label="  " + label,
        signe=signe,
    )

    for idk in idlist:
        for compte in (
            df[df.Compte.str.startswith(idk)]["Compte"].drop_duplicates().values
        ):
            row, col = add_line_compte_CR(
                worksheet,
                compte,
                row,
                beginning_col,
                dfd,
                df,
                curyear,
                refyear,
                formats_dict["normal"],
                formats_dict=formats_dict,
                signe=signe,
            )

    return row, col


def extract_df_for_CR(excel_path_list):
    df = load_excel_data(excel_path_list)
    df["classe"] = df["Compte"].apply(lambda x: str(x[0]))
    df["idlvl2"] = df["Compte"].apply(lambda x: str(x[:2]))
    df["idlvl3"] = df["Compte"].apply(lambda x: str(x[:3]))
    df["idlvl4"] = df["Compte"].apply(lambda x: str(x[:4]))
    df["idlvl5"] = df["Compte"].apply(lambda x: str(x[:5]))
    df["idlvl6"] = df["Compte"].apply(lambda x: str(x[:6]))
    df["year"] = df["Date"].apply(lambda x: datetime.strptime(x, "%d/%M/%Y").year)
    df["descriptionclasse"] = df["classe"].apply(
        lambda x: NOM_DICT_LVL1[x] if x in NOM_DICT_LVL1.keys() else None
    )
    df["descriptionlvl2"] = df["idlvl2"].apply(
        lambda x: NOM_DICT_LVL2[x] if x in NOM_DICT_LVL2.keys() else None
    )
    df["descriptionlvl3"] = df["idlvl3"].apply(
        lambda x: NOM_DICT_LVL3[x] if x in NOM_DICT_LVL3.keys() else None
    )
    df["descriptionlvl4"] = df["idlvl4"].apply(
        lambda x: NOM_DICT_LVL4[x] if x in NOM_DICT_LVL4.keys() else None
    )
    return df


def compte_de_resultats(dfd, df, workbook, row, col, refyear, curyear, sheet_name="CR"):
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

    row_init = row
    col_init = col

    # Let us define the width of the columns one time pour toutes
    # worksheet.set_column(0, 0, get_max_len_of_the_descriptions() / 2)
    # col_format = workbook.add_format({"bg_color": "#BCE3F1"})
    worksheet.set_column(0, 0, 40)
    worksheet.set_column(1, 1, 15)
    worksheet.set_column(2, 2, 15)
    worksheet.set_column(3, 3, 20)
    worksheet.set_column(4, 4, 20)

    # ENTETES DE PREMIERE LIGNE
    worksheet.write(row, col, "Compte de résultats détaillés")
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

    # Produits d'exploitation
    worksheet.write(row, col_init, "Produits d'exploitation", formats_dict["bold"])
    row += 1
    # Ventes de marchandises
    row, col = add_macro_categorie_and_detail(worksheet, ["707"], row, col_init, **data)
    # Production vendue biens
    row, col = add_macro_categorie_and_detail(worksheet, ["701"], row, col_init, **data)
    # Production vendue services
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["706", "708"],
        row,
        col_init,
        **data,
        label="Production vendue services",
    )
    idlist = ["70"]
    row, col, curyear_value_CA, refyear_value_CA = add_line_idlist_CR(
        worksheet,
        idlist,
        row,
        col_init,
        dfd,
        df,
        curyear,
        refyear,
        format=formats_dict["totals"],
        formats_dict=formats_dict,
        label="Chiffres d'affaires net",
    )
    row += 1

    # TOTAL I
    # Production stockée
    row, col = add_macro_categorie_and_detail(worksheet, ["71"], row, col_init, **data)
    # Production immobilisée
    row, col = add_macro_categorie_and_detail(worksheet, ["72"], row, col_init, **data)
    # subventions d exploitation recues
    row, col = add_macro_categorie_and_detail(worksheet, ["74"], row, col_init, **data)
    # subventions d exploitation recues
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["78", "79"],
        row,
        col_init,
        **data,
        label="Reprises sur amortissements, dépréciations et provisions, transferts de charges",
    )
    # autres produits
    row, col = add_macro_categorie_and_detail(worksheet, ["75"], row, col_init, **data)
    idlist = ["70", "71", "72", "74", "75", "78", "79"]
    # idlist = ["7"]
    row, col, curyear_value_totalI, refyear_value_totalI = add_line_idlist_CR(
        worksheet,
        idlist,
        row,
        col_init,
        dfd,
        df,
        curyear,
        refyear,
        format=formats_dict["totals"],
        formats_dict=formats_dict,
        label="TOTAL (I)",
    )
    row += 1

    # Charges d'exploitation
    worksheet.write(row, col_init, "Charges d'exploitation", formats_dict["bold"])
    row += 1
    # Achats de marchandises
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["6037"],
        row,
        col_init,
        **data,
        signe="-",
    )
    # Achats de marchandises
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["607"],
        row,
        col_init,
        **data,
        signe="-",
    )
    # Variation de stock
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["603"],
        row,
        col_init,
        **data,
        signe="-",
    )
    # Achats de matières premières et autres approvisionnements
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["601"],
        row,
        col_init,
        **data,
        label="Achats de matières premières et autres approvisionnements",
        signe="-",
    )
    # Autres achats et charges externes
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["602", "604", "605", "606", "608", "609", "61", "62"],
        row,
        col_init,
        **data,
        label="Autres achats et charges externes",
        signe="-",
    )
    row += 1

    # Impots, taxes et versements assimiles
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["63"],
        row,
        col_init,
        signe="-",
        **data,
    )
    # Salaires et traitements
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["641", "644"],
        row,
        col_init,
        label="Salaires et traitements",
        signe="-",
        **data,
    )
    # Charges sociales
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["645", "646", "647", "648"],
        row,
        col_init,
        label="Charges sociales",
        signe="-",
        **data,
    )
    # Autres charges de gestions courantes
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["65"],
        row,
        col_init,
        # label="Charges sociales",
        signe="-",
        **data,
    )
    # Charges exceptionnelles
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["67"],
        row,
        col_init,
        # label="Charges sociales",
        signe="-",
        **data,
    )
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["6811"],
        row,
        col_init,
        signe="-",
        **data,
    )
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["6812"],
        row,
        col_init,
        signe="-",
        **data,
    )
    # Dotations pour dépréciations des immobilisations incorporelles et corporelles
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["6816"],
        row,
        col_init,
        signe="-",
        **data,
    )
    #  Dotations aux dépréciations des actifs circulants
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["6817"],
        row,
        col_init,
        signe="-",
        **data,
    )
    # Dotations aux provisions pour risques et charges
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["6865"],
        row,
        col_init,
        signe="-",
        **data,
    )
    # Autres charges
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["65"],
        row,
        col_init,
        signe="-",
        **data,
    )
    idlist = ["60", "61", "62", "63", "64", "65", "681"]
    row, col, curyear_value_totalII, refyear_value_totalII = add_line_idlist_CR(
        worksheet,
        idlist,
        row,
        col_init,
        dfd,
        df,
        curyear,
        refyear,
        format=formats_dict["totals"],
        formats_dict=formats_dict,
        label="TOTAL (II)",
        signe="-",
    )
    row += 1

    return row, col


def main(excel_path_list, test=False):
    df = extract_df_for_CR(excel_path_list)
    xlsx_path = Path(WORK_PATH / "Compte_de_resultats_detailles.xlsx")
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

    sheet_name = "CR"
    refyear = 2022
    curyear = 2023
    LOGGER.info("Let us pick up the CR")
    row, col = compte_de_resultats(dfd, df, workbook, row, col, refyear, curyear, "CR")

    LOGGER.info(f"On ferme le fichier {xlsx_path.resolve()} ! ")
    if test:
        workbook.close()
    else:
        writer.close()
    return


if __name__ == "__main__":
    main(excel_path_list=list(DATA_PATH.glob("202*GL*xls*"))[:2], test=False)
