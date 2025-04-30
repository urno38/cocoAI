import re
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from common.convert import beamer_to_pdf
from common.identifiers import (
    NOM_DICT_LVL1,
    NOM_DICT_LVL2,
    NOM_DICT_LVL3,
    NOM_DICT_LVL4,
    get_official_nomenclature,
    load_nomenclature,
)
from common.logconfig import LOGGER
from common.path import (
    COMMERCIAL_DOCUMENTS_PATH,
    TMP_PATH,
    WORK_PATH,
    create_parent_directory,
    rapatrie_file,
)


def inscrire_compte_dans_tmp_fichier(df, tmp_path=TMP_PATH / "used_comptes.csv"):
    create_parent_directory(tmp_path)
    df.to_csv(tmp_path, header=False, index=False, mode="a")
    return


def generer_bilan_excel(fichier_excel):
    # Lire le fichier Excel
    df = pd.read_excel(fichier_excel)

    # Calculer les soldes des comptes
    soldes = df.groupby("compte")[["debit", "credit"]].sum()
    soldes["solde"] = soldes["debit"] - soldes["credit"]

    # Afficher le bilan comptable
    print("Bilan comptable :")
    print("=================")
    for compte, row in soldes.iterrows():
        print(f"Compte {compte}: {row['solde']:.2f}")


def generer_tableau_resultats(fichier_excel):
    # Lire le fichier Excel
    df = pd.read_excel(fichier_excel)

    # Calculer les soldes des comptes
    soldes = df.groupby("Compte")[["Débit", "Crédit"]].sum()
    soldes["Solde"] = soldes["Débit"] - soldes["Crédit"]

    # Réinitialiser l'index pour inclure 'Compte' dans le DataFrame
    soldes = soldes.reset_index()

    # Afficher le tableau de résultats
    print("Tableau de résultats :")
    print(soldes)

    return soldes, df


def is_official_FEC(path):
    if re.match(r"\w{9}FEC\d{8}.txt", path.name):
        LOGGER.debug(path)
        LOGGER.debug("it is an official FEC")
        return True
    else:
        LOGGER.info(path)
        LOGGER.debug("not an official FEC")
        return False


def get_official_end_operation_date(path):
    if is_official_FEC(path):
        date = datetime.strptime(path.name[-12:-4], "%Y%m%d")
    else:
        raise NotImplemented
    return date


def load_txt_data(path_list):
    # ["Compte", "Intitulé", "Date", "Journal"]
    # Compte Date Débit Crédit

    df_list = []
    for p in path_list:
        df = pd.read_csv(p, dtype={"PieceDate": str}, sep="\t")
        df["Compte"] = df["CompteNum"].apply(str)
        df["Débit"] = df["Debit"].apply(lambda x: float(x.replace(",", ".")))
        df["Crédit"] = df["Credit"].apply(lambda x: float(x.replace(",", ".")))
        df["Date"] = df["PieceDate"].apply(
            lambda x: datetime.strptime(str(x).strip(), "%Y%m%d")
        )
        df["Journal"] = df["JournalCode"]
        df["Intitulé"] = df["CompteLib"]
        df.loc[:, "BilanDate"] = get_official_end_operation_date(p)
        df["Bilanyear"] = get_official_end_operation_date(p).year
        df_list.append(df)

    dft = pd.concat(df_list)
    return dft


def load_excel_data(path_list) -> pd.DataFrame:

    df_list = []
    for p in path_list:
        df = pd.read_excel(p, dtype={"Compte": str})
        df["Date"] = df["Date"].apply(lambda x: datetime.strptime(x, "%d/%m/%Y"))
        df["Bilanyear"] = int(p.name.strip().split()[0])
        df_list.append(df)

    dft = pd.concat(df)
    return dft


def calculate_balance_sheet(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule le bilan et retourne un DataFrame."""
    bilan = {
        "Catégorie": ["Actifs", "Passifs", "Capitaux Propres", "Total Bilan"],
        "Montant": [
            df[df["Compte"].str.startswith(("2", "3", "4"))]["Débit"].sum(),
            df[df["Compte"].str.startswith(("1", "5"))]["Crédit"].sum(),
            df[df["Compte"].str.startswith("1")]["Crédit"].sum(),
            df[df["Compte"].str.startswith(("2", "3", "4"))]["Débit"].sum()
            - df[df["Compte"].str.startswith(("1", "5"))]["Crédit"].sum(),
        ],
    }
    return pd.DataFrame(bilan)


def calculate_income_statement(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule le compte de résultat et retourne un DataFrame."""
    compte_resultat = {
        "Catégorie": ["Produits", "Charges", "Résultat Net"],
        "Montant": [
            df[df["Compte"].str.startswith("7")]["Crédit"].sum(),
            df[df["Compte"].str.startswith("6")]["Débit"].sum(),
            df[df["Compte"].str.startswith("7")]["Crédit"].sum()
            - df[df["Compte"].str.startswith("6")]["Débit"].sum(),
        ],
    }
    return pd.DataFrame(compte_resultat)


def calculate_cash_flow_statement(df: pd.DataFrame) -> pd.DataFrame:
    """Calcule le tableau des flux de trésorerie et retourne un DataFrame."""
    flux = {
        "Catégorie": [
            "Flux Opérationnels",
            "Flux Investissements",
            "Flux Financements",
            "Variation de Trésorerie",
        ],
        "Montant": [
            df[df["Compte"].str.startswith(("6", "7"))]["Débit"].sum()
            - df[df["Compte"].str.startswith(("6", "7"))]["Crédit"].sum(),
            df[df["Compte"].str.startswith("2")]["Débit"].sum()
            - df[df["Compte"].str.startswith("2")]["Crédit"].sum(),
            df[df["Compte"].str.startswith(("1", "5"))]["Crédit"].sum()
            - df[df["Compte"].str.startswith(("1", "5"))]["Débit"].sum(),
            (
                df[df["Compte"].str.startswith(("6", "7"))]["Débit"].sum()
                - df[df["Compte"].str.startswith(("6", "7"))]["Crédit"].sum()
            )
            + (
                df[df["Compte"].str.startswith("2")]["Débit"].sum()
                - df[df["Compte"].str.startswith("2")]["Crédit"].sum()
            )
            + (
                df[df["Compte"].str.startswith(("1", "5"))]["Crédit"].sum()
                - df[df["Compte"].str.startswith(("1", "5"))]["Débit"].sum()
            ),
        ],
    }
    return pd.DataFrame(flux)


def generate_beamer_presentation(
    bilan: pd.DataFrame,
    compte_resultat: pd.DataFrame,
    flux_tresorerie: pd.DataFrame,
    output_path: Path,
):
    """Génère une présentation Beamer en LaTeX avec les trois tableaux."""
    latex_template = r"""
\documentclass{beamer}
\usepackage{booktabs}

\begin{document}

\begin{frame}
    \frametitle{Bilan}
    \centering
    \begin{tabular}{lc}
        \toprule
        Catégorie & Montant \\
        \midrule
        %s
        \bottomrule
    \end{tabular}
\end{frame}

\begin{frame}
    \frametitle{Compte de Résultat}
    \centering
    \begin{tabular}{lc}
        \toprule
        Catégorie & Montant \\
        \midrule
        %s
        \bottomrule
    \end{tabular}
\end{frame}

\begin{frame}
    \frametitle{Tableau des Flux de Trésorerie}
    \centering
    \begin{tabular}{lc}
        \toprule
        Catégorie & Montant \\
        \midrule
        %s
        \bottomrule
    \end{tabular}
\end{frame}

\end{document}
    """

    def df_to_latex_rows(df):
        """Convertit un DataFrame en lignes LaTeX."""
        return "\n".join(
            [
                f"{row['Catégorie']} & {row['Montant']:.0f} \\\\"
                for _, row in df.iterrows()
            ]
        )

    bilan_latex = df_to_latex_rows(bilan)
    compte_resultat_latex = df_to_latex_rows(compte_resultat)
    flux_tresorerie_latex = df_to_latex_rows(flux_tresorerie)

    latex_content = latex_template % (
        bilan_latex,
        compte_resultat_latex,
        flux_tresorerie_latex,
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex_content)


def generate_short_summary(excel_path_list):
    beamer_output_path = Path("presentation_beamer.tex")
    df = load_excel_data(excel_path_list)

    bilan_df = calculate_balance_sheet(df)
    compte_resultat_df = calculate_income_statement(df)
    flux_tresorerie_df = calculate_cash_flow_statement(df)

    print(" Bilan :\n", bilan_df)
    print("\n Compte de Résultat :\n", compte_resultat_df)
    print("\n Tableau de Flux de Trésorerie :\n", flux_tresorerie_df)

    generate_beamer_presentation(
        bilan_df, compte_resultat_df, flux_tresorerie_df, beamer_output_path
    )
    beamer_to_pdf(
        beamer_output_path, beamer_output_path.with_suffix(".pdf"), engine="pdflatex"
    )
    print(f"\n Présentation Beamer générée : {beamer_output_path}")
    return


def modify_df_patch(df):
    LOGGER.info("ATTENTION! patch pour le chien qui fume")
    # tous les intitulés de compte commençant par S sont transférés dans le compte 421100
    for compte in df[df.Compte.str.startswith("S")]["Compte"].drop_duplicates():
        df.loc[df.Compte == compte, "Compte"] = "421100"
    # tous les intitulés de compte commençant par 9 sont transférés dans le compte 401000
    for compte in df[df.Compte.str.startswith("9")]["Compte"].drop_duplicates():
        df.loc[df.Compte == compte, "Compte"] = "401000"
    return df


def extract_df_FEC(path_list, patch=False):

    if not isinstance(path_list, list):
        path_list = [path_list]

    path_list = [rapatrie_file(f) for f in path_list]

    if all([p.suffix == ".xlsx" for p in path_list]):
        df = load_excel_data(path_list)
    elif all([is_official_FEC(p) for p in path_list]):
        df = load_txt_data(path_list)
    else:
        raise ValueError("not implemented")

    if patch:
        df = modify_df_patch(df)

    df["Compte"] = df["Compte"].apply(lambda x: str(x).strip())
    df["classe"] = df["Compte"].apply(lambda x: str(x[0]))
    df["idlvl2"] = df["Compte"].apply(lambda x: str(x[:2]))
    df["idlvl3"] = df["Compte"].apply(lambda x: str(x[:3]))
    df["idlvl4"] = df["Compte"].apply(lambda x: str(x[:4]))
    df["idlvl5"] = df["Compte"].apply(lambda x: str(x[:5]))
    df["idlvl6"] = df["Compte"].apply(lambda x: str(x[:6]))
    df["year"] = df["Date"].apply(lambda x: x.year)
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
    df["Crédit_Débit"] = df["Crédit"] - df["Débit"]

    # pour le dispatching quand on présente le crédit et le débit
    df["absCrédit_Débit"] = abs(df["Crédit_Débit"])
    df["Bilan"] = df["Crédit_Débit"].apply(
        lambda x: "ACTIF" if x < 0 else ("PASSIF" if x > 0 else np.nan)
    )

    LOGGER.info(f"Les données comptables ont été chargées avec succès.")
    return df


def export_raw_data_by_year(df, writer):

    LOGGER.info(f"Données brutes")

    export_columns = ["Compte", "Intitulé", "Date", "Journal"]
    sorted_columns = export_columns + [c for c in df.columns if c not in export_columns]

    df[sorted_columns].to_excel(writer, sheet_name="raw data")

    for year in df.year.drop_duplicates():
        dfyear = df[df.year == year]
        dfyear.loc[:, "year"] = year

        dfyear.groupby(["Compte", "Intitulé", "year", "Bilanyear"])[
            ["Débit", "Crédit", "Crédit_Débit"]
        ].sum().to_excel(writer, sheet_name=f"{year} grouped data by compte")

    return writer


def export_FEC_summary(df, output_path):

    xlsx_path = Path(WORK_PATH / "export_sheet.xlsx")

    LOGGER.info(f"On ouvre le fichier {xlsx_path.resolve()} ! ")

    engine_options = {"nan_inf_to_errors": True}

    writer = pd.ExcelWriter(
        xlsx_path,
        engine="xlsxwriter",
        engine_kwargs={"options": engine_options},
    )

    writer = export_raw_data_by_year(df, writer)

    LOGGER.info(f"On ferme le fichier {xlsx_path.resolve()} ! ")

    writer.close()
    return


def add_line_compte(
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
    LOGGER.debug(label if LOGGER_msg is None else LOGGER_msg)

    curyear_value = calcule_balance_cred_moins_deb(
        dfd[int(curyear)].query(f"Compte == '{compte}'")
    )
    refyear_value = calcule_balance_cred_moins_deb(
        dfd[int(refyear)].query(f"Compte == '{compte}'")
    )

    row, col = add_line_elementary(
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


def add_line_elementary(
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
    row += 1
    return row, col


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
        "totaux": workbook.add_format(
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


def calcule_balance_cred_moins_deb(df):
    # pour garder trace de ce qui a été interprété
    inscrire_compte_dans_tmp_fichier(df)
    return df["Crédit"].sum() - df["Débit"].sum()


def add_line_idlist(
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
        LOGGER.debug(
            "je concatene tous les id " + " ".join(idlist)
            if LOGGER_msg is None
            else LOGGER_msg
        )
        if label is None:
            raise ValueError("label must be provided")

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

    row, col = add_line_elementary(
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

    LOGGER.debug(idlist)
    row, col, curyear_value, refyear_value = add_line_idlist(
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

    LOGGER.debug(curyear_value)
    LOGGER.debug(refyear_value)

    for idk in idlist:
        for compte in (
            df[df.Compte.str.startswith(idk)]["Compte"].drop_duplicates().values
        ):
            row, col = add_line_compte(
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


def get_unique_label_in_df(df, identifiant, type="compte"):
    if type == "compte":
        series_du_label = df.query(f"Compte=='{identifiant}'")[
            "Intitulé"
        ].drop_duplicates()
        LOGGER.debug(identifiant)
        LOGGER.debug(series_du_label)
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


def main(excel_path_list, patch=True):
    dfnom = load_nomenclature()
    generate_short_summary(excel_path_list)
    df = extract_df_FEC(excel_path_list, patch=True)
    export_FEC_summary(df, WORK_PATH / "FEC_Summary.xlsx")
    return


def edit_comptes_not_used(path_list):
    dfa = pd.read_csv(
        TMP_PATH / "used_comptes.csv",
        header=None,
    )
    dfa["Compte"] = dfa.iloc[:, 0].apply(lambda x: str(x).strip())

    dfb = extract_df_FEC(path_list)
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


if __name__ == "__main__":

    CHIEN_QUI_FUME_PATH = (
        COMMERCIAL_DOCUMENTS_PATH
        / "2 - DOSSIERS à l'ETUDE"
        / "CHIEN QUI FUME (Le) - 75001 PARIS - 33 Rue du PONT-NEUF"
        / "3. DOCUMENTATION FINANCIÈRE"
    )

    excel_path_list = [
        CHIEN_QUI_FUME_PATH / "2022 - GALLA - GL.xlsx",
        CHIEN_QUI_FUME_PATH / "2023 - GALLA - GL.xlsx",
    ]

    # main(excel_path_list)

    is_official_FEC(
        COMMERCIAL_DOCUMENTS_PATH
        / "1 - DOSSIERS EN COURS DE SIGNATURE"
        / "DEI FRATELLI - 75001 PARIS - 10 Rue des PYRAMIDES"
        / "3. DOCUMENTATION FINANCIÈRE"
        / "839951027FEC20231231.txt"
    )
    is_official_FEC(excel_path_list[0])
