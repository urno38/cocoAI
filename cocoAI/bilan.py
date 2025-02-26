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
from common.path import COMMERCIAL_ONE_DRIVE_PATH, WORK_PATH, rapatrie_file


def calcule_balance_cred_moins_deb(df):
    return df["Crédit"].sum() - df["Débit"].sum()


def define_formats(workbook):
    formats_dict = {
        "bigtitle": workbook.add_format(
            {"bold": True, "text_wrap": True, "num_format": "#,##0.00"}
        ),
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
                "text_wrap": True,
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


def add_line_bilan_elementary(
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
    row += 1
    return row, col


def add_line_compte_bilan(
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
    row, col = add_line_bilan_elementary(
        worksheet,
        f"    {label}",
        curyear_value,
        refyear_value,
        formats_dict["compte"],
        beginning_row,
        beginning_col,
        signe=signe,
    )
    return row, col


def add_line_idlist_bilan(
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
    else:
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

    row, col = add_line_bilan_elementary(
        worksheet,
        "  " + label,
        curyear_value,
        refyear_value,
        format,
        beginning_row,
        beginning_col,
        signe=signe,
    )
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

    row, col, curyear_value, refyear_value = add_line_idlist_bilan(
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
        label=label,
        signe=signe,
    )

    for idk in idlist:
        for compte in (
            df[df.Compte.str.startswith(idk)]["Compte"].drop_duplicates().values
        ):
            row, col = add_line_compte_bilan(
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


def bilan_de_comptes_annuels(
    dfd, df, workbook, row, col, refyear, curyear, sheet_name="CR"
):
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
    worksheet.write(row, col, "Bilan de comptes de résultats")
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
    worksheet.write(row, col_init, "Actif immobilisé".upper(), formats_dict["bigtitle"])
    row += 1

    worksheet.write(row, col_init, "Immobilisation incorporelles", formats_dict["bold"])
    row += 1
    row, col, curyear_value, refyear_value = add_line_idlist_bilan(
        worksheet, ["201"], row, col_init, **data, signe="-"
    )
    row, col, curyear_value, refyear_value = add_line_idlist_bilan(
        worksheet, ["203"], row, col_init, **data, signe="-"
    )
    row, col, curyear_value, refyear_value = add_line_idlist_bilan(
        worksheet, ["205"], row, col_init, **data, signe="-"
    )
    row, col, curyear_value, refyear_value = add_line_idlist_bilan(
        worksheet, ["206"], row, col_init, **data, signe="-"
    )
    row, col, curyear_value, refyear_value = add_line_idlist_bilan(
        worksheet, ["207"], row, col_init, **data, signe="-"
    )
    row, col, curyear_value, refyear_value = add_line_idlist_bilan(
        worksheet, ["208"], row, col_init, **data, signe="-"
    )

    worksheet.write(row, col_init, "Immobilisation corporelles", formats_dict["bold"])
    row += 1
    row, col, curyear_value, refyear_value = add_line_idlist_bilan(
        worksheet, ["211"], row, col_init, **data, signe="-"
    )
    row, col, curyear_value, refyear_value = add_line_idlist_bilan(
        worksheet, ["212"], row, col_init, **data, signe="-"
    )
    row, col, curyear_value, refyear_value = add_line_idlist_bilan(
        worksheet, ["213"], row, col_init, **data, signe="-"
    )
    row, col, curyear_value, refyear_value = add_line_idlist_bilan(
        worksheet, ["215"], row, col_init, **data, signe="-"
    )
    row, col, curyear_value, refyear_value = add_line_idlist_bilan(
        worksheet, ["218"], row, col_init, **data, signe="-"
    )

    # TODO A CONTINUER A PARTIR DE CA

    #     Un bilan d'actifs comptable présente les actifs détenus par une entreprise à une date donnée. Ces actifs sont généralement classés en deux grandes catégories : les actifs immobilisés (ou non courants) et les actifs circulants (ou courants). Voici les principaux comptes que l'on retrouve dans un bilan d'actifs comptable, en suivant le Plan Comptable Général (PCG) français :

    # ### 1. **Actifs Immobilisés (Non Courants)**
    # Ces actifs sont destinés à être utilisés de manière durable par l'entreprise.

    # - **Immobilisations incorporelles (Compte 20)**
    # - Frais d'établissement (201)
    # - Frais de recherche et développement (203)
    # - Concessions, brevets, licences, marques, droits et valeurs similaires (205)
    # - Fonds commercial (206)
    # - Autres immobilisations incorporelles (208)

    # - **Immobilisations corporelles (Compte 21)**
    # - Terrains (211)
    # - Constructions (212)
    # - Installations techniques, matériel et outillage industriels (213)
    # - Matériel de transport (215)
    # - Mobilier, matériel de bureau et informatique (218)

    # - **Immobilisations financières (Compte 27)**
    # - Participations (271)
    # - Créances rattachées à des participations (272)
    # - Autres créances immobilisées (275)

    # ### 2. **Actifs Circulants (Courants)**
    # Ces actifs sont destinés à être utilisés ou vendus dans le cadre du cycle d'exploitation normal de l'entreprise.

    # - **Stocks et en-cours (Compte 3)**
    # - Matières premières et fournitures (31)
    # - En-cours de production de biens (32)
    # - En-cours de production de services (33)
    # - Produits intermédiaires et finis (34)
    # - Marchandises (35)

    # - **Créances (Compte 4)**
    # - Clients (411)
    # - Autres créances (418)
    # - Sécurité sociale et autres organismes sociaux (431)
    # - État - Subventions à recevoir (441)
    # - État - Créances fiscales et assimilées (444)
    # - Personnel - Avances et acomptes (462)
    # - Débiteurs divers et créditeurs divers (467)

    # - **Placements financiers et disponibilités (Compte 5)**
    # - Valeurs mobilières de placement (VMP) (50)
    # - Banques (512)
    # - Instruments de trésorerie (52)
    # - Caisse (53)

    # ### Exemple de Présentation du Bilan Actif

    # | **Catégorie**                  | **Compte** | **Montant** |
    # |--------------------------------|------------|-------------|
    # | **Actifs Immobilisés**         |            |             |
    # | Immobilisations incorporelles  | 20         | 50 000 €    |
    # | Immobilisations corporelles    | 21         | 150 000 €   |
    # | Immobilisations financières    | 27         | 30 000 €    |
    # | **Total des immobilisations**  |            | 230 000 €   |
    # | **Actifs Circulants**          |            |             |
    # | Stocks et en-cours             | 3          | 40 000 €    |
    # | Créances                       | 4          | 60 000 €    |
    # | Placements financiers          | 50         | 20 000 €    |
    # | Disponibilités                 | 512, 53    | 10 000 €    |
    # | **Total des actifs circulants**|            | 130 000 €   |
    # | **Total de l'actif**           |            | 360 000 €   |

    # En suivant cette structure, vous pouvez établir un bilan d'actifs comptable qui reflète fidèlement la situation financière de votre entreprise à une date donnée.

    return row, col


def main(excel_path_list, test=False):

    excel_path_list = [rapatrie_file(f) for f in excel_path_list]
    df = extract_df_for_CR(excel_path_list)
    xlsx_path = Path(WORK_PATH / "Bilan_detaille.xlsx")
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

    sheet_name = "Bilan des comptes annuels"
    refyear = 2022
    curyear = 2023
    LOGGER.info("Let us pick up the bilan de comptes annuel")
    row, col = bilan_de_comptes_annuels(
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
