# Enrichissement des données

## Fichiers utilisés pour l'enrichissement des données
* Recup_ville.xsl permet de récupérer leurs identifiants, le nom des communes, leurs cantons
* Matchscript.py permet de trouver des communes à la suite d'une comparaison sur les substring

## Procédure d'enrichissement
- Extraction des noms des communes avec le fichier Recup_ville.xsl
- Nettoyage de cette première liste sur le logiciel Dataiku
- Normalisation de la liste pour comparaison des chaînes de caractère sur le logiciel Dataiku
- Première comparaison en *exact match* avec le nom des communes INSEE 2018 sur le logiciel Dataiku
- Deuxième comparaison des communes restantes en *exact match* avec le nom des communes INSEE 2011 sur le logiciel Dataiku
- Récupération de leur code INSEE 2018 sur le logiciel Dataiku
- Troisième comparaison des communes restantes sur les *substring* avec le script Matchscript.py
- Quatrième comparaison des communes sans match en fuzzy join sur le logiciel Dataiku
- Mise en place d'un tableur pour permettre la correction du texte

