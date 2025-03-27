from cocoAI.company import get_infos_from_a_siret
from cocoAI.folder_tree import main

# recherche par siren
for siren in [
    818114456,  # SIAM-POMPE
    310130323,  # GALLA
    481383537,  # BISTROT VALOIS
]:
    main(siren)


# recherche par siret
for siret in [
    65201475400012,  # LE ROI DE SIAM
]:
    get_infos_from_a_siret(siret)
    print(int(str(siret)[:-5]))
    main(int(str(siret)[:-5]))
