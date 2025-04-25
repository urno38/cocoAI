from ruamel.yaml import YAML, CommentedMap
from ruamel.yaml.scalarstring import PreservedScalarString

# Define the YAML content
yaml_content = """
JURIDIQUE_CORPORATE:
    ACTES SIGNES: {}
    ETATS DES INSCRIPTIONS: {} # tous les états d'inscription du fond de commerce
    K BIS - INSEE - STATUTS: {} #KBIS de la société, immatriculation au registre SIRENE
    REGISTRES NANTISSEMENT DES TITRES: {} # nantissement des titres de la société  de la société des parts sociales
    ORIGINE DE PROPRIETE DES TITRES: {} # acte de cession de titres de la société
    ORIGINE DE PROPRIETE DU FONDS: {} # acte de cession de titres du fonds de commerces
    CORPORATE: {} # tout compte rendu de conseil de surveillance ou d'oragane de contrôle de la société, PV de l'AG ou PV de décision de l'associé unique ou tout autre document juridique lié à l'administration de la société, attestation de beneficiaires de la societe
    LITIGES: {} # tous les documents relatifs à des litigrs

JURIDIQUE_EXPLOITATION_ET_CONTRATS:
    CAISSE: {} #attestation de conformité de caisse
    CONTRATS CREDITS BAUX: {} #contrat de crédit-bail ou de location longue durée
    CONTRATS FOURNISSEURS: {}
    DIAGNOSTICS: {} # amiante, DPE, plomb, termites
    ASSURANCE: {} #attestation d'assurance, responsabilité civile exploitation et autres ainsi que les contrats s'y afférent
    LICENCE IV: {} #attestation de la license, récépisssé de license
    TERRASSE - VOIRIE: {} # quittance de terrasse et certificat de la mairie de paris
    URBANISME: {} # rapport d'urbanisme

DOCUMENTATION_FINANCIERE:
    BILANS - CA: {} #tous les documents financiers, attestation de CA, états d'immobilisation, tous document issu de la comptabilité, tout tableau financier, tableau d'amortissement d'emprunt bancaire
    COMPTES COURANTS: {} # attestation de compte courant d'associés
    EMPRUNTS: {} # tout ce qui concerne les emprunts
    ATTESTATIONS DE REGULARITE IMPOTS URSSAF: {} #attestation de vigilance et de régularité

BAUX - QUITTANCE: {} #quittance de loyer et taxe fonciere ou appel de charges de copopritete

SOCIAL:
    BULLETINS PAIE: {}
    CONTRATS DE TRAVAIL: {}
    COTISATIONS: {} # journal de paie ou documents comptables relatifs aux prestations sociales
    DEMISSIONS: {}
    LISTE DU PERSONNEL: {}
    MUTUELLE - PREVOYANCE: {}
"""

# Initialize the YAML parser
yaml = YAML()
yaml.preserve_quotes = True

# Parse the YAML content
data = yaml.load(yaml_content)


# Function to recursively sort a dictionary and preserve comments
def sort_dict(d):
    if isinstance(d, CommentedMap):
        # Sort the dictionary by keys
        sorted_d = CommentedMap()
        for key in sorted(d.keys()):
            value = d[key]
            sorted_d[key] = sort_dict(value)  # Recursively sort nested dictionaries
            # Preserve comments
            if d.ca.items.get(key):
                sorted_d.yaml_add_eol_comment(d.ca.items[key][2].comment[1], key)
        return sorted_d
    return d


# Sort the YAML content
sorted_data = sort_dict(data)

# Output the sorted YAML content
sorted_yaml_content = yaml.dump(sorted_data, transform=PreservedScalarString)

print(sorted_yaml_content)
