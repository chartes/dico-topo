"""
match.py - Appariement des toponymes avec le Code officiel géographique (COG)

Ce script associe les toponymes normalisés du dictionnaire topographique
aux codes INSEE du COG 2011 via trois stratégies d'appariement progressives :
1. Correspondance exacte
2. Correspondance approximative par tokens/préfixes
3. Correspondance par distance d'édition (Levenshtein)

Usage:
    python match.py [input_file] [cog_file] [output_file]

Arguments:
    input_file  : Fichier Excel avec colonnes 'vedette', 'localisation', 'category', 'key_commune'
    cog_file    : Fichier TSV/CSV du COG avec colonnes 'insee_code', 'NCCENR', 'ARTMIN'
    output_file : Fichier Excel de sortie avec codes INSEE et type de match
"""

import pandas as pd
import re
import unicodedata
import sys
from pathlib import Path

# ==================== Configuration ====================

# Chemins par défaut (peuvent être surchargés par arguments)
DEFAULT_DT_PATH = "2_DT03_parsed.xlsx" 
DEFAULT_INSEE_PATH = "4.2_DT03_COG_2011.tsv"
DEFAULT_OUT_PATH = "5_DT03_matched.xlsx"

# Paramètres d'appariement
MAX_LEVENSHTEIN_DISTANCE = 1  # Distance d'édition maximale pour fuzzy matching


# ==================== Fonctions utilitaires ====================

def levenshtein(a: str, b: str) -> int:
    """
    Calcule la distance de Levenshtein (distance d'édition) entre deux chaînes.

    Args:
        a, b: Chaînes à comparer

    Returns:
        Nombre minimal d'opérations (insertion, suppression, substitution)
        nécessaires pour transformer a en b
    """
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    a, b = a.lower(), b.lower()
    m, n = len(a), len(b)
    dp = list(range(n + 1))

    for i in range(1, m + 1):
        prev = dp[0]
        dp[0] = i
        for j in range(1, n + 1):
            cur = dp[j]
            cost = 0 if a[i - 1] == b[j - 1] else 1
            dp[j] = min(
                dp[j] + 1,  # deletion
                dp[j - 1] + 1,  # insertion
                prev + cost,  # substitution
            )
            prev = cur
    return dp[n]


def strip_leading_article(s: str | None) -> str | None:
    """
    Supprime les articles français en début de chaîne.

    Gère les cas : "Le", "La", "Les", "L'", "(Le)", etc.

    Args:
        s: Chaîne à traiter

    Returns:
        Chaîne sans article initial, ou None si vide
    """
    if not isinstance(s, str):
        return None
    s = s.strip()
    if not s:
        return None

    # Supprimer les parenthèses autour de l'article : "(Le) Ham" -> "Le Ham"
    s = re.sub(
        r"\(([Ll]e)\)|\(([Ll]a)\)|\(([Ll]es)\)|\(([Ll][''])\)",
        lambda m: m.group(0).strip("()"),
        s
    )
    s = s.strip()

    # Supprimer l'article initial
    ARTICLE_LEADING_RE = re.compile(r"^(l['']|\ble\b|\bla\b|\bles\b)\s+", re.IGNORECASE)
    s = ARTICLE_LEADING_RE.sub("", s).strip()

    return s or None


def norm(s: str | None) -> str | None:
    """
    Normalisation typographique d'une chaîne.

    Opérations :
    - Conversion en minuscules
    - Suppression des accents (décomposition NFD)
    - Normalisation des tirets en espaces
    - Normalisation des apostrophes
    - Suppression des espaces multiples

    Args:
        s: Chaîne à normaliser

    Returns:
        Chaîne normalisée, ou None si vide
    """
    if not isinstance(s, str):
        return None
    s = s.strip()
    if not s:
        return None

    # Normaliser les apostrophes
    s = s.replace("'", "'").lower()

    # Convertir les tirets en espaces
    s = re.sub(r"[-‐‑‒–—]", " ", s)

    # Supprimer les accents via décomposition Unicode NFD
    s = "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )

    # Réduire les espaces multiples
    s = re.sub(r"\s+", " ", s).strip()

    return s or None


def norm_without_article(s: str | None) -> str | None:
    """
    Normalisation complète : suppression article + normalisation typographique.

    Args:
        s: Chaîne à normaliser

    Returns:
        Chaîne normalisée sans article, ou None si vide
    """
    base = strip_leading_article(s)
    if base is None:
        return None
    return norm(base)


# ==================== Construction des clés INSEE ====================

def insee_key(row: pd.Series) -> str | None:
    """
    Construit une clé normalisée à partir de ARTMIN + NCCENR du COG.

    Exemple :
        ARTMIN="(La)", NCCENR="Flèche" -> "fleche"

    Args:
        row: Ligne du DataFrame COG avec colonnes ARTMIN, NCCENR

    Returns:
        Clé normalisée pour appariement
    """
    name_raw = row.get("NCCENR")
    art_raw = row.get("ARTMIN")

    name_raw = name_raw if isinstance(name_raw, str) else ""
    art_raw = art_raw if isinstance(art_raw, str) else ""

    name_raw = name_raw.strip()
    art_raw = art_raw.strip()

    if not name_raw and not art_raw:
        return None

    # "(La)" -> "La"
    art_raw = re.sub(r"[()]", "", art_raw).strip()

    # Combiner article + nom
    full = f"{art_raw} {name_raw}".strip()

    # Normaliser (suppression article incluse)
    return norm_without_article(full)


# ==================== Construction des clés dictionnaire ====================

def key_from_vedette(v: str | None) -> str | None:
    """
    Extrait et normalise une clé depuis la vedette d'un article de type commune.

    Gère les cas :
    - Article à la fin : "Bazoche-Montpinçon (La)" -> "bazoche montpincon"
    - Alias : "Laval, alias Lavallis" -> "laval"
    - Qualificateurs : "Saint-Jean (près de Laval)" -> "saint jean"

    Args:
        v: Vedette de l'article

    Returns:
        Clé normalisée
    """
    if not isinstance(v, str):
        return None
    v = v.strip()
    if not v:
        return None

    # Supprimer les alias
    v = v.split(", alias", 1)[0].strip()

    # Gérer l'article à la fin : "Bazoche (La)" -> "La Bazoche"
    ARTICLE_RE = re.compile(r"^(.*)\s+\((l[ea']|les)\)$", re.IGNORECASE)
    m = ARTICLE_RE.match(v)
    if m:
        name = m.group(1).strip()
        art = m.group(2).lower().replace("'", "")
        v = f"{art} {name}"
    else:
        # Supprimer les qualificateurs entre parenthèses
        v = re.sub(r"\s*\([^)]*\)$", "", v).strip()

    # Normaliser
    return norm_without_article(v)


def key_from_localisation(loc: str | None) -> str | None:
    """
    Extrait et normalise le nom de commune depuis le champ localisation.

    Détecte les patterns : "commune de X", "du X", "de la X", "d'X"

    Exemples :
    - "commune de Bazouges" -> "bazouges"
    - "hameau du Ham" -> "ham"
    - "de la Flèche" -> "fleche"

    Args:
        loc: Texte de localisation

    Returns:
        Clé normalisée de la première commune mentionnée
    """
    if not isinstance(loc, str):
        return None
    loc = loc.strip()
    if not loc:
        return None

    # Pattern pour capturer : "de/du/de la/des X" ou "d'X"
    LOC_CONN_RE = re.compile(
        r"(de la|du|des|de)\s+(.+)|d[''](.+)",
        re.IGNORECASE,
    )

    m = LOC_CONN_RE.search(loc)
    if not m:
        return None

    # Extraire le nom capturé
    tail = (m.group(2) or m.group(3) or "").strip()
    if not tail:
        return None

    # Arrêter aux séparateurs : "|", ",", " et "
    tail = re.split(r"\s*\|\s*|,|\set\s+", tail, maxsplit=1)[0].strip()

    # Supprimer les qualificateurs entre parenthèses
    tail = re.sub(r"\s*\([^)]*\)$", "", tail).strip()

    # Normaliser
    return norm_without_article(tail)


# ==================== Stratégies d'appariement ====================

def exact_match(df: pd.DataFrame, insee: pd.DataFrame) -> pd.DataFrame:
    """
    Étape 1 : Correspondance exacte par jointure sur key_commune.

    Gère les cas avec plusieurs candidats (homonymes) en retournant
    tous les matches possibles au format JSON.

    Args:
        df: DataFrame du dictionnaire avec colonne key_commune
        insee: DataFrame COG avec colonnes insee_code, NCCENR, NCCENR_norm, key_commune

    Returns:
        DataFrame avec codes INSEE pour les correspondances exactes
    """
    import json

    # Joindre avec le COG
    result = df.merge(
        insee[["insee_code", "NCCENR", "NCCENR_norm", "key_commune"]],
        how="left",
        on="key_commune",
    )

    # Identifier les doublons (homonymes)
    duplicates = result[result.duplicated(subset=['id'], keep=False)]

    if len(duplicates) > 0:
        # Grouper les homonymes et créer des listes JSON
        grouped = duplicates.groupby('id').agg({
            'insee_code': lambda x: json.dumps(list(x.dropna())),
            'NCCENR': lambda x: json.dumps(list(x.dropna())),
            'NCCENR_norm': lambda x: json.dumps(list(x.dropna()))
        }).reset_index()

        # Marquer comme exact_multiple
        grouped['match_type'] = 'exact_multiple'
        grouped['match_count'] = grouped['insee_code'].apply(lambda x: len(json.loads(x)))

        # Garder les autres colonnes du DataFrame original
        other_cols = [col for col in df.columns if
                      col not in ['insee_code', 'NCCENR', 'NCCENR_norm', 'match_type', 'match_count']]
        grouped = grouped.merge(df[other_cols + ['id']], on='id', how='left')

        # Supprimer les doublons du résultat principal
        result = result[~result['id'].isin(grouped['id'])]

        # Ajouter les groupes avec match_count
        result = pd.concat([result, grouped], ignore_index=True)

    # Marquer les matches uniques comme exact
    result["match_type"] = result.get("match_type", None)
    mask_single_exact = result["insee_code"].notna() & result["match_type"].isna()
    result.loc[mask_single_exact, "match_type"] = "exact"

    return result


def fuzzy_match_prefix(
        result: pd.DataFrame,
        insee_key_to_code: pd.Series,
        insee_code_to_nccenr: pd.Series,
        insee_code_to_nccenr_norm: pd.Series
) -> pd.DataFrame:
    """
    Étape 2 : Correspondance approximative par tokens/préfixes.

    Stratégie :
    - Même premier token requis (sécurité contre faux positifs)
    - Clé du dictionnaire est un token du COG OU un préfixe du COG

    Retourne tous les candidats en JSON si plusieurs matches trouvés.

    Exemple :
    - "saint jean" match "saint jean de la motte" (préfixe)
    - "laval" match "laval" (token unique)

    Args:
        result: DataFrame avec colonnes key_commune, insee_code
        insee_key_to_code: Mapping clé normalisée -> code INSEE
        insee_code_to_nccenr: Mapping code INSEE -> nom officiel
        insee_code_to_nccenr_norm: Mapping code INSEE -> nom normalisé

    Returns:
        DataFrame enrichi avec correspondances fuzzy par tokens
    """
    insee_keys = insee_key_to_code.index.tolist()

    def fuzzy_match_insee_prefix(key: str | None) -> dict | None:
        """
        Recherche par tokens/préfixes avec contrainte premier token identique.
        Retourne tous les candidats si plusieurs matches.
        """
        if not isinstance(key, str) or not key:
            return None

        key_tokens = key.split()
        first_key = key_tokens[0] if key_tokens else ""

        candidates = []

        for k in insee_keys:
            if key == k:  # Déjà traité en exact match
                continue

            tokens = k.split()
            if not tokens:
                continue

            first_k = tokens[0]

            # Contrainte : même premier token
            if first_k != first_key:
                continue

            # Vérifier si key est un token OU un préfixe de k
            if key in tokens or k.startswith(key + " "):
                candidates.append({
                    'insee_code': insee_key_to_code[k],
                    'NCCENR': insee_code_to_nccenr.get(insee_key_to_code[k]),
                    'NCCENR_norm': insee_code_to_nccenr_norm.get(insee_key_to_code[k]),
                    'key_matched': k,
                    'length': len(k)
                })

        if not candidates:
            return None

        # Trier par longueur (préférer le plus long = le plus spécifique)
        candidates.sort(key=lambda x: x['length'], reverse=True)

        if len(candidates) == 1:
            # Un seul candidat
            return {
                'insee_code': candidates[0]['insee_code'],
                'NCCENR': candidates[0]['NCCENR'],
                'NCCENR_norm': candidates[0]['NCCENR_norm'],
                'multiple': False
            }
        else:
            # Plusieurs candidats
            return {
                'insee_code': [c['insee_code'] for c in candidates],
                'NCCENR': [c['NCCENR'] for c in candidates],
                'NCCENR_norm': [c['NCCENR_norm'] for c in candidates],
                'multiple': True,
                'count': len(candidates)
            }

    # Appliquer sur les entrées non matchées
    mask_missing = result["insee_code"].isna() & result["key_commune"].notna()

    # Stocker les résultats
    matches = result.loc[mask_missing, "key_commune"].map(fuzzy_match_insee_prefix)

    # Séparer les matches simples des multiples
    import json

    for idx, match in matches.items():
        if match is None:
            continue

        if match.get('multiple', False):
            # Plusieurs candidats : stocker en JSON string
            result.loc[idx, 'insee_code'] = json.dumps(match['insee_code'])
            result.loc[idx, 'NCCENR'] = json.dumps(match['NCCENR'])
            result.loc[idx, 'NCCENR_norm'] = json.dumps(match['NCCENR_norm'])
            result.loc[idx, 'match_type'] = 'fuzzy_multiple'
            result.loc[idx, 'match_count'] = match['count']
        else:
            # Un seul candidat
            result.loc[idx, 'insee_code'] = match['insee_code']
            result.loc[idx, 'NCCENR'] = match['NCCENR']
            result.loc[idx, 'NCCENR_norm'] = match['NCCENR_norm']
            result.loc[idx, 'match_type'] = 'fuzzy'

    return result


def fuzzy_match_edit_distance(
        result: pd.DataFrame,
        insee_key_to_code: pd.Series,
        insee_code_to_nccenr: pd.Series,
        insee_code_to_nccenr_norm: pd.Series,
        max_dist: int = MAX_LEVENSHTEIN_DISTANCE
) -> pd.DataFrame:
    """
    Étape 3 : Correspondance par distance de Levenshtein.

    Stratégie :
    - Même premier token requis (sécurité)
    - Distance d'édition <= max_dist (défaut : 1)
    - Capture les variantes orthographiques mineures

    Exemple :
    - "evrone" match "evron" (distance 1)
    - "st jean" match "saint jean" (distance > 1, rejeté)

    Args:
        result: DataFrame avec colonnes key_commune, insee_code
        insee_key_to_code: Mapping clé normalisée -> code INSEE
        insee_code_to_nccenr: Mapping code INSEE -> nom officiel
        insee_code_to_nccenr_norm: Mapping code INSEE -> nom normalisé
        max_dist: Distance de Levenshtein maximale autorisée

    Returns:
        DataFrame enrichi avec correspondances fuzzy par distance d'édition
    """
    insee_keys = insee_key_to_code.index.tolist()

    def fuzzy_match_insee_edit(key: str | None) -> str | None:
        """
        Recherche par distance d'édition avec contrainte premier token identique.
        """
        if not isinstance(key, str) or not key:
            return None

        key_tokens = key.split()
        first_key = key_tokens[0] if key_tokens else ""

        best_code = None
        best_dist = max_dist + 1

        for k in insee_keys:
            tokens_k = k.split()
            first_k = tokens_k[0] if tokens_k else ""

            # Contrainte : même premier token
            if first_k != first_key:
                continue

            d = levenshtein(key, k)
            if d < best_dist:
                best_dist = d
                best_code = insee_key_to_code[k]

        return best_code if best_dist <= max_dist else None

    # Appliquer sur les entrées encore non matchées
    mask_still_missing = result["insee_code"].isna() & result["key_commune"].notna()

    result.loc[mask_still_missing, "insee_code"] = result.loc[
        mask_still_missing, "key_commune"
    ].map(fuzzy_match_insee_edit)

    # Marquer comme fuzzy et remplir les noms
    mask_edit_ok = mask_still_missing & result["insee_code"].notna()
    result.loc[mask_edit_ok, "match_type"] = "fuzzy"
    result.loc[mask_edit_ok, "NCCENR"] = result.loc[
        mask_edit_ok, "insee_code"
    ].map(insee_code_to_nccenr)
    result.loc[mask_edit_ok, "NCCENR_norm"] = result.loc[
        mask_edit_ok, "insee_code"
    ].map(insee_code_to_nccenr_norm)

    return result


# ==================== Pipeline principal ====================

def process_matching(dt_path: str, insee_path: str, out_path: str):
    """
    Pipeline complet d'appariement des toponymes avec le COG.

    Args:
        dt_path: Chemin du fichier dictionnaire (Excel)
        insee_path: Chemin du fichier COG (TSV/CSV)
        out_path: Chemin du fichier de sortie (Excel)
    """
    print("=" * 60)
    print("MATCH.PY - Appariement avec le COG")
    print("=" * 60)

    # ---------- 1. Chargement des données ----------
    print("\n[1/7] Chargement des données...")
    df = pd.read_excel(dt_path)
    print(f"  • Dictionnaire : {len(df)} articles chargés")

    # Détecter le séparateur et l'encodage du fichier COG
    sep = "\t" if insee_path.endswith(".tsv") else ","

    # Si c'est un fichier Excel, utiliser read_excel
    if insee_path.endswith(('.xlsx', '.xls')):
        insee = pd.read_excel(insee_path, dtype=str)
    else:
        # Pour CSV/TSV, tenter différents encodages
        try:
            insee = pd.read_csv(insee_path, sep=sep, dtype=str, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                insee = pd.read_csv(insee_path, sep=sep, dtype=str, encoding='latin-1')
            except UnicodeDecodeError:
                insee = pd.read_csv(insee_path, sep=sep, dtype=str, encoding='cp1252')

    print(f"  • COG : {len(insee)} communes chargées")

    # ---------- 2. Construction des clés INSEE ----------
    print("\n[2/7] Construction des clés INSEE...")
    insee["key_commune"] = insee.apply(insee_key, axis=1)
    insee["NCCENR_norm"] = insee["NCCENR"].apply(norm_without_article)
    print(f"  • {insee['key_commune'].notna().sum()} clés INSEE générées")

    # ---------- 3. Construction des clés dictionnaire ----------
    print("\n[3/7] Construction des clés dictionnaire...")

    # Vérifier si la clé existe déjà (commune_norm ou key_commune)
    if "commune_norm" in df.columns:
        print("  ℹ️  Utilisation de la colonne 'commune_norm' existante")
        df["key_commune"] = df["commune_norm"]
    elif "key_commune" in df.columns:
        print("  ℹ️  Utilisation de la colonne 'key_commune' existante")
        # key_commune existe déjà, ne rien faire
    else:
        print("  ⚙️  Génération des clés depuis vedette/localisation")
        df["key_commune"] = None

        # Vérifier si colonne 'category' ou 'is_commune' existe
        if "category" in df.columns:
            # Ancien format avec category
            is_commune = df["category"] == "commune"
            is_loc = df["category"] == "commune de localisation"
            is_unknown = df["category"] == "category unknown"

            df.loc[is_commune, "key_commune"] = df.loc[is_commune, "vedette"].map(
                key_from_vedette
            )

            df.loc[is_loc, "key_commune"] = df.loc[is_loc, "localisation"].map(
                key_from_localisation
            )

            df.loc[is_unknown, "key_commune"] = df.loc[is_unknown, "vedette"].map(
                key_from_vedette
            )

            # Fallback : utiliser localisation brute si pattern non détecté
            mask_loc_plain = (
                    (df["category"] == "commune de localisation")
                    & df["key_commune"].isna()
                    & df["localisation"].notna()
            )
            df.loc[mask_loc_plain, "key_commune"] = df.loc[mask_loc_plain, "localisation"].map(
                norm_without_article
            )

        elif "is_commune" in df.columns:
            # Nouveau format avec is_commune (boolean)
            is_commune = df["is_commune"] == True
            is_not_commune = df["is_commune"] == False

            # Pour les communes : utiliser la vedette
            df.loc[is_commune, "key_commune"] = df.loc[is_commune, "vedette"].map(
                key_from_vedette
            )

            # Pour les non-communes : utiliser la localisation
            df.loc[is_not_commune, "key_commune"] = df.loc[is_not_commune, "localisation"].map(
                key_from_localisation
            )

            # Fallback : utiliser localisation brute si pattern non détecté
            mask_loc_plain = (
                    (df["is_commune"] == False)
                    & df["key_commune"].isna()
                    & df["localisation"].notna()
            )
            df.loc[mask_loc_plain, "key_commune"] = df.loc[mask_loc_plain, "localisation"].map(
                norm_without_article
            )

        else:
            # Aucune colonne de classification trouvée, utiliser vedette par défaut
            print("  ⚠️  Attention : Aucune colonne 'category' ou 'is_commune' trouvée")
            print("      Utilisation de la vedette pour toutes les entrées")
            df["key_commune"] = df["vedette"].map(key_from_vedette)

    print(f"  • {df['key_commune'].notna().sum()} clés dictionnaire générées")

    # ---------- 4. Étape 1 : Correspondance exacte ----------
    print("\n[4/7] Étape 1 : Correspondance exacte...")
    result = exact_match(df, insee)

    # Initialiser match_count pour toutes les lignes
    if 'match_count' not in result.columns:
        result['match_count'] = None

    exact_count = (result["match_type"] == "exact").sum()
    exact_multiple_count = (result["match_type"] == "exact_multiple").sum()

    print(f"  • {exact_count} correspondances exactes trouvées")
    if exact_multiple_count > 0:
        print(f"  • {exact_multiple_count} correspondances avec candidats multiples")

    # ---------- 5. Préparation des index pour fuzzy matching ----------
    print("\n[5/7] Préparation des index pour fuzzy matching...")

    insee_key_to_code = (
        insee
        .dropna(subset=["key_commune"])
        .drop_duplicates(subset=["key_commune"])
        .set_index("key_commune")["insee_code"]
    )

    insee_code_to_nccenr = (
        insee
        .dropna(subset=["insee_code"])
        .drop_duplicates(subset=["insee_code"])
        .set_index("insee_code")["NCCENR"]
    )

    insee_code_to_nccenr_norm = (
        insee
        .dropna(subset=["insee_code"])
        .drop_duplicates(subset=["insee_code"])
        .set_index("insee_code")["NCCENR_norm"]
    )

    print(f"  • Index de {len(insee_key_to_code)} clés INSEE préparés")

    # ---------- 6. Étape 2 : Fuzzy matching par tokens/préfixes ----------
    print("\n[6/7] Étape 2 : Fuzzy matching par tokens/préfixes...")
    result = fuzzy_match_prefix(
        result,
        insee_key_to_code,
        insee_code_to_nccenr,
        insee_code_to_nccenr_norm
    )

    fuzzy_count_after_prefix = (result["match_type"] == "fuzzy").sum()
    print(f"  • {fuzzy_count_after_prefix} correspondances fuzzy trouvées (tokens/préfixes)")

    # ---------- 7. Étape 3 : Fuzzy matching par distance d'édition ----------
    print("\n[7/7] Étape 3 : Fuzzy matching par distance d'édition...")
    result = fuzzy_match_edit_distance(
        result,
        insee_key_to_code,
        insee_code_to_nccenr,
        insee_code_to_nccenr_norm,
        max_dist=MAX_LEVENSHTEIN_DISTANCE
    )

    fuzzy_count_final = (result["match_type"] == "fuzzy").sum()
    fuzzy_count_edit = fuzzy_count_final - fuzzy_count_after_prefix
    print(f"  • {fuzzy_count_edit} correspondances fuzzy supplémentaires (distance d'édition)")

    # ---------- 8. Export ----------
    print("\n" + "=" * 60)
    print("RÉSULTATS")
    print("=" * 60)

    total_matched = result["insee_code"].notna().sum()
    total_unmatched = result["insee_code"].isna().sum()

    # Compter les différents types de matches
    exact_count = (result["match_type"] == "exact").sum()
    exact_multiple_count = (result["match_type"] == "exact_multiple").sum()
    fuzzy_count = (result["match_type"] == "fuzzy").sum()
    fuzzy_multiple_count = (result["match_type"] == "fuzzy_multiple").sum()

    print(f"\nCorrespondances trouvées : {total_matched}/{len(result)} ({100 * total_matched / len(result):.1f}%)")
    print(f"  • Exact (unique)   : {exact_count}")
    if exact_multiple_count > 0:
        print(f"  • Exact (multiples): {exact_multiple_count} ⚠️ Nécessitent validation")
    print(f"  • Fuzzy (unique)   : {fuzzy_count}")
    if fuzzy_multiple_count > 0:
        print(f"  • Fuzzy (multiples): {fuzzy_multiple_count} ⚠️ Nécessitent validation")
    print(f"\nNon appariés : {total_unmatched}")

    # Afficher quelques exemples de matches multiples
    if exact_multiple_count > 0 or fuzzy_multiple_count > 0:
        print("\n" + "-" * 60)
        print("EXEMPLES DE MATCHES MULTIPLES (nécessitent validation)")
        print("-" * 60)

        multiples = result[result["match_type"].str.contains("multiple", na=False)].head(5)
        for idx, row in multiples.iterrows():
            print(f"\n{row['id']} - {row['vedette']}")
            print(f"  Clé recherchée : {row['key_commune']}")
            print(f"  Candidats INSEE : {row['insee_code']}")
            print(f"  Candidats NCCENR: {row['NCCENR_norm']}")
            print(f"  Type : {row['match_type']}")

    # Export
    result.to_excel(out_path, index=False)
    print(f"\n{'=' * 60}")
    print(f"Fichier exporté : {out_path}")
    print("=" * 60)


# ==================== Point d'entrée ====================

def main():
    """Point d'entrée principal du script."""

    # Récupérer les arguments de ligne de commande
    if len(sys.argv) == 4:
        dt_path = sys.argv[1]
        insee_path = sys.argv[2]
        out_path = sys.argv[3]
    else:
        dt_path = DEFAULT_DT_PATH
        insee_path = DEFAULT_INSEE_PATH
        out_path = DEFAULT_OUT_PATH

        if len(sys.argv) > 1:
            print("Usage: python match.py [input_file] [cog_file] [output_file]")
            print("Utilisation des chemins par défaut...")

    # Vérifier l'existence des fichiers d'entrée
    if not Path(dt_path).exists():
        print(f"❌ Erreur : Fichier dictionnaire introuvable : {dt_path}")
        sys.exit(1)

    if not Path(insee_path).exists():
        print(f"❌ Erreur : Fichier COG introuvable : {insee_path}")
        sys.exit(1)

    # Lancer le traitement
    try:
        process_matching(dt_path, insee_path, out_path)
    except Exception as e:
        print(f"\n❌ Erreur lors du traitement : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()