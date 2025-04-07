from pathlib import Path

import pandas as pd
import xlsxwriter

from common.FEC import (
    add_line_elementary,
    add_line_idlist,
    add_macro_categorie_and_detail,
    define_formats,
    extract_df_FEC,
)
from common.logconfig import LOGGER
from common.path import COMMERCIAL_DOCUMENTS_PATH, WORK_PATH


def compte_de_resultats(
    dfd, df, workbook, row, col, refyear, curyear, sheet_name="Compte de résultats"
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
    row, col, curyear_value_CA, refyear_value_CA = add_line_idlist(
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
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["781"],
        row,
        col_init,
        **data,
        label="Reprises sur amortissements, dépréciations et provisions, transferts de charges",
    )
    # autres produits
    row, col = add_macro_categorie_and_detail(worksheet, ["75"], row, col_init, **data)
    idlist = ["70", "71", "72", "74", "75", "78", "79"]
    # idlist = ["7"]
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
        ["681"],
        row,
        col_init,
        signe="-",
        **data,
    )
    # row, col = add_macro_categorie_and_detail(
    #     worksheet,
    #     ["6812"],
    #     row,
    #     col_init,
    #     signe="-",
    #     **data,
    # )
    # # Dotations pour dépréciations des immobilisations incorporelles et corporelles
    # row, col = add_macro_categorie_and_detail(
    #     worksheet,
    #     ["6816"],
    #     row,
    #     col_init,
    #     signe="-",
    #     **data,
    # )
    # #  Dotations aux dépréciations des actifs circulants
    # row, col = add_macro_categorie_and_detail(
    #     worksheet,
    #     ["6817"],
    #     row,
    #     col_init,
    #     signe="-",
    #     **data,
    # )
    # # Dotations aux provisions pour risques et charges
    # row, col = add_macro_categorie_and_detail(
    #     worksheet,
    #     ["6865"],
    #     row,
    #     col_init,
    #     signe="-",
    #     **data,
    # )
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
    row, col, curyear_value_totalII, refyear_value_totalII = add_line_idlist(
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
        label="TOTAL (II)",
        signe="-",
    )
    # row += 1

    # Resultats d exploitation (I-II)
    # attention, II est deja negatif

    row, col = add_line_elementary(
        worksheet,
        "RESULTAT D'EXPLOITATION (I-II)",
        curyear_value_totalI + curyear_value_totalII,
        refyear_value_totalI + refyear_value_totalII,
        formats_dict["totaux"],
        row,
        col_init,
        signe="+",
    )
    row += 1

    # Bénéfices attribués ou pertes tranférées
    (
        row,
        col,
        curyear_value_totalIII,
        refyear_value_totalIII,
    ) = add_line_idlist(
        worksheet,
        ["655"],
        row,
        col_init,
        signe="-",
        **data,
        label="Bénéfices attribués ou pertes tranférées (III)",
    )

    # Perte supportée ou bénéfice transféré
    row, col, curyear_value_totalIV, refyear_value_totalIV = add_line_idlist(
        worksheet,
        ["755"],
        row,
        col_init,
        signe="-",
        **data,
        label="Perte supportée ou bénéfice transféré (IV)",
    )

    row += 1

    # Produits financiers
    worksheet.write(row, col_init, "Produits financiers", formats_dict["bold"])
    row += 1
    # Produits financiers de participation
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["761"],
        row,
        col_init,
        **data,
    )
    # Produits autres valeurs mobilières et créances actif immobilisé
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["762", "763", "764"],
        row,
        col_init,
        **data,
        label="Produits autres valeurs mobilières et créances actif immobilisé",
    )
    #  Autres intérêts et produits assimilés
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["768"],
        row,
        col_init,
        **data,
        label="Autres intérêts et produits assimilés",
    )
    #  Autres intérêts et produits assimilés
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["765"],
        row,
        col_init,
        **data,
        label="Autres intérêts et produits assimilés",
    )

    # Différence positives de change
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["766"],
        row,
        col_init,
        **data,
    )
    #  Produits nets sur cessions de valeurs mobilières de placement
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["767"],
        row,
        col_init,
        **data,
    )
    #  Produits nets sur cessions de valeurs mobilières de placement
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["786"],
        row,
        col_init,
        **data,
    )

    # idlist = ["60", "61", "62", "63", "64", "65", "681"]
    row, col, curyear_value_totalV, refyear_value_totalV = add_line_idlist(
        worksheet,
        ["76", "786"],
        row,
        col_init,
        dfd,
        df,
        curyear,
        refyear,
        format=formats_dict["totaux"],
        formats_dict=formats_dict,
        label="TOTAL (V)",
        signe="-",
    )
    row += 1

    # Charges financières
    worksheet.write(row, col_init, "Charges financières", formats_dict["bold"])
    row += 1
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["664", "665"],
        row,
        col_init,
        **data,
        label="Dotations financières aux amortissements, dépréciations et provisions",
        signe="-",
    )
    row, col = add_macro_categorie_and_detail(
        worksheet, ["661"], row, col_init, **data, signe="-"
    )
    row, col = add_macro_categorie_and_detail(
        worksheet, ["666"], row, col_init, **data, signe="-"
    )
    row, col = add_macro_categorie_and_detail(
        worksheet, ["667"], row, col_init, **data, signe="-"
    )
    row, col = add_macro_categorie_and_detail(
        worksheet, ["668"], row, col_init, **data, signe="-"
    )
    row, col = add_macro_categorie_and_detail(
        worksheet, ["686"], row, col_init, **data, signe="-"
    )

    # idlist = ["60", "61", "62", "63", "64", "65", "681"]
    row, col, curyear_value_totalVI, refyear_value_totalVI = add_line_idlist(
        worksheet,
        ["66", "686"],
        row,
        col_init,
        dfd,
        df,
        curyear,
        refyear,
        format=formats_dict["totaux"],
        formats_dict=formats_dict,
        label="TOTAL (VI)",
        signe="-",
    )
    row += 1

    row, col = add_line_elementary(
        worksheet,
        "RESULTAT FINANCIER (V-VI)",
        curyear_value_totalV + curyear_value_totalVI,
        refyear_value_totalV + refyear_value_totalVI,
        formats_dict["totaux"],
        row,
        col_init,
        signe="+",
    )

    row, col = add_line_elementary(
        worksheet,
        "RESULTAT COURANT AVANT IMPOTS (I-II+III-IV+V-VI)",
        curyear_value_totalI
        + curyear_value_totalII
        + curyear_value_totalIII
        + curyear_value_totalIV
        + curyear_value_totalV
        + curyear_value_totalVI,
        refyear_value_totalI
        + refyear_value_totalII
        + refyear_value_totalIII
        + refyear_value_totalIV
        + refyear_value_totalV
        + refyear_value_totalVI,
        formats_dict["totaux"],
        row,
        col_init,
        signe="+",
    )

    row += 1
    # Produits exceptionnels
    worksheet.write(row, col_init, "Produits exceptionnels", formats_dict["bold"])
    LOGGER.debug("Produits exceptionnels")
    row += 1
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["771"],
        row,
        col_init,
        **data,
    )
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["772"],
        row,
        col_init,
        **data,
    )
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["774", "775", "777", "778"],
        row,
        col_init,
        **data,
        label="Produits exceptionnels sur opérations en capital",
    )
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["787"],
        row,
        col_init,
        **data,
    )

    row, col, curyear_value_totalVII, refyear_value_totalVII = add_line_idlist(
        worksheet,
        ["77", "787"],
        row,
        col_init,
        dfd,
        df,
        curyear,
        refyear,
        format=formats_dict["totaux"],
        formats_dict=formats_dict,
        label="TOTAL (VII)",
        signe="-",
    )
    row += 1

    # Charges exceptionnelles
    worksheet.write(row, col_init, "Charges exceptionnelles", formats_dict["bold"])
    row += 1
    LOGGER.debug("Charges exceptionnelles")
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["671"],
        row,
        col_init,
        **data,
        signe="-",
    )
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["672"],
        row,
        col_init,
        **data,
        signe="-",
    )
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["674", "675", "677", "678"],
        row,
        col_init,
        **data,
        label="Charges exceptionnelles sur opérations en capital",
        signe="-",
    )
    row, col = add_macro_categorie_and_detail(
        worksheet,
        ["687"],
        row,
        col_init,
        **data,
        signe="-",
    )
    row, col, curyear_value_totalVIII, refyear_value_totalVIII = add_line_idlist(
        worksheet,
        ["67", "687"],
        row,
        col_init,
        dfd,
        df,
        curyear,
        refyear,
        format=formats_dict["totaux"],
        formats_dict=formats_dict,
        label="TOTAL (VIII)",
        signe="-",
    )

    row, col = add_line_elementary(
        worksheet,
        "RESULTAT EXCEPTIONNEL (VII-VIII)",
        curyear_value_totalVII + curyear_value_totalVIII,
        refyear_value_totalVII + refyear_value_totalVIII,
        formats_dict["totaux"],
        row,
        col_init,
        signe="+",
    )

    row, col, curyear_value_totalIX, refyear_value_totalIX = add_line_idlist(
        worksheet,
        ["691"],
        row,
        col_init,
        dfd,
        df,
        curyear,
        refyear,
        format=formats_dict["totaux"],
        formats_dict=formats_dict,
        # signe="-",
    )

    row, col, curyear_value_totalX, refyear_value_totalX = add_line_idlist(
        worksheet,
        ["695"],
        row,
        col_init,
        dfd,
        df,
        curyear,
        refyear,
        format=formats_dict["totaux"],
        formats_dict=formats_dict,
        # signe="-",
    )

    LOGGER.debug("TOTAL DES PRODUITS")
    row, col = add_line_elementary(
        worksheet,
        "TOTAL DES PRODUITS",
        curyear_value_totalI
        + curyear_value_totalIII
        + curyear_value_totalV
        + curyear_value_totalVII,
        refyear_value_totalI
        + refyear_value_totalIII
        + refyear_value_totalV
        + refyear_value_totalVII,
        formats_dict["totaux"],
        row,
        col_init,
        signe="+",
    )

    LOGGER.debug("TOTAL DES CHARGES")
    row, col = add_line_elementary(
        worksheet,
        "TOTAL DES CHARGES",
        curyear_value_totalII
        + curyear_value_totalIV
        + curyear_value_totalVI
        + curyear_value_totalVIII
        + curyear_value_totalIX
        + curyear_value_totalX,
        refyear_value_totalII
        + refyear_value_totalIV
        + refyear_value_totalVI
        + refyear_value_totalVIII
        + refyear_value_totalIX
        + refyear_value_totalX,
        formats_dict["totaux"],
        row,
        col_init,
        signe="-",
    )

    LOGGER.debug("BENEFICE OU PERTES = (TOTAL DES PRODUITS - TOTAL DES CHARGES)")

    benefice_curyear = (
        curyear_value_totalI
        + curyear_value_totalIII
        + curyear_value_totalV
        + curyear_value_totalVII
    ) + (
        curyear_value_totalII
        + curyear_value_totalIV
        + curyear_value_totalVI
        + curyear_value_totalVIII
        + curyear_value_totalIX
        + curyear_value_totalX
    )

    benefice_refyear = (
        refyear_value_totalI
        + refyear_value_totalIII
        + refyear_value_totalV
        + refyear_value_totalVII
    ) + (
        refyear_value_totalII
        + refyear_value_totalIV
        + refyear_value_totalVI
        + refyear_value_totalVIII
        + refyear_value_totalIX
        + refyear_value_totalX
    )

    row, col = add_line_elementary(
        worksheet,
        "BENEFICE OU PERTES = (TOTAL DES PRODUITS - TOTAL DES CHARGES)",
        benefice_curyear,
        benefice_refyear,
        formats_dict["totaux"],
        row,
        col_init,
    )

    return row, col, benefice_curyear, benefice_refyear


def main(path_list, test=False, curyear=2022, refyear=2021):

    df = extract_df_FEC(path_list, patch=False)

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
            COMMERCIAL_DOCUMENTS_PATH
            / "2 - DOSSIERS à l'ETUDE"
            / "1 - FONDS DE COMMERCES"
            / "CHIEN QUI FUME (Le) - 75001 PARIS - 33 Rue du PONT-NEUF"
            / "3. DOCUMENTATION FINANCIÈRE"
            / "2022 - GALLA - GL.xlsx"
        ),
        (
            COMMERCIAL_DOCUMENTS_PATH
            / "2 - DOSSIERS à l'ETUDE"
            / "1 - FONDS DE COMMERCES"
            / "CHIEN QUI FUME (Le) - 75001 PARIS - 33 Rue du PONT-NEUF"
            / "3. DOCUMENTATION FINANCIÈRE"
            / "2023 - GALLA - GL.xlsx"
        ),
    ]

    main(excel_path_list, test=True)
