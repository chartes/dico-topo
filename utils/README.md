# Enrichissement des données

## Fichiers utilisés pour l'enrichissement des données
* Recup_ville.xsl permet de récupérer leurs identifiants, le nom des communes, leurs cantons
* Matchscript.py permet de trouver des communes à la suite d'une comparaison sur les substring
* add_commune.py permet d'ajouter les balises communes sur les différents noms de commune

## Procédure d'enrichissement du code INSEE des communes
- Extraction des noms des communes avec le fichier Recup_ville.xsl
- Nettoyage de cette première liste sur le logiciel Dataiku
- Normalisation de la liste pour comparaison des chaînes de caractère sur le logiciel Dataiku
- Première comparaison en *exact match* avec le nom des communes INSEE 2011 sur le logiciel Dataiku
- Deuxième comparaison des communes restantes sur les *substring* avec le script Matchscript.py
- Troisième comparaison des communes sans match en fuzzy join sur le logiciel Dataiku
- Mise en place d'un tableur pour permettre la correction du texte 

##Procédure d'enrichissement sur Dataiku : Exemple du département 73 (cf. DT73.zip)

1. Ajout du fichier CSV DT73 des communes extraites depuis le fichier DT73.xml 
2. Mise en ordres des données avec suppression des espaces vides, alignement des cases et création d'une colonne qui contient une version normalisée de la commune
3. Ajout du fichier des communes 2011 avec le code INSEE, suppression des communes qui ne sont pas du département, nettoyage des colonnes et normalisation du nom des communes
4. Fusion des deux jeux de données en fonction des noms normalisés et ajout d'une colonne contenant le code INSEE et du nom normalisé dans le fichier DT73 
5. Séparation en deux du fichier obtenu avec d'un côté les communes avec un code INSEE et ceux vide de l'autre
6. Extraction des communes sans code INSEE dans un fichier CSV qui grâce est utilisé par le fichier Matchscript.py pour trouver de nouvelle correspondance. Le script nous fournit un fichier csv
7. Le fichier csv est réutilisé dans dataiku pour un fuzzyjoin avec le fichier des communes de 2011 nettoyé et obtention du dernier fichier. 
8. Création du fichier de correction DT73.ods avec l'ajout d'un niveau de risque. High pour ceux issue de la première fusion, Medium pour ceux de la deuxième et de Low pour la troisième.

L'ensemble de la procédure est la même pour chaque département. Il suffit à chaque fois de copier la procédure et de mettre le numéro du département correspondant. 