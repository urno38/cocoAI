from pathlib import Path

import pandas as pd

from common.convert import convert_beamer_to_pdf, load_yaml_to_dict
from common.path import COMMON_PATH, DATA_PATH


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


def load_excel_data(path_list) -> pd.DataFrame:
    """Charge les données comptables depuis un fichier Excel."""
    df = pd.concat([pd.read_excel(p, dtype={"Compte": str}) for p in path_list])
    return df


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


def load_nomenclature(yaml_path=COMMON_PATH / "nomenclature.yaml"):
    df_list = []
    di = load_yaml_to_dict(yaml_path)
    for k, dict in di.items():
        df_list.append(
            pd.DataFrame(
                {"Classe": str(k), "description": dict["description"]}, index=[k]
            )
        )
        if dict["subcategories"]:
            for kk, dictt in dict["subcategories"].items():
                df_list.append(
                    pd.DataFrame(
                        {
                            "Classe": str(k),
                            "niveau1": str(kk),
                            "description": dictt["description"],
                        },
                        index=[kk],
                    )
                )
                if "subcategories" in dictt.keys():
                    for kkk, dicttt in dictt["subcategories"].items():
                        df_list.append(
                            pd.DataFrame(
                                {
                                    "Classe": str(k),
                                    "niveau1": str(kk),
                                    "niveau2": str(kkk),
                                    "description": dicttt["description"],
                                },
                                index=[kkk],
                            )
                        )
    df = pd.concat(df_list, ignore_index=True)
    return df


def main(excel_path_list):
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
    convert_beamer_to_pdf(
        beamer_output_path, beamer_output_path.with_suffix(".pdf"), engine="pdflatex"
    )
    print(f"\n Présentation Beamer générée : {beamer_output_path}")
    return


if __name__ == "__main__":
    # excel_path_list = list(DATA_PATH.glob("202*xls*"))[:2]
    # main(excel_path_list)

    df = load_nomenclature()
    print(df)
