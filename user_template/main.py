from cocoAI.company import get_all_siret_from_a_siren
from common.identifiers import pick_id

# li = get_all_siret_from_a_siren(652014754)


siren = pick_id("GALLA")
li = get_all_siret_from_a_siren(siren)

# print(li)
