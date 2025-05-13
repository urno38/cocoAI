import json
import random
from pathlib import Path

import pandas as pd
import pyperclip

from common.identifiers import get_infos_from_a_siren
from common.logconfig import LOGGER
from common.path import WORK_PATH, load_json_file, write_json_file

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
