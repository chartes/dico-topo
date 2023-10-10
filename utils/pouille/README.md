Pipeline de liage
===

1. Liage Pouillé / Code Insee
2. Liage Pouillé / DT

À chacune de ces étapes correspond des notebooks :

1. `linking.ipynb` + `annotate.ipynb`
2. `reinjection.ipynb`


Création de l’environnement avec Conda : 

```
conda create --name pouille python=3.9.7
conda activate pouille
pip install pandas
pip install python-Levenshtein
pip install thefuzz
pip install unidecode
pip install odfpy
# pip install difflib

jupyter notebook
```

### 1. Liage PO/code INSEE

- script : `linking.ipynb`
- inputs : `PO_tn.xml` + `main_insee_commune.csv` + `departements-region.csv`
- output : `liage_PO7.csv` (le tableau à valider par OC)

### 2. Validation manuelle des liages

- opérateur : OC
- input : `liage_PO7.ods` avec les couleurs
- ouput : `liage_PO7.ods` (corrigé)

### 3. Injection des codes INSEE dans le XML du PO

- script : `annotate.ipynb`
- inputs : `PO_tn.xml` + `liage_PO7.ods`
- outputs: `PO_t9_modified.xml` + `liage_PO7.csv` (export CSV de l’ODS)

TODO: diagnostic des articles non liés (objectif de couverture du liage de 95%).

### 4. Liage PO/DT

- script : `reinjection.ipynb` + `liage_po9.csv` (l’export CSV de l’étape 3)
- inputs : `liage_po9.csv` + tous les `DT/ouput7.xml`
- output : `po9_dicotopo.csv` (tableau à valider des liages PO/DT)

### 5. Validation manuelle des liages PO/DT

- opérateur : OC
- input : `po9_dicotopo.csv`
- output: `po9_dicotopo.csv` (corrigé)

### 6. Injection des ID DT dans le XML du PO

- script : `reinjection.ipynb` (cf section "Réinsertion dans le fichier XML")
- inputs : `po9_dicotopo.csv` (corrigé) + `PO_t9_modified.xml`
- output : `po9_dicotopo.xml` le PO avec tous les liages

TODO:

- diagnostic des articles non liés
- nettoyer le XML (notamment les attributs vides)



## Étape 1: Lien entre le pouillé et le référentiel INSEE

Input:

Pouillé au format XML
Référentiel INSEE
Traitement:

Lire le pouillé au format XML.
Utiliser un script de correspondance exacte pour identifier les correspondances exactes entre les données du pouillé et le référentiel INSEE.
Appliquer un algorithme de correspondance floue (fuzzy matching) pour les correspondances incertaines.
Créer un fichier CSV contenant les résultats avec les colonnes suivantes :
Correspondances exactes
Correspondances floues
Non-correspondances
Correction manuelle par Olivier:

Olivier examine et corrige manuellement les correspondances au besoin.
Fichier ODS corrigé:

Le fichier ODS est mis à jour avec les correspondances corrigées.
Étape 2: Lien entre le pouillé et INSEE finalisé

Input:

ID Dicotopo
Ancienne référence Dicotopo
Fichier ODS corrigé
Traitement:

Lire les données d'ID Dicotopo et d'ancienne référence Dicotopo.
Utiliser un script de correspondance exacte pour identifier les correspondances exactes entre ces données et le fichier ODS corrigé.
Appliquer un algorithme de correspondance floue (fuzzy matching) pour les correspondances incertaines.
Créer un fichier CSV contenant les résultats avec les colonnes suivantes :
Correspondances exactes
Correspondances floues
Non-correspondances
Correction manuelle par Olivier:

Olivier examine et corrige manuellement les correspondances au besoin.
Fichier ODS corrigé:

Le fichier ODS est mis à jour avec les correspondances corrigées.
Étape 3: Lien entre le pouillé et Dicotopo finalisé

Traitement:

Réinjecter les correspondances finalisées dans le fichier XML du pouillé en ajoutant une balise <insee> pour les informations INSEE.
Réinjecter les correspondances finalisées dans le fichier XML du pouillé en ajoutant une balise <dicotopo> pour les informations Dicotopo.
Finalité:

Le fichier XML est enrichi avec les informations INSEE et Dicotopo.
