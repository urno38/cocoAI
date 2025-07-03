# cocoAI

*co*mptoir et *co*mmerce *AI*

## Procédure d'installation

1. Exécuter ```install.bash```

 |                    | Windows     | Mac          |
 | ------------------ | ----------- | ------------ |
 | fichier à exécuter | install.ps1 | install.bash |

attention bien utiliser pip (et pas uv à la première install) car certains packages (comme win32com ou docx2pdf) ne sont pas accessbles via uv

1. Récupérer les clés et les enregistrer dans common/keys.py
2. Générer une clé ssh et l'envoyer sur le github  

### améliorations

- une fois que le pdf des terrasses est téléchargé, le classer là où il faut dans le dossier documents
- refacto la procédure pour la simplifier
- penser à faire imprimer un dessin mistral pour ma sortie

## to do list

- implémenter la charte graphique de CC dans les beamers
- les bénéficiaires indirects ont un diagramme à améliorer : pointillés et sans les holdings intermédiaires
- présenter les avantages de mettre en place une procédure ou pas dans la boite comptoirs et commerces
- annuaire partagé, google workspace
- applications sur les téléphones portables

## Mode d'emploi sur mac

1. Ouvrir un terminal

2. taper

```bash
bash
```

attendre que la commande soit terminée puis

```bash
cd Documents/cocoAI
git pull
uv sync
source .venv/bin/activate
cd user_template
```

3. utilisation

```bash
python3 main_script_chapeau.py
```

4. suivre les instructions qui s'affichent sur le terminal
