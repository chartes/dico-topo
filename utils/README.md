# Enrichissement des données

## Fichiers utilisés pour l'enrichissement des données
* Recup_ville.xsl permet de récupérer leurs identifiants, le nom des communes, leurs cantons
* Matchscript.py permet de trouver des communes à la suite d'une comparaison sur les substring
* Injection_attr_commune.xsl ajoute l'attribut type dans la balise article
* Injection_INSEE.xsl ajoute la balise INSEE et son code
* add_commune.py permet d'ajouter les balises communes sur les différents noms de commune. Il fournit la liste des balises localisations qui ne corresponde pas à certaines valeurs.
* add_Insee_Commune.py ajoute l'attribut INSEE et son code dans les balises communes. Il nous fournit un fichier csv avec les échecs.
* Update_Commune_INSEE.py utilise le tableau de correction pour ajouter les balises communes dans les balises localisations du fichier XML
* Update_INSEE_Code.py rajoute les codes INSEE dans les balises communes qui n'ont pas matchs


## Procédure d'enrichissement du code INSEE des communes
- Extraction des noms des communes avec le fichier Recup_ville.xsl
- Nettoyage de cette première liste sur le logiciel Dataiku
- Normalisation de la liste pour comparaison des chaînes de caractère sur le logiciel Dataiku
- Première comparaison en *exact match* avec le nom des communes INSEE 2011 sur le logiciel Dataiku
- Deuxième comparaison des communes restantes sur les *substring* avec le script Matchscript.py
- Troisième comparaison des communes sans match en fuzzy join sur le logiciel Dataiku
- Mise en place d'un tableur pour permettre la correction du texte  (Voir la procédure d'enrichissement détaillé sur Dataiku)
- Correction manuel des communes dont la précision n'est pas High
- Ajout de l'attribut type avec commune dans la balise article avec le fichier Injection_attr_commune.xsl
- AJout de la balise INSEE avec son code avec le fichier Injection_INSEE.xsl


## Ajout des balises communes dans les balises localisation
- Utilisation du script «  add_commune.py » qui ajoute les balises communes dans les balises localisations selon les règles établies à l'avance 
- Le script nous fournit un premier XML et un tableau csv avec les échecs « DTXX_liageINSEE_localisation-commune-desambiguisation.csv » qui doit permettre une correction aisée des localisations qui ne correspondent pas aux cas définis dans le script.
- Le fichier XML obtenue doit être nettoyer des balises  &lt;tmp>et &lt;/tmp> qui sont ajouter pour pouvoir placer certaines balises communes facilement et qui peuvent donc gèner les étapes suivantes
- Le XML récupéré sert de base pour le script suivant « add_Insee_Commune.py », il récupère le nom contenu dans la balise commune puis le compare avec la liste des noms de communes et si ça correspond il ajoute un attribut insee avec son code. 
- Le script fournit un nouvelle XML avec les codes ajoutés dans les attributs insee mais aussi un fichier csv « DTXX_liageINSEE_localisation-commune.csv » qui contient le nom des communes dont les noms n'ont trouvé aucune correspondace à cause d'une erreur de typo ou encore des abréviations et qui doit être corrigé avec le tableau contenant les communes.
- Le tableau « DTXX_liageINSEE_localisation-commune.csv » corrigé est ensuite réinjécté par le script  « Update_Commune_INSEE.py ». Il est réinjécté par le script « Update_INSEE_code.py » et rajoute les codes INSEE sur les balises communes déjà placé issu du script « add_INSEE_commune.py ». 
-  Le tableau « DTXX_liageINSEE_localisation-commune-desambiguisation.csv » corrigé est réinjécté par le script Update_INSEE_code.py. Il contient un travail manuel avec aussi bien les valeurs où il faut poser les balises communes mais aussi les codes INSEE donc cette injection permet de faire l'intégralité du travail de correction en une seul passe.  
- Le fichier XML obtenue doit être nettoyer des balises  &lt;tmp>et &lt;/tmp> qui sont ajouter pour pouvoir placer certaines balises communes dans les balises localisations non-stéréotypé.
- Un test de la validité des données est fait à chaque étape grâce à « Testscript.py» qui fournit un csv avec les chiffres qui permettent de connaître la qualité de la donnée et nous informe 

## Outils de contrôle
Il existe deux scripts de contrôle :

- Testscript.py, il s'agit d'un script qui sert à compter et à contrôler les nouvelles données inscrites dans un xml à n'importe quel étape de la procédure pour être sûr qu'il n'y ait pas de code INSEE fautive et qui soit bien du référentielle de 2011, et qu'il n'y ait pas d'autre fautes.
- TestResultatDT.py, il compare les chaînes de caractères et les modifications entre le DT original livré par Wordpro et le DT final ou à tester. Il permet de contrôler qu'aucune modification n'a altérer le DT de manière négative et que la cohérence est toujours présente.
- Le dernier fichier se situe dans le dossier data et se nomme _OUTPUT6_VALDATION_PROCEDURE.pdf. Il s'agit d'une procédure à suivre pour être sûr que toutes les vedettes soient grammaticalement juste, qu'il n'y ait pas d'inversion de caractères, qu'il n'y ait pas de localisation mal segmenté
  

####Procédure d'enrichissement sur Dataiku : Exemple du département 73 (cf. DT73.zip)

1. Ajout du fichier CSV DT73 des communes extraites depuis le fichier DT73.xml 
2. Mise en ordres des données avec suppression des espaces vides, alignement des cases et création d'une colonne qui contient une version normalisée de la commune
3. Ajout du fichier des communes 2011 avec le code INSEE, suppression des communes qui ne sont pas du département, nettoyage des colonnes et normalisation du nom des communes
4. Fusion des deux jeux de données en fonction des noms normalisés et ajout d'une colonne contenant le code INSEE et du nom normalisé dans le fichier DT73 
5. Séparation en deux du fichier obtenu avec d'un côté les communes avec un code INSEE et ceux vide de l'autre
6. Extraction des communes sans code INSEE dans un fichier CSV qui grâce est utilisé par le fichier Matchscript.py pour trouver de nouvelle correspondance. Le script nous fournit un fichier csv
7. Le fichier csv est réutilisé dans dataiku pour un fuzzyjoin avec le fichier des communes de 2011 nettoyé et obtention du dernier fichier. 
8. Création du fichier de correction DT73.ods avec l'ajout d'un niveau de risque. High pour ceux issue de la première fusion, Medium pour ceux de la deuxième et de Low pour la troisième.

L'ensemble de la procédure est la même pour chaque département. Il suffit à chaque fois de copier la procédure et de mettre le numéro du département correspondant. 