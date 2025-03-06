import copy
from pathlib import Path

import numpy as np
import pandas as pd
import xlsxwriter

from cocoAI.compte_de_resultats import compte_de_resultats
from common.FEC import define_formats, export_raw_data_by_year, extract_df_FEC
from common.identifiers import get_official_nomenclature, get_query_from_id_list
from common.logconfig import LOGGER
from common.path import COMMERCIAL_ONE_DRIVE_PATH, WORK_PATH


def get_dfyear(df, year):

    # dfyear = df[df.year == year]
    # dfyear.loc[:, "year"] = year

    dfyear = pd.DataFrame(
        df.query(f"year == {year}")
        .groupby(["Compte"])["Crédit_Débit"]
        .sum()
        .reset_index()
    )

    dfyear["classe"] = dfyear["Compte"].apply(lambda x: str(x[0]))
    dfyear["idlvl2"] = dfyear["Compte"].apply(lambda x: str(x[:2]))
    dfyear["idlvl3"] = dfyear["Compte"].apply(lambda x: str(x[:3]))
    dfyear["idlvl4"] = dfyear["Compte"].apply(lambda x: str(x[:4]))
    dfyear["idlvl5"] = dfyear["Compte"].apply(lambda x: str(x[:5]))

    # pour le dispatching quand on présente le crédit et le débit
    dfyear["absCrédit_Débit"] = abs(dfyear["Crédit_Débit"])
    dfyear["Bilan"] = dfyear["Crédit_Débit"].apply(
        lambda x: "ACTIF" if x < 0 else ("PASSIF" if x > 0 else np.nan)
    )

    return dfyear


def imprime_ligne_simplifie(
    label,
    query,
    dfd,
    row_init,
    col_init,
    worksheet,
    format=None,
    additional_series=None,
    raw_value=False,
):

    row = row_init
    col = col_init

    worksheet.write(
        row,
        col,
        label,
        format,
    )

    ser = pd.Series()

    for year in sorted(list(set(dfd.keys())), reverse=True):
        if query is None:
            df_filtered = dfd[year]
        else:
            df_filtered = dfd[year].query(query)

        col += 1
        # je fais la valeur absolue et j'ajoute eventuellement une additional series
        if raw_value:
            # pour prendre en compte le report a nouveau qui est algebrique
            value = df_filtered["Crédit_Débit"].sum()
        else:
            value = abs(df_filtered["Crédit_Débit"].sum())

        if additional_series is not None:
            value += additional_series[year]

        worksheet.write(
            row,
            col,
            value,
            format,
        )

        ser[year] = value

    row += 1

    return row, col, worksheet, ser


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


def imprime_ligne_bilan(
    label,
    id_list,
    row,
    col,
    ws,
    dfd_grouped,
    Bilan=None,
    format=None,
    additional_series=None,
    raw_value=False,
):

    filter = False
    if id_list != []:
        filter = True

    if filter:
        # definition de la query pour filtrer le df
        if Bilan is None:
            query = get_query_from_id_list(id_list)
        else:
            if isinstance(Bilan, str):
                # si je ne splitte pas les residus positifs et negatifs
                query = (
                    "(" + get_query_from_id_list(id_list) + f") and Bilan=='{Bilan}'"
                )
            elif isinstance(Bilan, list) and len(Bilan) == len(id_list):
                query_list = []
                for i, bil in enumerate(Bilan):
                    if bil is not None:
                        query_list.append(
                            get_query_from_id_list([id_list[i]])
                            + f" and Bilan=='{bil}'"
                        )
                    else:
                        LOGGER.debug("bil")
                        LOGGER.debug(bil)
                        LOGGER.debug(query_list)
                        LOGGER.debug(id_list)
                        query_list.append(get_query_from_id_list([id_list[i]]))
                query = "(" + (") or (").join(query_list) + ")"
                LOGGER.debug(label)
                LOGGER.debug(query)
            else:
                raise ValueError
    else:
        query = None

    row, col, ws, ser = imprime_ligne_simplifie(
        label,
        query,
        dfd_grouped,
        row,
        col,
        ws,
        format,
        additional_series,
        raw_value,
    )

    return row, col, ws, ser

    # edit_comptes_not_used(excel_path_list)


def bilan_simplifiev2(
    df,
    benefice_total_curyear,
    benefice_total_refyear,
    workbook,
    sheet_name="Bilan simplifié",
):
    # on change d'approche : pour chacune des lignes de comptes, je determine si le bilan est positif ou negatif et ensuite je range dans le bilan si le bilan est positif ou negatif

    dfd_grouped = {y: get_dfyear(df, y) for y in df["year"].drop_duplicates()}
    # definition des formats
    formats_dict = define_formats(workbook)
    liste_annees_croissante = list(df["year"].drop_duplicates().sort_values().values)
    liste_annees_decroissante = list(
        df["year"].drop_duplicates().sort_values(ascending=False).values
    )
    ws = workbook.add_worksheet(sheet_name)

    # MISE EN PAGE
    # je dilate mes colonnes
    ws.write(0, 0, "BILAN")
    col = 0
    for ibilan in range(2):  # actif et passif
        if ibilan == 0:
            ws.write(1, col, "ACTIF")
        if ibilan == 1:
            ws.write(1, col, "PASSIF")
        ws.set_column(col, col, 40)
        for ncol in range(len(liste_annees_decroissante)):
            col += 1
            ws.write(1, col, liste_annees_decroissante[ncol])
            ws.set_column(col, col, 15)
        col += 1
        ws.set_column(col, col, 5)
        col += 1

    row = 2
    col = 0
    # creation de la matrice de tableau
    # 4 blocs dans lesquels on met des lignes de comptes

    ########################
    # ACTIF
    ########################
    # actif : 3 blocs

    # actif immobilisé
    # definition du bloc actif immobilise

    row, col, ws, ser = imprime_ligne_bilan(
        "Immobilisations incorporelles",
        ["201", "203", "205", "206", "207", "232", "237"],
        row,
        0,
        ws,
        dfd_grouped,
    )

    row, col, ws, ser = imprime_ligne_bilan(
        "Immobilisations corporelles",
        ["211", "212", "213", "2145", "215", "218", "281"],
        row,
        0,
        ws,
        dfd_grouped,
    )

    row, col, ws, ser = imprime_ligne_bilan(
        "Immobilisations financières",
        ["261", "266", "267", "271", "272", "273", "274", "275", "276", "277"],
        row,
        0,
        ws,
        dfd_grouped,
    )

    row += 1
    row, col, ws, ser = imprime_ligne_bilan(
        "ACTIF NET IMMOBILISE",
        ["201", "203", "205", "206", "207", "232", "237"]
        + ["211", "212", "213", "2145", "215", "218", "281"]
        + ["261", "266", "267", "271", "272", "273", "274", "275", "276", "277"],
        row,
        0,
        ws,
        dfd_grouped,
        Bilan=None,
        format=formats_dict["bold"],
    )
    row += 1

    row += 1
    row += 1
    row += 1

    # actif circulant

    row, col, ws, ser = imprime_ligne_bilan(
        get_official_nomenclature("3"),
        ["3"],
        row,
        0,
        ws,
        dfd_grouped,
        Bilan="ACTIF",
        # format=formats_dict["bold"],
    )

    row, col, ws, ser = imprime_ligne_bilan(
        get_official_nomenclature("4091"),
        ["4091"],
        row,
        0,
        ws,
        dfd_grouped,
        Bilan="ACTIF",
        # format=formats_dict["bold"],
    )

    row, col, ws, ser = imprime_ligne_bilan(
        "Créances clients et comptes rattachés",
        ["411", "413", "416", "417", "418"],
        row,
        0,
        ws,
        dfd_grouped,
        Bilan="ACTIF",
        # format=formats_dict["bold"],
    )

    row, col, ws, ser = imprime_ligne_bilan(
        "Autres créances",
        ["40", "42", "44", "45"],
        row,
        0,
        ws,
        dfd_grouped,
        Bilan="ACTIF",
        # format=formats_dict["bold"],
    )

    row, col, ws, ser = imprime_ligne_bilan(
        "Valeurs mobilières de placement",
        ["501", "502", "503", "504", "505", "506", "507", "508"],
        row,
        0,
        ws,
        dfd_grouped,
        Bilan="ACTIF",
        # format=formats_dict["bold"],
    )

    row, col, ws, ser = imprime_ligne_bilan(
        "Disponibilités et insruments de trésorerie",
        ["51", "53", "58"],
        row,
        0,
        ws,
        dfd_grouped,
        Bilan="ACTIF",
        # format=formats_dict["bold"],
    )

    row, col, ws, ser = imprime_ligne_bilan(
        "Charges constatées d'avance",
        ["486"],
        row,
        0,
        ws,
        dfd_grouped,
        Bilan="ACTIF",
        # format=formats_dict["bold"],
    )

    row, col, ws, ser = imprime_ligne_bilan(
        "ACTIF CIRCULANT",
        ["3"]
        + ["4091"]
        + ["411", "413", "416", "417", "418"]
        + ["40", "42", "44", "45"]
        + ["501", "502", "503", "504", "505", "506", "507", "508"]
        + ["51", "53", "58"]
        + ["486"],
        row,
        0,
        ws,
        dfd_grouped,
        Bilan="ACTIF",
        format=formats_dict["totaux"],
    )

    # compte de regularisation

    row, col, ws, ser = imprime_ligne_bilan(
        "Comptes de régularisation",
        ["169", "476", "481"],
        row,
        0,
        ws,
        dfd_grouped,
        Bilan="ACTIF",
        # format=formats_dict["bold"],
    )

    # POUR LE BILAN ACTIF TOTAL
    id_list_immob = (
        ["201", "203", "205", "206", "207", "232", "237"]
        + ["211", "212", "213", "2145", "215", "218", "281"]
        + ["261", "266", "267", "271", "272", "273", "274", "275", "276", "277"]
    )
    id_list = id_list_immob
    Bilan_list = [None] * len(id_list_immob)

    id_list_circulant = (
        ["3"]
        + ["4091"]
        + ["411", "413", "416", "417", "418"]
        + ["40", "42", "44", "45"]
        + ["501", "502", "503", "504", "505", "506", "507", "508"]
        + ["51", "53", "58"]
        + ["486"]
    )
    id_list += id_list_circulant
    Bilan_list += ["ACTIF"] * len(id_list_circulant)

    row, col, ws, ser = imprime_ligne_bilan(
        "TOTAL ACTIF",
        id_list,
        row,
        0,
        ws,
        dfd_grouped,
        Bilan=Bilan_list,
        format=formats_dict["totaux"],
    )

    ########################
    # PASSIF
    ########################

    # Capitaux propres : passif
    row = 2

    row, col, ws, ser = imprime_ligne_bilan(
        "Capital",
        ["101"],
        row,
        len(liste_annees_decroissante) + 2,
        ws,
        dfd_grouped,
        Bilan="PASSIF",
        # format=formats_dict["bold"],
    )

    row, col, ws, ser_report = imprime_ligne_bilan(
        "Report à nouveau",
        ["11"],
        row,
        len(liste_annees_decroissante) + 2,
        ws,
        dfd_grouped,
        Bilan=None,
        # format=formats_dict["bold"],
        raw_value=True,
    )

    row, col, ws, ser_resultat_exercice = imprime_ligne_elementary(
        pd.Series(
            [benefice_total_curyear, benefice_total_refyear],
            index=liste_annees_decroissante,
        ),
        ws,
        row,
        len(liste_annees_decroissante) + 2,
        "Resultat de l exercice",
        formats_dict["normal"],
    )
    row += 1

    row, col, ws, ser = imprime_ligne_bilan(
        "Subventions d'investissement",
        ["13"],
        row,
        len(liste_annees_decroissante) + 2,
        ws,
        dfd_grouped,
        Bilan="PASSIF",
    )

    row, col, ws, ser = imprime_ligne_bilan(
        "Réserves",
        ["106"],
        row,
        len(liste_annees_decroissante) + 2,
        ws,
        dfd_grouped,
        Bilan="PASSIF",
    )

    row, col, ws, ser = imprime_ligne_bilan(
        "Autres capitaux propres",
        ["105", "110", "14"],
        row,
        len(liste_annees_decroissante) + 2,
        ws,
        dfd_grouped,
        Bilan="PASSIF",
    )

    row, col, ws, ser = imprime_ligne_bilan(
        "Provisions pour risques",
        ["151", "153", "155", "156", "157", "158"],
        row,
        len(liste_annees_decroissante) + 2,
        ws,
        dfd_grouped,
        Bilan="PASSIF",
    )

    row += 1
    row, col, ws, ser_capitaux_propres = imprime_ligne_bilan(
        "Capitaux propres".upper(),
        ["101"]
        + ["13"]
        + ["106"]
        + ["105", "110", "14"]
        + ["151", "153", "155", "156", "157", "158"],
        row,
        len(liste_annees_decroissante) + 2,
        ws,
        dfd_grouped,
        Bilan="PASSIF",
        format=formats_dict["totaux"],
        additional_series=ser_report + ser_resultat_exercice,
    )
    row += 1

    # Passif circulant

    row, col, ws, ser = imprime_ligne_bilan(
        "Clients - Avances et acomptes reçus sur commandes",
        ["4191"],
        row,
        len(liste_annees_decroissante) + 2,
        ws,
        dfd_grouped,
        Bilan="PASSIF",
    )

    row, col, ws, ser = imprime_ligne_bilan(
        "Dettes fournisseurs - comptes rattachés",
        # ["401", "403", "408", "421", "422", "424", "427", "431", "437", "442"],
        ["401", "408"],
        row,
        len(liste_annees_decroissante) + 2,
        ws,
        dfd_grouped,
        Bilan=None,
    )

    # Changement de découpage pour fitter au bilan in extenso
    row, col, ws, ser = imprime_ligne_bilan(
        "Dettes fiscales et sociales",
        [
            "421",
            "424",
            "425",
            "427",
            "428",
            "43",
            "44",
        ],
        row,
        len(liste_annees_decroissante) + 2,
        ws,
        dfd_grouped,
        Bilan=None,
    )

    # row, col, ws, ser = imprime_ligne_bilan(
    #     "Sécurité sociale et autres organismes sociaux",
    #     ["43"],
    #     row,
    #     len(liste_annees_decroissante) + 2,
    #     ws,
    #     dfd_grouped,
    #     Bilan=None,
    # )

    # row, col, ws, ser = imprime_ligne_bilan(
    #     "État et autres collectivités publiques",
    #     ["44"],
    #     row,
    #     len(liste_annees_decroissante) + 2,
    #     ws,
    #     dfd_grouped,
    #     Bilan=None,
    # )

    row, col, ws, ser = imprime_ligne_bilan(
        "Emprunts et dettes assimilées",
        ["161", "163", "164", "165", "166", "1675", "168", "17", "426", "519"],
        row,
        len(liste_annees_decroissante) + 2,
        ws,
        dfd_grouped,
        Bilan="PASSIF",
    )

    row, col, ws, ser = imprime_ligne_bilan(
        "Produits constatés d'avance",
        ["487"],
        row,
        len(liste_annees_decroissante) + 2,
        ws,
        dfd_grouped,
        Bilan="PASSIF",
    )

    # Total circulant
    row += 1
    row, col, ws, ser_passif_circulant = imprime_ligne_bilan(
        "Passif Circulant".upper(),
        ["4191"]
        + ["401", "408"]
        + [
            "421",
            "424",
            "425",
            "427",
            "428",
            "43",
            "44",
        ]
        + ["161", "163", "164", "165", "166", "1675", "168", "17", "426", "519"]
        + ["487"],
        row,
        len(liste_annees_decroissante) + 2,
        ws,
        dfd_grouped,
        Bilan=None,
        format=formats_dict["bold"],
        # additional_series=ser_capitaux_propres,
    )
    row += 1

    row, col, ws, ser = imprime_ligne_bilan(
        "total passif".upper(),
        [],
        row,
        len(liste_annees_decroissante) + 2,
        ws,
        dfd_grouped,
        Bilan="PASSIF",
        additional_series=ser_passif_circulant + ser_capitaux_propres,
        format=formats_dict["totaux"],
    )

    return workbook


def main(excel_path_list, test=False):

    df = extract_df_FEC(excel_path_list)

    global dfdrop
    dfdrop = copy.copy(df)

    xlsx_path = Path(WORK_PATH / "Bilan_detaillev2.xlsx")
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

    workbook = bilan_simplifiev2(
        df, benefice_total_curyear, benefice_total_refyear, workbook
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

    # df = extract_df_FEC(excel_path_list)
    # dfyear = get_dfyear(df, 2022)
