import json
import random
from pathlib import Path

import pandas as pd
import pyperclip

from cocoAI.company import get_infos_from_a_siren
from common.logconfig import LOGGER
from common.path import WORK_PATH

# df2 = pd.read_excel(Path(r"C:\Users\lvolat\Documents\cocoAI\common\bdd_SIRET.xlsx"))


# for e, s in df2.reset_index()[["ENSEIGNE", "SIRET"]].dropna().iterrows():
#     print(s["ENSEIGNE"], s["SIRET"])
#     if s["SIRET"] != "Non trouvé":
#         get_infos_from_a_siren(str(s["SIRET"])[:-5])


# di = {
#     "CASA DI MARIO - 75007 PARIS - 132 Rue du BAC": "53119288800018",
#     "BROOKLYN CAFE - 75017 PARIS - 32 Place Saint FERDINAND": "Informations non disponibles",
#     "CAFE DU MEXIQUE - 75016 PARIS - 3 Place de MEXICO": "Informations non disponibles",
#     "CHEZ BEBER  - 75006 PARIS - 71 Bld du MONTPARNASSE": "42507282400011",
#     "CHIEN QUI FUME (Le) - 75001 PARIS - 33 Rue du PONT-NEUF": "31013032300015",
#     "CIAL - 75001 PARIS - rue Mondétour - 16": "Informations non disponibles",
#     "DEI FRATELLI - 75001 PARIS - 10 Rue des PYRAMIDES": "83995102700011",
#     "GENTLEMEN - JARDINS DE L'ARCHE - 92000 NANTERRE": "80449572900035",
#     "GRAND CARNOT (Le) - 75017 PARIS - 32 Avenue CARNOT angle 40 Rue des ACACIAS": "79895243800017",
#     "MANHATTAN TERRAZZA - 108 Av de VILLIERS - 75017 PARIS": "88096301200014",
#     "RALLYE PASSY (BOUILLON PASSY) - 75016 PARIS - 34 Rue de l'ANNONCIATION": "48747486800022",
#     "AFFRANCHIS (Les) - 75012 PARIS - 14 Avenue DAUMESNIL": "84492436500027",
#     "ANDORINHA - 75016 PARIS - 199 Avenue de VERSAILLES - ex VERSAILLES AVENUE - MONTCASTEL": "79903742900014",
#     "AQUABIKE - 75015 PARIS - 45 Avenue de la MOTTE-PICQUET": "43776601700010",
#     "ASCENSION - 75018 - 62 RUE CUSTINE": "79854416900016",
#     "ASIAN KITCHEN - 75007 PARIS - 49 Quai d'ORSAY - 20240925": "42507282400011",
#     "ASSOCIES (Les) - 75012 PARIS - 50 Bld de la BASTILLE": "43472611300013",
#     "AVELLINO - 4 Bld Richard WALLACE - 92800 PUTEAUX": "53862111100013",
#     "AZZURO - 92100 BOULOGNE-BILLANCOURT - 59 Place René CLAIR": "38027351600019",
#     "BAIGNEUSES (Les) - 64200 BIARRITZ - 14 Rue du PORT VIEUX": "40101719900014",
#     "BAR DES SPORT - 75012 - 73 AVENUE DU GENERAL MICHEL BIZOT": "82268394200012",
#     "BARIOLÉ (Le) - 75020 PARIS - 103 Rue de BELLEVILLE": "53792611300013",
#     "BEBER - 75006 PARIS - 71 Bld du MONTPARNASSE": "42507282400011",
#     "BILLY BILLI - 92000 NANTERRE": "89324339400010",
#     "BISTROT BALNÉAIRE (Le) - 40150 SOORTS-HOSSEGOR - 1830 Avenue du TOURING CLUB": "48903161700014",
#     "BISTROT CHARBON (Le) - 75004 PARIS- 131 rue Saint MARTIN": "53739192200013",
#     "BISTROT DE RUNGIS - DEFICIT REPORTABLE": "43792187700043",
#     "BISTROT DU FAUBOURG - 12 Allée de l'ARCHE - 92400 COURBEVOIE": "81531506400023",
#     "BOIS LE VENT (Le) - 75016 PARIS - 59 Rue de BOULAINVILLIERS": "38098071400014",
#     "BON JACQUES (Le) - 75017 - 34 Rue Jouffroy d'ABBANS": "90834751100013",
#     "BOUDOIR (Le) - 75006 PARIS - 202 Bld Saint GERMAIN": "84072367000013",
#     "BOULANGERIE DE L'OLYMPIA": "34027633600014",
#     "BOULEDOGUE (Le) - 75003 PARIS - 20 Rue RAMBUTEAU": "40327792400011",
#     "BRASSERIE LOLA - MURS ET FONDS - 75015 PARIS - 99 rue du THÉÂTRE": "83488996600015",
#     "BRIOCHE DORÉE - 78 Av des CHAMPS ELYSÉES - 75008 PARIS": "31890659100014",
#     "CAFÉ DE L'ÉGLISE - 92110 CLICHY - 100 Bld Jean JAURÈS": "83226626600015",
#     "CANTINA - 75016 - CLAUDE TERRASSE - 16": "48057007600020",
#     "COMPAGNIE (La) - 75017 PARIS - 123 Av de WAGRAM": "Informations non disponibles",
#     "DA ROSA - 75001 PARIS - 7 Rue ROUGET de l'ISLE": "Informations non disponibles",
#     "DIPLOMATE (Le)- 75016 - CLAUDE TERRASSE - 16": "Informations non disponibles",
#     "DODDY'S - 75017 PARIS - 80 Rue Mstislav ROSTROPOVITCH": "Informations non disponibles",
#     "EL SOL - 75008 - 22 RUE DE PONTHIEU": "Informations non disponibles",
#     "FAJITAS - 75006 PARIS - 15 Rue DAUPHINE": "Informations non disponibles",
#     "GERMAIN - 94340 - JOINVILLE LE PONT - quai de la Marne": "Informations non disponibles",
#     "GRILLON - SARL LE SUQUET": "Informations non disponibles",
#     "GROUPE DORR": "Informations non disponibles",
#     "CLAUDIA - 75015 PARIS - 51 Avenue de La MOTTE-PICQUET": "43776601700010",
#     "BRIOCHE DORÉE - 78 Av des CHAMPS ELYSÉES - 75008 PARIS": "Informations non disponibles",
#     "CAFÉ DE L'ÉGLISE - 92110 CLICHY - 100 Bld Jean JAURÈS": "Informations non disponibles",
#     "BRIOCHE DORÉE - 78 Av des CHAMPS ELYSÉES - 75008 PARIS": "31890659100014",
#     "BROOKLYN CAFE - 75017 PARIS - 32 Place Saint FERDINAND": "Informations non disponibles",
#     "CAFE DU MEXIQUE - 75016 PARIS - 3 Place de MEXICO": "Informations non disponibles",
#     "CAFÉ DE L'ÉGLISE - 92110 CLICHY - 100 Bld Jean JAURÈS": "83226626600015",
#     "CHEZ BEBER  - 75006 PARIS - 71 Bld du MONTPARNASSE": "42507282400011",
#     "BROOKLYN CAFE - 75017 PARIS - 32 Place Saint FERDINAND": "Informations non disponibles",
#     "CAFE DU MEXIQUE - 75016 PARIS - 3 Place de MEXICO": "Informations non disponibles",
#     "CHEZ BEBER  - 75006 PARIS - 71 Bld du MONTPARNASSE": "42507282400011",
#     "CHIEN QUI FUME (Le) - 75001 PARIS - 33 Rue du PONT-NEUF": "31013032300015",
#     "CIAL - 75001 PARIS - rue Mondétour - 16": "Informations non disponibles",
#     "CLOS BOURGUIGNON (Le) - 75009 PARIS - 39 Rue CAUMARTIN": "39260504400017",
#     "COMPAGNIE (La) - 75017 PARIS - 123 Av de WAGRAM": "84275832800012",
#     "DA ROSA - 75001 PARIS - 7 Rue ROUGET de l'ISLE": "75239417100017",
#     "DIPLOMATE (Le)- 75016 PARIS - 15 Rue SINGER": "83389469400011",
#     "DODDY'S - 75017 PARIS - 80 Rue Mstislav ROSTROPOVITCH": "84275832800012",
#     "EL SOL - 75008 - 22 RUE DE PONTHIEU": "50186386400028",
#     "BROOKLYN CAFE - 75017 PARIS - 32 Place Saint FERDINAND": "Informations non disponibles",
#     "CAFE DU MEXIQUE - 75016 PARIS - 3 Place de MEXICO": "Informations non disponibles",
#     "CHEZ BEBER  - 75006 PARIS - 71 Bld du MONTPARNASSE": "42507282400011",
#     "CHIEN QUI FUME (Le) - 75001 PARIS - 33 Rue du PONT-NEUF": "31013032300015",
#     "CIAL - 75001 PARIS - rue Mondétour - 16": "Informations non disponibles",
#     "CLOS BOURGUIGNON (Le) - 75009 PARIS - 39 Rue CAUMARTIN": "39260504400017",
#     "COMPAGNIE (La) - 75017 PARIS - 123 Av de WAGRAM": "84275832800012",
#     "DA ROSA - 75001 PARIS - 7 Rue ROUGET de l'ISLE": "75239417100017",
#     "DIPLOMATE (Le)- 75016 PARIS - 15 Rue SINGER": "83389469400011",
#     "DODDY'S - 75017 PARIS - 80 Rue Mstislav ROSTROPOVITCH": "84275832800012",
#     "EL SOL - 75008 - 22 RUE DE PONTHIEU": "50186386400028",
#     "FAJITAS - 75006 PARIS - 15 Rue DAUPHINE": "43426634200014",
#     "GERMAIN - 94340 - JOINVILLE LE PONT - quai de la Marne": "85255555600012",
#     "GRILLON - SARL LE SUQUET": "45361623700013",
#     "GROUPE DORR": "32918652200010",
#     "HIPPOPOTAMUS BASTILLE - 75004 PARIS - 1 Bld BEAUMARCHAIS": "Informations non disponibles",
#     "IL PARADISIO - 75017 PARIS - 30 RUE LEGENDRE": "Informations non disponibles",
# }

# for v in di.values():
#     get_infos_from_a_siren(str(v)[:-5])


def load_json_file(path):
    with open(path, "r", encoding="utf-8") as file:
        di = json.load(file)
    return di


def write_json_file(di, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(di, ensure_ascii=False))
    return


siret_db_path = WORK_PATH / "siret_databank.json"


# je digere la reponse de Mistral AI
res = pyperclip.paste()


res_di = json.loads(res)
di = load_json_file(siret_db_path)

new_di = di
for k, v in res_di.items():
    if (
        v
        not in [
            "Informations non disponibles",
            "Non trouvé",
            "SIRET non disponible",
            "SIRET non trouvé",
        ]
        and k not in new_di.keys()
        # and len(v.replace(" ", "").strip()) == 14
    ):
        new_di[k] = v

sorted_new_di = {key: new_di[key] for key in sorted(new_di)}
write_json_file(sorted_new_di, siret_db_path)


# j ouvre je classe le json
di = load_json_file(siret_db_path)
li = [
    "CASA DI MARIO - 75007 PARIS - 132 Rue du BAC",
    "DEI FRATELLI - 75001 PARIS - 10 Rue des PYRAMIDES",
    "GENTLEMEN - JARDINS DE L'ARCHE - 92000 NANTERRE",
    "GRAND CARNOT (Le) - 75017 PARIS - 32 Avenue CARNOT angle 40 Rue des ACACIAS",
    "MANHATTAN TERRAZZA - 108 Av de VILLIERS - 75017 PARIS",
    "RALLYE PASSY (BOUILLON PASSY) - 75016 PARIS - 34 Rue de l'ANNONCIATION",
    "AFFRANCHIS (Les) - 75012 PARIS - 14 Avenue DAUMESNIL",
    "ANDORINHA - 75016 PARIS - 199 Avenue de VERSAILLES - ex VERSAILLES AVENUE - MONTCASTEL",
    "AQUABIKE - 75015 PARIS - 45 Avenue de la MOTTE-PICQUET",
    "ASCENSION - 75018 - 62 RUE CUSTINE",
    "ASIAN KITCHEN - 75007 PARIS - 49 Quai d'ORSAY - 20240925",
    "ASSOCIES (Les) - 75012 PARIS - 50 Bld de la BASTILLE",
    "AVELLINO - 4 Bld Richard WALLACE - 92800 PUTEAUX",
    "AZZURO - 92100 BOULOGNE-BILLANCOURT - 59 Place René CLAIR",
    "BAIGNEUSES (Les) - 64200 BIARRITZ - 14 Rue du PORT VIEUX",
    "BAR DES SPORT - 75012 - 73 AVENUE DU GENERAL MICHEL BIZOT",
    "BARIOLÉ (Le) - 75020 PARIS - 103 Rue de BELLEVILLE",
    "BEBER - 75006 PARIS - 71 Bld du MONTPARNASSE",
    "BILLY BILLI - 92000 NANTERRE",
    "BISTROT BALNÉAIRE (Le) - 40150 SOORTS-HOSSEGOR - 1830 Avenue du TOURING CLUB",
    "BISTROT CHARBON (Le) - 75004 PARIS- 131 rue Saint MARTIN",
    "BISTROT DU FAUBOURG - 12 Allée de l'ARCHE - 92400 COURBEVOIE",
    "BOIS LE VENT (Le) - 75016 PARIS - 59 Rue de BOULAINVILLIERS",
    "BON JACQUES (Le) - 75017 - 34 Rue Jouffroy d'ABBANS",
    "BOUDOIR (Le) - 75006 PARIS - 202 Bld Saint GERMAIN",
    "BOULANGERIE DE L'OLYMPIA",
    "BOULEDOGUE (Le) - 75003 PARIS - 20 Rue RAMBUTEAU",
    "BRASSERIE LOLA - MURS ET FONDS - 75015 PARIS - 99 rue du THÉÂTRE",
    "BRIOCHE DORÉE - 78 Av des CHAMPS ELYSÉES - 75008 PARIS",
    "BROOKLYN CAFE - 75017 PARIS - 32 Place Saint FERDINAND",
    "CAFÉ DE L'ÉGLISE - 92110 CLICHY - 100 Bld Jean JAURÈS",
    "CHEZ BEBER \xa0- 75006 PARIS - 71 Bld du MONTPARNASSE",
    "CHIEN QUI FUME (Le) - 75001 PARIS - 33 Rue du PONT-NEUF",
    "CIAL - 75001 PARIS - rue Mondétour - 16",
    "CLAUDIA - 75015 PARIS - 51 Avenue de La MOTTE-PICQUET",
    "CLOS BOURGUIGNON (Le) - 75009 PARIS - 39 Rue CAUMARTIN",
    "COMPAGNIE (La) - 75017 PARIS - 123 Av de WAGRAM",
    "DA ROSA - 75001 PARIS - 7 Rue ROUGET de l'ISLE",
    "DIPLOMATE (Le)- 75016 PARIS - 15 Rue SINGER",
    "DODDY'S - 75017 PARIS - 80 Rue Mstislav ROSTROPOVITCH",
    "EL SOL - 75008 - 22 RUE DE PONTHIEU",
    "FAJITAS - 75006 PARIS - 15 Rue DAUPHINE",
    "GERMAIN - 94340 - JOINVILLE LE PONT - quai de la Marne",
    "GRILLON - SARL LE SUQUET",
    "HIPPOPOTAMUS BASTILLE - 75004 PARIS - 1 Bld BEAUMARCHAIS",
    "IL PARADISIO - 75017 PARIS - 30 RUE LEGENDRE",
    "JAD - PARIS 75002 - 35 Bld BONNE NOUVELLE",
    "LE DIPLOMATE - Place SINGER - 75016 PARIS",
    "MADELEINE 7 (Le) - 75001 PARIS - 7 Bld de La MADELEINE",
    "MAISON DE L'INFANTE - 64500 SAINT JEAN DE LUZ - 1 Rue de l'INFANTE",
    "MAISON MULOT - 75006 - RUE DE SEINE",
    "MAMMA ROMA - 55 Rue du CHERCHE MIDI - 75006 PARIS",
    "MAMY CREPES - 18 Rue SURCOUF - 75007 PARIS",
    "MIZON - 75010 - 37 QUAI DE VALMY",
    "MONSIEUR LE ZINC - 75006 PARIS - R-15 rue MONSIEUR LE PRINCE",
    "MOULIN de la GALETTE - 95110 SANNOIS - 16 Rue des MOULINS",
    "MUSEE DU CHOCOLAT - 14 AVENUE BEAURIVAGE - 64200 BIARRITZ",
    "NOMAD'S - 12 Place du MARCHE SAINT HONORÉ - 75001 PARIS",
    "NOVIMENTO - 75008 PARIS - 11 Rue TRONCHET",
    "O'NIEL - 75006 - 20 RUE DES CANNETTES",
    "PACHYDERME - 2 BD SAINTMARTIN 75010 PARIS",
    "PAOLA - 94300 VINCENNES - 60 Rue de MONTREUIL",
    "PAOLA - 94300 VINCENNES - 60 Rue de MONTREUIL",
    "PAPARAZZI - 75009 PARIS - 6 Square de l'OPÉRA - Louis JOUVET",
    "PETIT BOUILLON VAVIN (Le) - 75006 PARIS - 119 Bld du MONTPARNASSE",
    "PETIT MARGUERY (Au) - 75013 PARIS - 9 Bld de PORT-ROYAL",
    "PETITES CANAILLES - 92300 LEVALLOIS - 6 place du 11 novembre",
    "PIPPA - 92800 PUTEAUX - 2 RUE ANATOLE FRANCE",
    "PLACE (La)- 92500 RUEIL-MALMAISON - 16 Place des IMPRESSIONNISTES",
    "PORTE MONTMARTRE (La) - 75018 PARIS - 87 Bld NEY",
    "PREVOYANT (Le) - 75010 PARIS - 79 bd de MAGENTA",
    "RICHER (Le) - 75009 PARIS - 1 Rue RICHER",
    "STARBUCKS CAFÉ - 75018 PARIS - 10 Rue NORVINS",
    "STELLAS MARIS - 132 Rue du BAC - 75007 PARIS",
    "TELEPHONES (Les) - 75007 PARIS - 54 Rue CLER",
    "TONTON BECTON - 75015 - 19 bld lefevre",
    "TOUR MAUBOURG (La) - 75007 PARIS - 58 Bld de la TOUR MAUBOURG",
    "TRATTORIA CHIC- 92200 NEUILLY sur SEINE - 144 Avenue Charles de GAULLE",
    "TROUVILLE - Saint Mandé",
    "VERSAILLES - 92130 ISSY les MOULINEAUX - 1 rue Ernest RENAND",
    "VILLA FLEURY - 92190 MEUDON - 22 Place Henri BROUSSE",
    "WOOD - LE BISTROT À VINS \xa0- 92400 COURBEVOIE - 35 Place des COROLLES",
    "ZACK RESTAURANT - 93000 SAINT DENIS - 24 Avenue des FRUITIERS",
    "ZIGZAG - 75005 PARIS - 32 rue des CARMES",
    "CHEZ CLAUDE - 166 Rue SAINT-HONORE - 75001 PARIS",
    "CORDONNERIE - 75016 PARIS - 35 Rue de L'ANNONCIATION",
    "ANNA - 75008 PARIS - 14 Rue MARBEUF \xa0- Dossier LATREILLE Benoit",
    "ABRADAVIO - 3 Rue de MAUBEUGE - 75009 PARIS",
    "ABSINTHE CAFE - 54 RUE TURBIGO - 75001 PARIS",
    "AVENIR - 104 Rue Sadi Carnot - 92 VANVES",
    "BEAUX PARLEURS - SAS JADE - 35 Bld BONNE NOUVELLE - 75002 PARIS",
    "BILLY BILLI - 92000 NANTERRE",
    "BISTROT VALOIS (Le) - 75001 PARIS - 1 Bis Place de VALOIS",
    "BOULANGERIE - 48 Bld Gouvioon St Cyr - 75017 PARIS",
    "PAVE (Le) - 75003 PARIS - 7 Rue des LOMBARDS",
]

manquante = [et for et in li if et not in di.keys()]

LOGGER.info("total")
LOGGER.info(len(li))
LOGGER.info("manquante")
LOGGER.info(len(manquante))

if len(manquante) < 10:
    request = '["' + (
        '",\n"'.join(manquante)
        + '"]'
        + "\n Trouve le SIRET de chacun des établissements dans cette liste. Exporte le résultat sous forme d'un dictionnaire json. Présente moi le résultat sous la forme k:v où k est chacun des membres de la liste et v le SIRET que tu as trouvé."
    )
else:
    request = '["' + (
        '",\n"'.join(random.sample(manquante, 10))
        + '"]'
        + "\n Trouve le SIRET de chacun des établissements dans cette liste. Exporte le résultat sous forme d'un dictionnaire json. Présente moi le résultat sous la forme k:v où k est chacun des membres de la liste et v le SIRET que tu as trouvé."
    )

pyperclip.copy(request)


# TODO : trier les siren/ SIRET et trouver spécifiquement les SIRET
# vérifie que les SIRET que tu as trouvé contiennent bien 14 chiffres. Relance la recherche si ce n'est pas le cas.
