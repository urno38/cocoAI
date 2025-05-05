from random import sample

from cocoAI.company import main
from common.identifiers import get_entreprise_name, pick_id
from common.path import get_df_folder_possibles

# main(siren=pick_id("GALLA", kind="siren"), entreprise="GALLA")
# main(siren=pick_id("BISTROT_VALOIS", kind="siren"), entreprise="BISTROT_VALOIS")


siret = sample(get_df_folder_possibles()["siret"].dropna().values.tolist(), 1)[0]
siren = siret[:-5]
main(siren=siren, entreprise=get_entreprise_name(siren))
