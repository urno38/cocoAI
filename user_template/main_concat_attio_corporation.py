import re
from datetime import datetime
from locale import LC_TIME, setlocale

import numpy as np
import pandas as pd

from common.path import DATALAKE_PATH

df = pd.concat(
    [
        pd.read_csv(f, index_col=0)
        for f in list(DATALAKE_PATH.rglob("ATTIO_FILES/corporation.csv"))
    ]
)


def modify_activity(activity):
    if isinstance(activity, str):
        if "brasserie" in activity.lower():
            return "Brasserie"
        elif "restaurant" in activity.lower() or "restauration" in activity.lower():
            return "Restaurant"
        elif "pizzeria" in activity.lower():
            return "Pizzeria"
        elif "bar" in activity.lower() or "limonadier" in activity.lower():
            return "Limonade"
        else:
            return activity
    else:
        if pd.isnull(activity):
            return "Brasserie"
        else:
            return activity


# def modify_red(x):
#     if isinstance(x, Number):
#         if np.isnan(x):
#             return np.nan
#         else:
#             return str(float(x)) + " €"
#     else:
#         new_x = x.replace("euros", "€")
#         new_x = x.replace("€HT", "€ HT")
#         new_x = re.sub(r"HT HT", "HT", x)
#         new_x = x.replace('"', "")
#         return new_x


def entier_avec_espaces_francais(n):
    if n < 1000:
        return str(n)
    else:
        # Utiliser la division et le modulo pour séparer les milliers
        quotient, reste = divmod(n, 1000)
        # Appel récursif pour le quotient et concaténation avec le reste
        return entier_avec_espaces_francais(quotient) + " " + f"{reste:03d}"


def remplacer_caracteres(chaine):
    nouvelle_chaine = []
    for i in range(len(chaine)):
        if chaine[i] == ",":
            # Vérifie si la virgule est placée avant le point
            if "." in chaine[i:]:
                nouvelle_chaine.append(" ")
            else:
                nouvelle_chaine.append("")
        elif chaine[i] == ".":
            # Vérifie si le point est placé avant la virgule
            if "," in chaine[i:]:
                nouvelle_chaine.append(" ")
            else:
                nouvelle_chaine.append("")
        else:
            nouvelle_chaine.append(chaine[i])
    return "".join(nouvelle_chaine)


def transform_to_formatted_date(date_str):
    date_str = date_str.replace("décembre", "12")
    try:
        # Définir le locale en français pour interpréter les noms de mois en français
        setlocale(LC_TIME, "fr_FR.UTF-8")
    except:
        # Si le locale 'fr_FR.UTF-8' n'est pas disponible, essayer 'fr_FR'
        setlocale(LC_TIME, "fr_FR")

    # Liste des formats d'entrée possibles
    input_date_formats = ["%d %B %Y", "%d %m %Y", "%d.%m.%Y", "%Y-%m-%d"]
    convert = False
    for date_format in input_date_formats:
        try:
            # Convertir la chaîne en objet date
            date_obj = datetime.strptime(date_str, date_format).date()
            convert = True
            break
        except ValueError:
            # print(date_str)
            # return date_str
            continue
    if not convert:
        print(date_str)
        return date_str

    # Définir le format de sortie
    output_date_format = "%d/%m/%Y"

    # Formater l'objet date en chaîne selon le format de sortie
    formatted_date_str = date_obj.strftime(output_date_format)

    return formatted_date_str


def modify_red(x):
    print(x)
    if isinstance(x, float) and np.isnan(x):
        return x

    if "FF" in str(x):
        return np.nan
    new_x = str(x).replace("€", "")

    # cas des virgules et des points
    if "." in new_x and "," not in new_x:
        new_x = new_x.replace(".", "")
    if "," in new_x and "." not in new_x:
        new_x = new_x.replace(",", "")
    # coder qui est en premier et modifier en consequence
    if "," in new_x and "." in new_x:
        new_x = remplacer_caracteres(new_x)

    # new_x = str(x).replace(".", "")
    new_x = new_x.replace("HT", "")
    new_x = re.sub(" +", "", new_x)
    new_x = new_x.replace("(ouTTC?)", "")
    new_x = new_x.replace("euros", "")
    new_x = new_x.replace("F", "")
    print(new_x)
    return entier_avec_espaces_francais(int(new_x))


wdir = DATALAKE_PATH / "ATTIO_workdir"
wdir.mkdir(exist_ok=True)
df.to_csv(wdir / "corporation_global_raw.csv")

# je mets en forme rapidement pour que ça soit plus lisible dans attio
df["Nom de la société"] = df["Nom de la société"].apply(lambda x: x.replace("_", " "))
df["Activité exercée"] = df["Activité exercée"].apply(lambda x: modify_activity(x))
df["Redevance de gérance"] = df["Redevance de gérance"].apply(lambda x: modify_red(x))
df["Date de renouvellement - Location gérance"] = df[
    "Date de renouvellement - Location gérance"
].apply(lambda x: transform_to_formatted_date(str(x)))

# TODO coder la masse salariale


wdir = DATALAKE_PATH / "ATTIO_workdir"
wdir.mkdir(exist_ok=True)

df.to_csv(wdir / "corporation_global.csv")
print(wdir / "corporation_global.csv")
