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

**Description**. Pour un DT, lister les noms de communes potentielles ainsi que leur canton de localisation.

**Usage**

```
DT{id}$ xsltproc -o DT{id}-Recup_ville.csv ../../utils/Recup_ville.xsl DT{id}.xml
```

**Output** : TSV sur sortie standard. 3 colonnes :

- `ID` : identifiant de l’article (de type commune) – ex. `DT02-00196`
- `NomCommune` : vedette de l’article – ex. `Aulnois,`
- `NomCanton` : label du canton de localisation – ex. `canton de Laon` (utile pour désambiguiser l’identification d’une commune)

**Note**. Ce TSV est importé dans Dataiku pour le liage INSEE (voir *Workflow* plus bas).


### `Matchscript.py`

**Description**. Pour les vedettes des articles de type commune non liées dans Dataiku, sortir des tableaux facilitant le liage manuel, selon différents cas.

**Input**

- `Rest_prepared.csv` : export Dataiku de la liste des vedettes des articles de type commune pour lesquelles le liage a échoué.

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


## Contrôles qualité

Il existe deux scripts de contrôle :


### `Testscript.py`

**Description**. Contrôle que les attributs `@insee` sur les élements `commune` sont conformes aux normes décidés au début du projet.

**Input**
- `data/DT{id}/output4.xml` ou `data/DT{id}/output5.xml`

**Output**

- `data/DT{id}/@result_validation_DT{id}.csv` : statistiques sur la qualité des enrichissements.
  
**Note**. 
Ces résultats servent au suivi de la qualité des données et permettent de réaliser des corrections manuelles en cas de problème. La ligne de résultat doit être reportée dans l'issue 17 sur notre [github](https://github.com/chartes/dico-topo/issues/17). S’il s'agit d'un `data/DT{id}/output4.xml`, il faut mettre en première valeur de la ligne `DT{id}_Etape2` et pour `data/DT{id}/output5.xml`, il faut mettre `DT{id}_Etape3` dans cette première valeur.


### `TestResultatDT.py`

**Description**. 

Compare le fichier souces livré par WordPro et le dernier état de notre travail pour contrôler qu'il n'y ait pas eu d'erreur au cours dans la balise `localisation`.

**Input**
- `DT{id}`
- `data/DT{id}/output6.xml` 

**Output**
- `@DTXX_result.csv`: Il fournit une comparaison chiffrée du DT du départ et de `data/DT{id}/output6.xml`
- `@DTXX_result_commune.csv` : Il renvoie les chaînes de caractères qui sont différentes entre les deux fichiers pour pouvoir les contrôler et les corriger si des erreurs ont été faites au moment de l'injection des différentes balises `commune`


### `_OUTPUT6_VALDATION_PROCEDURE.pdf`

**Description**. 

Procédure à suivre pour être sûr que toutes les vedettes soient grammaticalement juste, qu'il n'y ait pas d'inversion de caractères, qu'il n'y ait pas de localisation mal segmenté ou pour s'assurer que l'indentation soit correcte dans `data/DT{id}/output6.xml`.
 

### `dico-topo.rng`

**Description**

Les `data/DT{id}/output7.xml` doivent appeller le schéma de contrôle [dico-topo.rng](https://raw.githubusercontent.com/chartes/dico-topo/master/data/dico-topo.rng) pour valider la structure du xml après les différentes interventions réalisées à partir de script ou manuellement.

  
# Exemple de DT37

## A. Liage INSEE

### 1. Extraction des noms de communes potentielles

Extraction des probables noms des communes du `DT37.xml` avec le fichier `Recup_ville.xsl`

```
xsltproc -o DT37-Recup_ville.csv ../../utils/Recup_ville.xsl DT37.xml
```

### 2. Dataiku, Liage

Ouvrir le *Worflow* [Dataiku](https://www.dataiku.com/product/get-started/) [DT_INSEELINKING_DATAIKUWORKLOW.zip](https://github.com/chartes/dico-topo/blob/enrichissement_xml_dt/utils/DT_INSEELINKING_DATAIKUWORKLOW.zip) et le cloner `data/DT37/DT37_DATAIKUWORKLOW`

#### Charger `DT37-Recup_ville.csv`

- separateur : `\t`
- première ligne comme en-tête

#### Normaliser les noms de communes

Dans le Worflow, utiliser la *Prepare recipe* `compute_DTid_prepared`, en veillant à bien mettre à jour l’id du DT dans les règles.

**NB**. Appeler le bon département dans la *Prepare recipe* `compute_comsimp2011_prepared`.


Outputs :

- `CommuneOK` : les liages corrects (`high`), à faire valider tout de même par OC et SN.
- `Rest_prepared` : liste des communes potentielles non liées. Exporter en TSV (`Rest_prepared.csv`), pour traitement avec `Matchscript.py`.

#### Sortir de Dataiku pour traiter `Rest_prepared`

```
python Matchscript.py
```
**NB**. Mettre à jour la variable `dep`.


Outputs :

- `result2.csv`: la commune potentielle, suivie de la liste des propositions de liages (code INSEE + NCCENR)- `result3.csv`: idem
- `rest3.csv`: les communes non liées

#### Dataiku, traiter `rest3.csv`- Dans le Worflow Dataiku [DTid.zip](https://github.com/chartes/dico-topo/blob/enrichissement_xml_dt/utils/DTid.zip), charger `rest3` et lancer la *Prepare recipe* `compute_rest3_prepared` (=*fuzzy join* sur les noms non liés).
- Exporter `rest3prepared.csv`.### 3. Fusionner les outputs pour validation OC/SNDans `DTid.ods` avec l'ajout d'un niveau de probabilité du liage :

- `high`: bleu – `CommuneOk.csv` (Dataiku)
- `medium`: orange - `result2.csv` et `result3.csv` (`Matchscript.py`)
- `low`: rouge – `rest3prepared` (Dataiku)


Récupérer le fichier validé, le convertir en TSV pour annoter les sources XML.


## B. Annotation des sources XML

### 1. Ajout en `localisation` de la balise `commune` pour lier le lieu à sa commune de rattachement

#### Injecter les éléments `insee` et `@type='commune'`

**NB**. Éditer `Update_article_commune.py` pour appeler le bon DT… (TODO, passer en arg)

```
utils$ python3 Update_article_commune.py
```

#### Ajouter les éléments `commune` dans `localisation`

```
DT37$ rm DT37.xml
DT37$ mv DT37_CommuneINSEE.xml DT37.xml
```

Push la nouvelle version de DT37

**NB**. Éditer variable `dep` in `add_commune.py` pour appeler le bon DT… (TODO, passer en arg)

des *requirements*…

```
$ pip3 install Unidecode
$ pip3 install beautifulsoup4
```

```
utils$ python3 add_commune.py
```

On obtient :

- `data/DT37/output2.xml`. Y supprimer les balises `tmp`.
- `DT37_liageINSEE_localisation-commune-desambiguisation.csv` : convertir en ODS envoyer à OC/SN pour validation


#### Ajout de `@insee` dans les éléments `commune` de `localisation`

**NB**. Éditer variable `dep` in `add_commune.py` pour appeler le bon DT… (TODO, passer en arg)

```
utils$ python3 Add_Insee_Communes.py
```

On obtient :

- `data/DT37/output3.xml`
- `DT37_liageINSEE_localisation-commune.csv` : convertir en ODS envoyer à OC/SN pour validation


#### Injection dans le XML des liages résiduels

A. Injecter dans le fichier output3.xml les liages inscrits dans `DT37_liageINSEE_localisation-commune.ods`

- Lire la colonne commentaire et faire les corrections manuelles attendues.
- Exporter en TSV `DT37_liageINSEE_localisation-commune.ods` (sep = `\t`)
- **NB**. Éditer variable `dep` in `Update_Commune_INSEE.py` pour appeler le bon DT… (TODO, passer en arg)

```
utils$ python3 Update_Commune_INSEE.py
```

Les codes insee sont injectés dans `definition/localisation/commune/@insee` et le nom de la commune est éventuellement corrigé (`definition/localisation/commune`).

**NB**. Penser à tester la sortie `output4.xml` avec `Testscript.py` (cf plus bas, documentation des tests).


B. Injecter dans le fichier output4.xml les ultimes liages inscrits dans `DT37_liageINSEE_localisation-commune-desambiguisation.csv`

- Exporter en TSV `DT37_liageINSEE_localisation-commune-desambiguisation.ods` (sep = `\t`)
- **NB**. Éditer variable `dep` in `Update_INSEE_Code.py` pour appeler le bon DT… (TODO, passer en arg)

```
utils$ python3 Update_INSEE_Code.py
```

Supprimer les balises `tmp` inscrites dans la sortie `output5.xml`.


#### Validation de `output5.xml`

##### `TestScript.py`

Des stats sur le DT: pourcentage liage, code INSEE inconnus, etc.

```
utils % python3 TestScript.py 37 ../data/DT37/output5.xml
```

output: `utils/out/@result_validation_DT37.csv`



##### `TestResultatDT.py`

Diff entre la version première du DT et l’output testé, par ex.

```
utils % python3 TestResultatDT.py 37 ../data/DT37/DT37.xml ../data/DT37/output5.xml
```

output:

- `utils/out/@DT37_result.csv` : des stats camparées (nombre d’articles et de liages, etc.)- `utils/out/@DT37_result_commune.csv` : liste des localisations modifiées pour vérification.


Enregistrer après les vérification et éventuelles corrections manuelles `output6.xml`.

[Procédure de validation de output6](https://github.com/chartes/dico-topo/blob/enrichissement_xml_dt/data/_OUTPUT6_VALDATION_PROCEDURE.md)



#### Injection des nouveaux ids (attribués par l’application)
  
- `insert_new-ids.py` : prend en entrée `output6.xml` et le mapping des anciens ids et des nouveaux attribués par l’application, pour injecter ces nouveaux identifiants dans `output7.xml`.


## Injection des nouveaux ids (attribués par l’application)
  
- `insert_new-ids.py` : prend en entrée `output6.xml` et le mapping des anciens ids et des nouveaux attribués par l’application, pour injecter ces nouveaux identifiants dans `output7.xml`.


