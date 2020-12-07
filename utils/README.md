Enrichissement des données
===

Procédure d’insertion des codes communes pour les communes de localisation citées dans la définition des articles.

## Scripts utiles

### Identification des articles de type commune dans les fichiers livrés
- `Recup_ville.xsl` pour un DT en entrée, il liste dans un tableau les articles candidats de type commune.
- `Matchscript.py` pour un tableau des articles candidats en entrées et la liste des communes du département de 2011, il fournit deux tableaux de résultat commune/insee possibles `result.csv` et dans un tableau différent le reste des articles communes possibles
- `Injection_INSEE.xsl` prend en entrée le fichier XML qui continent l'intégralité des articles de type commune avec leur code INSEE et les intégre dans le DT
- `Injection_attr_commune.xsl` ajoute l'attribut type dans la balise article si l'article contient une balise INSEE comme enfant


### Balisage des communes citées en définition des articles
- `add_commune.py` pour un DT en entrée et un tableau des communes avec leur code INSEE, liste les balises localisations qui ne correspondant pas aux demandes spécifié dans « DTXX_liageINSEE_localisation-commune-desambiguisation.csv » et donne le fichier `output2.xml` avec des balises communes dans certaines balises localisations
- `add_Insee_Commune.py` pour l'`output2.xml` en entrée, liste les balises communes sans code code insee dans « DTXX_liageINSEE_localisation-commune.csv » et donne le fichier `output3.xml` avec l'attribut insee et son code dans les balises communes
- `Update_Commune_INSEE.py` pour « DTXX_liageINSEE_localisation-commune.csv » et `output3.xml` en entrée, le script ajoute les attributs insee et le code dans les balises communes qui n'ont pu être ajouter automatiquement par `add_Insee_Commune.py` dans un fichier `output4.xml`
- `Update_INSEE_Code.py` pour « DTXX_liageINSEE_localisation-commune-desambiguisation.csv »  et `output4.xml` en entrée. Il sort le fichier `output5.xml` en ayant intégré les balises communes et code insee dans certaines des balises localisations restantes

## Outils de contrôle
Il existe deux scripts de contrôle :

- `Testscript.py`, prend un fichier xml d'un DT ou un output en entrée et permet à travers un tableau de résultat de contrôler les injections de code insee et que les balises communes respectent les normes décidés aux débuts du projet.
- `TestResultatDT.py`, prend le DT original livré par Wordpro et l'output à tester en entrée. Il livre deux fichiers en sortie: `@DTXX_result.csv` qui offre une comparaison chiffrer des deux DT et `@DTXX_result_commune.csv` qui permet de controler que les injections n'ont pas cassé de chaîne de caractères et ainsi nous permet de les corriger pour la création de `output6.xml`
- Le dernier fichier se situe dans le dossier data et se nomme `_OUTPUT6_VALDATION_PROCEDURE.pdf`. Il s'agit d'une procédure à suivre pour être sûr que toutes les vedettes soient grammaticalement juste, qu'il n'y ait pas d'inversion de caractères, qu'il n'y ait pas de localisation mal segmenté

### Injection des nouveaux ids (attribués par l’application)
- `insert_new-ids.py` : prend en entrée `output6.xml` et le mapping des anciens ids et des nouveaux attribués par l’application, pour injecter ces nouveaux identifiants dans `output7.xml`.
  
## Exemple avec le DT73.xml d'un cheminement pour l'ajout de la localisation des différents articles

### Procédure d'enrichissement du code INSEE des communes
- Extraction des probables noms des communes du `DT73.xml` avec le fichier `Recup_ville.xsl`
- Nettoyage de cette première liste sur le logiciel Dataiku (Voir procédure d'enrichissement )
- Normalisation de la liste pour comparaison des chaînes de caractère sur le logiciel Dataiku
- Première comparaison en *exact match* avec le nom des communes INSEE 2011 sur le logiciel Dataiku
- Deuxième comparaison des communes restantes sur les *substring* avec le script `Matchscript.py`
- Troisième comparaison des communes sans match en fuzzy join sur le logiciel Dataiku
- Mise en place d'un tableur pour permettre la correction du texte  (Voir la procédure d'enrichissement détaillé sur Dataiku)
- Correction manuel des communes dont la précision n'est pas High
- Ajout de la balise INSEE avec son code avec le fichier `Injection_INSEE.xsl`
- Ajout de l'attribut type avec commune dans la balise article avec le fichier `Injection_attr_commune.xsl`
- On obtient ainsi le `DT73.xml` avec les articles des communes 


## Ajout des balises communes dans les balises localisation
- Utilisation du script `add_commune.py` qui ajoute les balises communes dans les balises localisations selon les règles établies à l'avance et fournit le fichier `output2.xml` et  `DT73_liageINSEE_localisation-commune-desambiguisation.csv`
- Le fichier XML obtenue doit être nettoyer des balises  &lt;tmp>et &lt;/tmp> qui sont ajouter pour pouvoir placer certaines balises communes.
- Le XML récupéré sert de base pour le script suivant `add_Insee_Commune.py` , il récupère le contenu dans la balise commune puis le compare avec la liste des noms de communes et si ça correspond il ajoute un attribut insee avec son code. Il fournit le fichier `output3.xml` et le `DT73_liageINSEE_localisation-commune.csv` pour les balises communes qui n'ont pas de code insee.
- Le tableau `DT73_liageINSEE_localisation-commune.csv` corrigé est ensuite réinjécté par le script  `Update_Commune_INSEE.py` dans `output3.xml`. Il contient un travail manuel de rajout des codes insee donc un travail de vérification manuel du fichier est à faire avant l'injection avec des possibles défauts de segmentaiton, ajout de nouvelles articles communes qui ont pu être manqués sur la première étape, faute de typo ... Une colonne commentaire est prévu à cet effet. Le script sort le fichier `output4.xml`. Il est conseillé d'utiliser le fichier `Testscript.py` sur le fichier `output4.xml` pour corriger des erreurs possibles.
-  Le tableau `DT73_liageINSEE_localisation-commune-desambiguisation.csv` corrigé est réinjécté par le script `Update_INSEE_Code.py` dans le fichier `output4.xml` Il contient un important travail manuel sur les balises localisations sans balise commmune donc il peut y avoir beaucoup de corrections manuel de tout type à réaliser donc il faut prendre son temps de bien regarder les différents commentaires notés par le correcteur. Le script fournit le fichier `output5.xml`
- Le fichier XML obtenue doit être nettoyer des balises  &lt;tmp>et &lt;/tmp> qui sont ajouter pour pouvoir placer certaines balises communes dans les balises localisations non-stéréotypé.
- Il est conseillé d'utiliser le fichier `Testscript.py` sur le fichier `output5.xml` pour corriger de possibles erreurs injectées à ce moment.
- Il faut ensuite comparer le fichier XML du départ `DT73.xml` et `output5.xml` avec `TestResultatDT.py` pour corriger les dernières erreurs possibles. Le script fournit les csv `@DT73_result.csv` pour obtenir une vision globale chiffré et le fichier `@DT73_result_commune.csv` pour corriger les dernières manuellement enregistré sous le nom `output6.xml`
- Une dernière étape est de contrôler avec des xpaths contenues dans le fichier `_OUTPUT6_VALDATION_PROCEDURE.pdf` pour être sûr que le fichier `output6.xml` soit corrigé.

  

####Procédure d'enrichissement sur Dataiku : Exemple du département 73 (cf. DT73.zip)

1. Ajout du fichier CSV DT73 des communes extraites depuis le fichier DT73.xml 
1. Mise en ordres des données avec suppression des espaces vides, alignement des cases et création d'une colonne qui contient une version normalisée de la commune
1. Ajout du fichier des communes 2011 avec le code INSEE, suppression des communes qui ne sont pas du département, nettoyage des colonnes innutiles et normalisation du nom des communes
1. Fusion des deux jeux de données en fonction des noms normalisés et ajout d'une colonne contenant le code INSEE et du nom normalisé dans le fichier DT73 
1. Séparation en deux du fichier obtenu avec d'un côté les communes avec un code INSEE et le reste de l'autre
1. Extraction des communes sans code INSEE dans un fichier CSV qui sert de fichier d'entréer pour `Matchscript.py` pour trouver de nouvelle correspondance. Le script nous fournit un nouveau fichier de reste.
1. Le fichier csv est réutilisé dans dataiku pour un fuzzyjoin avec le fichier des communes de 2011 nettoyé et obtention du dernier fichier. 
1. Création du fichier de correction DT73.ods avec l'ajout d'un niveau de risque. High pour ceux issue de la première fusion de dataiku, Medium pour ceux de la deuxième issue de `Matchscript.py` et de Low pour ceux issue du fuzzyjoin

L'ensemble de la procédure est la même pour chaque département. Il suffit à chaque fois de copier la procédure et de mettre le numéro du département correspondant. 

