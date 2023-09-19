```
Librairies nécessaires: 

conda create --name pouille python=3.9.7
conda activate pouille
pip install pandas
pip install python-Levenshtein
pip install thefuzz
pip install difflib

jupyter notebook

Pipeline de correspondance et d'enrichissement de données:

Étape 1: Lien entre le pouillé et le référentiel INSEE

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
```