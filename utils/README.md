LIAGES INSEE (COG 2011), documentation
===

## Objectifs

Procédure d’insertion des codes communes :

1. pour les articles de type commune : ajout de `article/@type='commune'` et de la balise `insee` ;
1. pour les articles localisés dans une commune : ajout en localisation de `commune/@insee`.

**Output cas 1 (article de type commune)**

```xml
<article id="DT02-01486" type="commune">
  <vedette><sm>Clacy,</sm></vedette>
  <definition><localisation>canton de <commune insee="02408" precision="approximatif">Laon</commune></localisation>.</definition>
  <forme_ancienne>— <i>Claciacum,</i> <date>1122</date> <reference>(cart. de l’abb. de Saint-Martin de Laon, f° 172, bibl. de Laon)</reference>.</forme_ancienne>
  <!-- … -->
  <insee>02196</insee>
</article>
```

**Output cas 2 (article localisé dans une commune)**

```xml
<article id="DT02-00197" pg="13">
  <vedette><sm>Aulnois,</sm></vedette>
  <definition><typologie>moulin et ferme</typologie>, <localisation>commune de <commune insee="02196" precision="certain">Clacy</commune></localisation>…</definition>
  <forme_ancienne>— Molendinum de <i>Alneto,</i> <date>1174</date> <reference>(gr. cart. de l’év. de Laon, ch. 2)</reference>.</forme_ancienne>
    <!-- … -->
</article>
```


## Identification et liage des articles de type commune

### `Recup_ville.xsl`

**Description**. Pour un DT, repérer les articles de type commune et lister dans un CSV leur vedette et leur canton de localisation.

**Input** : `DT{id}.xml`

**Output** : CSV sur sortie standard. 3 colonnes :

- `ID` : identifiant de l’article (de type commune) – ex. `DT02-00196`
- `NomCommune` : vedette de l’article – ex. `Aulnois,`
- `NomCanton` : label du canton de localisation – ex. `canton de Laon` (utile pour désambiguiser l’identification d’une commune)

**Note**. Ce CSV est nettoyé dans Dataiku où le liage INSEE est fait sur `NomCommune` en différentes étapes (voir plus bas).

### `Matchscript.py`

**Description**. Pour les vedettes des articles de type commune non liées dans Dataiku, sortir des tableaux facilitant le liage manuel, selon différents cas.

**Input**

- `listcommune.csv` : liste des communes INSEE du seul département (pour déjouer les homonymies)
- `Rest_prepared.csv` : liste des vedettes des articles de type commune pour lesquelles le liage a échoué dans Dataiku.

**Output**

- `result2.csv` : vedettes alignées avec des communes dont le nom contient strictement la vedette (*exactMatch*). – plusieurs candidats possibles.
- `result3.csv` : vedettes alignées avec des communes dont le premier mot du nom est contenu dans la vedette (*exactMatch*). – plusieurs candidats possibles.
- `rest3.csv`  : les vedettes des articles de type commune toujours non liées (pas de match).

**Note**. `result2.csv` et `result3.csv` sont corrigés manuellement par les experts. `rest3.csv` sera traité dans Dataiku à coups de *fuzzy join*.


### `Update_article_commune.py`

**Description**. Inscrire dans le DT{id}.xml les liages INSEE pour les articles de type commune : ajout de `@type='commune'` et de l’élément `insee`.

**Input**

- `DT{id}`
- `DT{id}_liageINSEE_article-commune.csv` : le liage INSEE validé des vedettes des articles de type commune.

**Output**

- `DT{id}_communeINSEE.xml` : le DT avec le liage INSEE des articles de type commune.


## Identification et liage des communes de localisation

### `add_commune.py`

**Description**. Inscrire les balises `commune` pour repérer les noms de commune dans l’élément `localisation`. L’attribut `@precision` précise la relation entre le lieu et la commune de localisation :

- `@precision='certain'` : le lieu est localisé dans la commune
- `@precision='approximatif'` : le lieu est localisé de manière floue

**Input**

- `DT{id}`
- `DT{id}_liageINSEE_article-commune.csv`

**Output**

- `data/DT{id}/output2.xml` : le DT avec un premier balisage des communes de localisation
- `data/DT{id}/DT{id}_liageINSEE_localisation-commune-desambiguisation.csv` : liste des éléments `localisation` restant sans élément `commune`.

**Note**. `DT{id}_liageINSEE_localisation-commune-desambiguisation.csv` est transmis aux experts qui y inscrivent manuellement le liage selon une méthode documentée plus bas.


### `add_Insee_Commune.py`

**Description**. Inscrire et renseigner l’attribut `@insee` sur l’élement `commune` de la localisation.

**Input**

- `data/DT{id}/output2.xml`
- `DT{id}_liageINSEE_article-commune.csv`

**Output**

- `data/DT{id}/output3.xml` : le DT avec un premier liage des communes de localisation (inscription du code INSEE en valeur de `commune/@insee`).
- `DT{id}_liageINSEE_localisation-commune.csv` : liste des éléments `commune` pour lesquelles le liage INSEE a échoué (impossibilité d’inscrire le code INSEE en valeur de `@insee`)

**Note**. `DT{id}_liageINSEE_localisation-commune.csv` est transmis aux experts qui y inscrivent manuellement le liage selon une méthode documentée plus bas.


### `Update_Commune_INSEE.py`

**Description**. Inscrire et renseigner l'attribut `@insee` sur les élements `commune` encore non lié à partir du fichier de corrections des experts. Il corrige aussi certaines erreurs contenues dans l'élément `commune`.

**Input**

- `data/DT{id}/output3.xml`
- `DT{id}_liageINSEE_localisation-commune.csv` 

**Output**

- `data/DT{id}/output4.xml`

**Note**. Une colonne `Commentaire` est présente dans le fichier `DT{id}_liageINSEE_localisation-commune.csv`. Il comprend des corrections particulières qui doivent être faites à la main dans `data/DT{id}/output4.xml`.

### `Update_INSEE_Code.py`

**Description**. Inscrire les balises `commune` et les attributs `@insee` dans les éléments `localisation` restant qui ne contiennent pas de balises `commune` à partir du tableau de correction fournit par les experts `DT{id}_liageINSEE_localisation-commune.csv`. Il précise la relation entre le lieu et la commune de localisation qui est de manière automatique `@precision='approximatif'`.

**Input**

- `data/DT{id}/output4.xml`
- `DT{id}_liageINSEE_localisation-commune.csv`

**Output**

- `data/DT{id}/output5.xml`

**Note**. 



## Injection des nouveaux ids (attribués par l’application)
  
- `insert_new-ids.py` : prend en entrée `output6.xml` et le mapping des anciens ids et des nouveaux attribués par l’application, pour injecter ces nouveaux identifiants dans `output7.xml`.


## Contrôles qualité

Il existe deux scripts de contrôle :

### `Testscript.py`

**Description**. Contrôle que les attributs `@insee` sur les élements `commune` sont conformes aux normes décidés au début du projet.

**Input**
- `data/DT{id}/output4.xml` ou `data/DT{id}/output5.xml`

**Output**

- `data/DT{id}/@result_validation_DT{id}.csv` : Liste différentes statistiques et données sur la qualité de nos enrichissement.
  
**Note**. 
Ces résultats servent au suivi de la qualité des données et permettent de réaliser des corrections manuelles en cas de problème. La ligne de résultat doit être reportée dans l'issue 17 sur notre [github](https://github.com/chartes/dico-topo/issues/17). Si il s'agit d'un `data/DT{id}/output4.xml`, il faut mettre en première valeur de la ligne `DT{id}_Etape2` et pour `data/DT{id}/output5.xml`, il faut mettre `DT{id}_Etape3` dans cette première valeur.

### `TestResultatDT.py`

**Description**. 

Compare le fichier souces livré par WordPro et le dernier état de notre travail pour contrôler qu'il n'y ait pas eu d'erreur au cours dans la balise `localisation`.

**Input**
- `DT{id}`
- `data/DT{id}/output6.xml` 

**Output**
- `@DTXX_result.csv`: Il fournit une comparaison chiffrée du DT du départ et de `data/DT{id}/output6.xml`
- `@DTXX_result_commune.csv` : Il renvoie les chaînes de caractères qui sont différentes entre les deux fichiers pour pouvoir les contrôler et les corriger si des erreurs ont été faites au moment de l'injection des différentes balises `commune`

**Note**. 

### `_OUTPUT6_VALDATION_PROCEDURE.pdf`

**Description**. 

Procédure à suivre pour être sûr que toutes les vedettes soient grammaticalement juste, qu'il n'y ait pas d'inversion de caractères, qu'il n'y ait pas de localisation mal segmenté ou pour s'assurer que l'indentation soit correcte dans `data/DT{id}/output6.xml`.

 

### `dico-topo.rng`

**Description**

Les `data/DT{id}/output7.xml` doivent appeller le schéma de contrôle [dico-topo.rng](https://raw.githubusercontent.com/chartes/dico-topo/master/data/dico-topo.rng) pour valider la structure du xml après les différentes interventions réalisées à partir de script ou manuellement.
  
## Exemple de DT73

### Procédure d'enrichissement du code INSEE des communes

- Extraction des probables noms des communes du `DT73.xml` avec le fichier `Recup_ville.xsl`
- Nettoyage de cette première liste sur le logiciel Dataiku (Voir procédure d'enrichissement )
- Normalisation de la liste pour comparaison des chaînes de caractère sur le logiciel Dataiku
- Première comparaison en *exact match* avec le nom des communes INSEE 2011 sur le logiciel Dataiku
- Deuxième comparaison des communes restantes sur les *substring* avec le script `Matchscript.py`
- Troisième comparaison des communes sans match en fuzzy join sur le logiciel Dataiku
- Mise en place d'un tableur pour permettre la correction du texte  (Voir la procédure d'enrichissement détaillé sur Dataiku)
- Correction manuel des communes dont la précision n'est pas High dans le fichier `DT73_liageINSEE_article-commune.csv`
- Ajout de la balise INSEE et de l'attribut commune avec `Update_article_commune.py`
- On obtient ainsi le `DT73_communeINSEE.xml` avec les articles des communes 


### Ajout des balises communes dans les balises localisation

- Utilisation du script `add_commune.py` qui ajoute les balises communes dans les balises localisations selon les règles établies à l'avance et fournit le fichier `output2.xml` et  `DT73_liageINSEE_localisation-commune-desambiguisation.csv`
- Le fichier XML obtenue doit être nettoyer des balises  &lt;tmp>et &lt;/tmp> qui sont ajouter pour pouvoir placer certaines balises communes.
- Le XML récupéré sert de base pour le script suivant `add_Insee_Commune.py` , il récupère le contenu dans la balise commune puis le compare avec la liste des noms de communes et si ça correspond il ajoute un attribut insee avec son code. Il fournit le fichier `output3.xml` et le `DT73_liageINSEE_localisation-commune.csv` pour les balises communes qui n'ont pas de code insee.
- Le tableau `DT73_liageINSEE_localisation-commune.csv` corrigé est ensuite réinjécté par le script  `Update_Commune_INSEE.py` dans `output3.xml`. Il contient un travail manuel de rajout des codes insee donc un travail de vérification manuel du fichier est à faire avant l'injection avec des possibles défauts de segmentaiton, ajout de nouvelles articles communes qui ont pu être manqués sur la première étape, faute de typo ... Une colonne commentaire est prévu à cet effet. Le script sort le fichier `output4.xml`. Il est conseillé d'utiliser le fichier `Testscript.py` sur le fichier `output4.xml` pour corriger des erreurs possibles.
-  Le tableau `DT73_liageINSEE_localisation-commune-desambiguisation.csv` corrigé est réinjécté par le script `Update_INSEE_Code.py` dans le fichier `output4.xml` Il contient un important travail manuel sur les balises localisations sans balise commmune donc il peut y avoir beaucoup de corrections manuel de tout type à réaliser donc il faut prendre son temps de bien regarder les différents commentaires notés par le correcteur. Le script fournit le fichier `output5.xml`
- Le fichier XML obtenue doit être nettoyer des balises  &lt;tmp>et &lt;/tmp> qui sont ajouter pour pouvoir placer certaines balises communes dans les balises localisations non-stéréotypé.
- Il est conseillé d'utiliser le fichier `Testscript.py` sur le fichier `output5.xml` pour corriger de possibles erreurs injectées à ce moment.
- Il faut ensuite comparer le fichier XML du départ `DT73.xml` et `output5.xml` avec `TestResultatDT.py` pour corriger les dernières erreurs possibles. Le script fournit les csv `@DT73_result.csv` pour obtenir une vision globale chiffré et le fichier `@DT73_result_commune.csv` pour corriger les dernières manuellement enregistré sous le nom `output6.xml`
- Une dernière étape est de contrôler avec des xpaths contenues dans le fichier `_OUTPUT6_VALDATION_PROCEDURE.pdf` pour être sûr que le fichier `output6.xml` soit corrigé.

  

### Procédure d'enrichissement sur Dataiku : Exemple du département 73 (cf. DT73.zip)

1. Ajout du fichier CSV DT73 des communes extraites depuis le fichier DT73.xml 
1. Mise en ordres des données avec suppression des espaces vides, alignement des cases et création d'une colonne qui contient une version normalisée de la commune
1. Ajout du fichier des communes 2011 avec le code INSEE, suppression des communes qui ne sont pas du département, nettoyage des colonnes innutiles et normalisation du nom des communes
1. Fusion des deux jeux de données en fonction des noms normalisés et ajout d'une colonne contenant le code INSEE et du nom normalisé dans le fichier DT73 
1. Séparation en deux du fichier obtenu avec d'un côté les communes avec un code INSEE et le reste de l'autre
1. Extraction des communes sans code INSEE dans un fichier CSV qui sert de fichier d'entréer pour `Matchscript.py` pour trouver de nouvelle correspondance. Le script nous fournit un nouveau fichier de reste.
1. Le fichier csv est réutilisé dans dataiku pour un fuzzyjoin avec le fichier des communes de 2011 nettoyé et obtention du dernier fichier. 
1. Création du fichier de correction DT73.ods avec l'ajout d'un niveau de risque. High pour ceux issue de la première fusion de dataiku, Medium pour ceux de la deuxième issue de `Matchscript.py` et de Low pour ceux issue du fuzzyjoin

L'ensemble de la procédure est la même pour chaque département. Il suffit à chaque fois de copier la procédure et de mettre le numéro du département correspondant. 

