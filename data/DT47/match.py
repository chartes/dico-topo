import pandas as pd
import re
import unicodedata

# ---------- Paths ----------

DT_PATH = "DT47_export.xlsx"          # your DT33 table
INSEE_PATH = "DT47_insee_commune.tsv"        # attached TSV
OUT_PATH = "DT47_with_insee.xlsx"

# ---------- 0. Levenshtein helper ----------

def levenshtein(a: str, b: str) -> int:
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
                dp[j] + 1,
                dp[j - 1] + 1,
                prev + cost,
            )
            prev = cur
    return dp[n]

# ---------- 1. Load data ----------

df = pd.read_excel(DT_PATH)
insee = pd.read_csv(INSEE_PATH, sep="\t", dtype=str)  # [file:46]

# Expect INSEE columns:
# 0: insee_code, 4: name (NCCENR), 5: ARTMIN or empty, etc.
# Adapt if your header row differs.
insee.columns = [
    "insee_code", "REG", "DEP", "AR", "CT",
    "NCCENR", "ARTMIN", "coords", "geonames",
    "wikidata", "wikipedia", "bnf", "col12",
    "col13", "col14", "col15",
][: len(insee.columns)]

# ---------- 2. Normalization helpers ----------

ARTICLE_LEADING_RE = re.compile(r"^(l['’]|\ble\b|\bla\b|\bles\b)\s+", re.IGNORECASE)

def strip_leading_article(s: str | None) -> str | None:
    if not isinstance(s, str):
        return None
    s = s.strip()
    if not s:
        return None
    s = re.sub(r"\(([Ll]e)\)|\(([Ll]a)\)|\(([Ll]es)\)|\(([Ll]['’])\)", lambda m: m.group(0).strip("()"), s)
    s = s.strip()
    s = ARTICLE_LEADING_RE.sub("", s).strip()
    return s or None

def norm(s: str | None) -> str | None:
    if not isinstance(s, str):
        return None
    s = s.strip()
    if not s:
        return None
    s = s.replace("’", "'").lower()
    s = re.sub(r"[-‐‑‒–—]", " ", s)
    s = "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    )
    s = re.sub(r"\s+", " ", s).strip()
    return s or None

def norm_without_article(s: str | None) -> str | None:
    base = strip_leading_article(s)
    if base is None:
        return None
    return norm(base)

# ---------- 3. Build INSEE key ----------

def insee_key(row: pd.Series) -> str | None:
    name_raw = row.get("NCCENR")
    art_raw = row.get("ARTMIN")
    name_raw = name_raw.strip() if isinstance(name_raw, str) else ""
    art_raw = art_raw.strip() if isinstance(art_raw, str) else ""
    if not name_raw and not art_raw:
        return None
    art_raw = re.sub(r"[()]", "", art_raw).strip()
    full = f"{art_raw} {name_raw}".strip()
    return norm_without_article(full)

insee["key_commune"] = insee.apply(insee_key, axis=1)
insee["NCCENR_norm"] = insee["NCCENR"].apply(norm_without_article)

# ---------- 4. Build DT33 keys ----------

ARTICLE_RE = re.compile(r"^(.*)\s+\((l[ea']|les)\)$", re.IGNORECASE)

def key_from_vedette(v: str | None) -> str | None:
    if not isinstance(v, str):
        return None
    v = v.strip()
    if not v:
        return None
    v = v.split(", alias", 1)[0].strip()
    m = ARTICLE_RE.match(v)
    if m:
        name = m.group(1).strip()
        art = m.group(2).lower().replace("'", "")
        v = f"{art} {name}"
    else:
        v = re.sub(r"\s*\([^)]*\)$", "", v).strip()
    return norm_without_article(v)

LOC_CONN_RE = re.compile(
    r"(de la|du|des|de)\s+(.+)|d[’'](.+)",
    re.IGNORECASE,
)

def key_from_localisation(loc: str | None) -> str | None:
    if not isinstance(loc, str):
        return None
    loc = loc.strip()
    if not loc:
        return None
    m = LOC_CONN_RE.search(loc)
    if not m:
        return None
    tail = (m.group(2) or m.group(3) or "").strip()
    if not tail:
        return None
    tail = re.split(r"\s*\|\s*|,|\set\s+", tail, maxsplit=1)[0].strip()
    tail = re.sub(r"\s*\([^)]*\)$", "", tail).strip()
    return norm_without_article(tail)

df["key_commune"] = None
is_commune = df["is_commune"]       # from your XML export
is_loc = ~df["is_commune"]

df.loc[is_commune, "key_commune"] = df.loc[is_commune, "vedette"].map(key_from_vedette)
df.loc[is_loc, "key_commune"] = df.loc[is_loc, "localisation"].map(key_from_localisation)

mask_loc_plain = is_loc & df["key_commune"].isna() & df["localisation"].notna()
df.loc[mask_loc_plain, "key_commune"] = df.loc[mask_loc_plain, "localisation"].map(norm_without_article)

# ---------- 5. Exact join ----------

result = df.merge(
    insee[["insee_code", "NCCENR", "NCCENR_norm", "key_commune"]],
    how="left",
    on="key_commune",
)

result["match_type"] = None
result.loc[result["insee_code"].notna(), "match_type"] = "exact"

# ---------- 6. Fuzzy stages (same as DT53 with first-token rule) ----------

insee_key_to_code = (
    insee
    .dropna(subset=["key_commune"])
    .drop_duplicates(subset=["key_commune"])
    .set_index("key_commune")["insee_code"]
)
insee_keys = insee_key_to_code.index.tolist()

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

def fuzzy_match_insee_prefix(key: str | None) -> str | None:
    if not isinstance(key, str) or not key:
        return None
    key_tokens = key.split()
    first_key = key_tokens[0] if key_tokens else ""
    best_code = None
    best_len = 0
    for k in insee_keys:
        if key == k:
            continue
        tokens = k.split()
        if not tokens:
            continue
        first_k = tokens[0]
        if first_k != first_key:
            continue
        if key in tokens or k.startswith(key + " "):
            if len(k) > best_len:
                best_len = len(k)
                best_code = insee_key_to_code[k]
    return best_code

mask_missing = result["insee_code"].isna() & result["key_commune"].notna()
result.loc[mask_missing, "insee_code"] = result.loc[mask_missing, "key_commune"].map(fuzzy_match_insee_prefix)

mask_fuzzy_prefix_ok = mask_missing & result["insee_code"].notna()
result.loc[mask_fuzzy_prefix_ok, "match_type"] = "fuzzy"
result.loc[mask_fuzzy_prefix_ok, "NCCENR"] = result.loc[mask_fuzzy_prefix_ok, "insee_code"].map(insee_code_to_nccenr)
result.loc[mask_fuzzy_prefix_ok, "NCCENR_norm"] = result.loc[mask_fuzzy_prefix_ok, "insee_code"].map(insee_code_to_nccenr_norm)

mask_still_missing = result["insee_code"].isna() & result["key_commune"].notna()

def fuzzy_match_insee_edit(key: str | None, max_dist: int = 1) -> str | None:
    if not isinstance(key, str) or not key:
        return None
    key_tokens = key.split()
    first_key = key_tokens[0] if key_tokens else ""
    best_code = None
    best_dist = max_dist + 1
    for k in insee_keys:
        tokens_k = k.split()
        first_k = tokens_k[0] if tokens_k else ""
        if first_k != first_key:
            continue
        d = levenshtein(key, k)
        if d < best_dist:
            best_dist = d
            best_code = insee_key_to_code[k]
    return best_code if best_dist <= max_dist else None

result.loc[mask_still_missing, "insee_code"] = result.loc[mask_still_missing, "key_commune"].map(
    lambda k: fuzzy_match_insee_edit(k)
)

mask_edit_ok = mask_still_missing & result["insee_code"].notna()
result.loc[mask_edit_ok, "match_type"] = "fuzzy"
result.loc[mask_edit_ok, "NCCENR"] = result.loc[mask_edit_ok, "insee_code"].map(insee_code_to_nccenr)
result.loc[mask_edit_ok, "NCCENR_norm"] = result.loc[mask_edit_ok, "insee_code"].map(insee_code_to_nccenr_norm)

# ---------- 7. Export ----------

result.to_excel(OUT_PATH, index=False)
print(f"{len(result)} rows written to {OUT_PATH}")
print(f"{(result['match_type'] == 'exact').sum()} rows matched exactly")
print(f"{(result['match_type'] == 'fuzzy').sum()} rows matched fuzzily")
