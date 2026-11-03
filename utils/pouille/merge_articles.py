"""
Reconstitution des articles des Pouillés — tomes 1 à 6
======================================================

OBJECTIF
--------

Les références aux pages sont rattachées exclusivement aux entrées des formes anciennes
(articles commençant par <forme_ancienne>). Il faut donc réunir les informations de ces
entrées avec celles des formes modernes correspondantes (articles commençant par <vedette>),
afin d'obtenir un article unique et complet pour chaque lieu.

PRINCIPE GÉNÉRAL
----------------

1. Chaque article reçoit une clé d'entité : (vedette normalisée, localisations normalisées).
   Deux articles de même clé désignent le même lieu.
2. Les articles de même clé sont regroupés. Deux regroupements complémentaires rapprochent
   des clés presque identiques (cas 4 et 5).
3. Dans chaque groupe, l'article de forme moderne est conservé. Ses <forme_ancienne> sont
   remplacées par celles de tous les articles du groupe qui contiennent une <reference>,
   dédoublonnées puis triées chronologiquement.
4. Les articles absorbés sont supprimés ; les articles restants sont renumérotés
   (id="PO{N}-00001"…, où {N} est le numéro du tome) et reçoivent l'attribut pg, déduit
   des balises <pg>.

LOGIQUES DE NORMALISATION
-------------------------

Trois mécanismes rendent la clé d'entité tolérante aux variantes d'écriture :

(a) Normalisation textuelle (normalize_text) : minuscules, sans accents, apostrophes
    unifiées, espaces simplifiés.

(b) Règle « BASE = BASE-SUITE » (conseil du responsable scientifique) :
    un nom court est rattaché à la forme longue qui le prolonge après un trait d'union,
    à condition que le contexte soit identique. Cette règle n'est PAS écrite en dur :
    elle est déduite du corpus avant le regroupement (build_prefix_aliases).

      - Pour les localisations (canton, commune, arrondissement) : le contexte est le
        département. « con de Dampierre » devient « con de Dampierre-sur-Salon » si
        « Dampierre-sur-Salon » est la seule forme longue de « Dampierre » dans le
        département.
      - Pour les vedettes : le contexte est (département, canton, commune). Le canton doit
        être renseigné et identique. « Charency, auj. Saint-Didier » se rattache ainsi à
        « Saint-Didier-sur-Arroux » dans un même canton.

    Garde-fous :
      - Si la forme courte peut se prolonger de plusieurs façons dans le contexte
        (Pouilly-en-Auxois / Pouilly-en-Montagne, Nogent-le-Roi / Nogent-en-Bassigny,
        Saint-Symphorien-…), aucun rattachement n'est fait : le cas est écrit dans le
        rapport CSV (action « ambigu »).
      - Deux formes longues différentes ne sont jamais rapprochées l'une de l'autre
        (Bar-sur-Aube ≠ Bar-sur-Seine ; Pont-de-Vaux ≠ Pont-de-Veyle).
      - Pour les vedettes, sans canton renseigné, aucune règle n'est appliquée
        (Saint-Sauveur ≠ Saint-Sauveur-le-Vicomte).

(c) Alias manuels (LOCALISATION_ALIASES) : pour les variantes qui ne relèvent pas de la
    règle (b), par exemple deux graphies longues d'un même toponyme
    (Magneux-Hauterive / Magneux-Haute-Rive).

EXEMPLE
-------

Article de forme moderne :

    <article>
        <vedette><i>Labergement-lés-Seurre</i></vedette>
        <localisationde>Côte-d’Or</localisationde>
        <localisationca>c<sup>on</sup> de Seurre</localisationca>
        <forme_ancienne>— <fa>Abargamentum Ducis</fa>;</forme_ancienne>
        <forme_ancienne><fa>l’Abergement</fa>.</forme_ancienne>
    </article>

Article de forme ancienne 1 :

    <article>
        <forme_ancienne><fa>Abargamentum Ducis</fa>, <reference>185f</reference>.</forme_ancienne>
        <vedette><i>Labergement-lés-Seurre</i></vedette>
        <localisationde>Côte-d’Or</localisationde>
        <localisationca>c<sup>on</sup> de Seurre</localisationca>
    </article>

Article de forme ancienne 2 :

    <article>
        <forme_ancienne><fa>Abergement</fa> (l’), prebenda, <reference>108a</reference>.</forme_ancienne>
        <vedette><i>Labergement-lés-Seurre</i></vedette>
        <localisationde>Côte-d’Or</localisationde>
        <localisationca>c<sup>on</sup> de Seurre</localisationca>
    </article>

Article reconstitué :

    <article>
        <vedette><i>Labergement-lés-Seurre</i></vedette>
        <localisationde>Côte-d’Or</localisationde>
        <localisationca>c<sup>on</sup> de Seurre</localisationca>
        <forme_ancienne><fa>Abergement</fa> (l’), prebenda, <reference>108a</reference>.</forme_ancienne>
        <forme_ancienne><fa>Abargamentum Ducis</fa>, <reference>185f</reference>.</forme_ancienne>
    </article>

CAS PARTICULIERS
----------------

Cas 1 : Homonymes.
-> Les localisations font partie de la clé d'entité (article_key) : deux articles de même
   vedette mais de localisations différentes ne sont pas fusionnés.

    Abergement dans l'Ain ≠ Abergement en Saône-et-Loire
    Arconcey en Côte-d’Or, canton de Pouilly ≠ Arconcey en Côte-d’Or, canton de Saint-Jean-de-Losne

Cas 2 : Variations de vedettes.
-> raw_vedette_names ramène ces variantes à un même ensemble de noms normalisés
   (article antéposé ou postposé, « S. » = « Saint », « auj. », « jadis »,
   « ou », « autrement dit »).

    L’Abergement = Abergement (l’)
    Le Puy = Puy (le)
    Oroux, auj. Saint-Aubin = Saint-Aubin, jadis Oroux = Saint-Aubin
    Aisey-le-Duc ou Aisey-sur-Seine = Aisey-sur-Seine ou Aisey-le-Duc = Aisey-le-Duc
    Le Val-S.-Martin, autrement dit Sélignat = Sélignat
    Charency, auj. Saint-Didier = Charency, auj. Saint-Didier-sur-Arroux   (règle BASE = BASE-SUITE,
                                                                           même département et même canton)

   Vedettes volontairement non fusionnées (entités distinctes, indiquées par <compl>) :

    <vedette><i>Baume</i></vedette>
    <compl>(Saint-Gervais, à)</compl>
        ≠
    <vedette><i>Saint-Gervais</i></vedette>
    <compl><i>à Baume</i></compl>

    Lezinnes (Non loin de) ≠ Lezinnes

   Cas non traités automatiquement (graphies proches), à vérifier manuellement :

    Saint-Georges-de-Baroille ≈ Saint-Georges-de-Baroilles
    N.-D.-de-Boisset ≈ Notre-Dame-de-Boisset
    C.-le-Château ≈ Cirey-le-Château
    Chevagnes ≈ Chavagnes
    Baroille ≈ Baroilles
    Carizien ≈ Carizieu

Cas 3 : Variations de cantons et de communes.
-> normalize_localisation transforme « S.- » en « Saint- ». La règle BASE = BASE-SUITE
   (build_prefix_aliases) rattache le nom court à la forme longue unique du département.

    con de S.-Gengoux = con de Saint-Gengoux
    con de Dampierre = con de Dampierre-sur-Salon
    con de Semur = con de Semur-en-Brionnais
    con de Sennecey = con de Sennecey-le-Grand
    con de Villars = con de Villars-les-Dombes
    cne de Magneux-Hauterive = cne de Magneux-Haute-Rive   (alias manuel)

   Cas ambigus, NON fusionnés (action « ambigu » dans le rapport CSV) :

    con de Pouilly ? Pouilly-en-Auxois / Pouilly-en-Montagne
    con de Nogent ? Nogent-le-Roi / Nogent-en-Bassigny

   Formes longues distinctes, jamais rapprochées :

    con de Bar-sur-Aube ≠ con de Bar-sur-Seine

Cas 4 : Localisation incomplète.
-> Deux clés de même vedette sont regroupées si les localisations de l'une sont incluses
   dans celles de l'autre (action « fusion_inclusion » dans le rapport CSV).

    <vedette><i>Argouges</i></vedette>
    <localisationde>Manche</localisationde>
    <localisationca>c<sup>on</sup> de Saint-James</localisationca>
        =
    <vedette><i>Argouges</i></vedette>
    <localisationde>Manche</localisationde>
    <localisationca>c<sup>on</sup> de Saint-James</localisationca>
    <localisationco>c<sup>ne</sup> de Saint-James</localisationco>

Cas 5 : Deux entrées de formes modernes pour un même lieu.
-> Les vedettes qui partagent au moins un nom (« A ou B », « A, autrement dit B ») dans un
   même département sont regroupées (action « fusion_nom_partage » dans le rapport CSV).
   Au moins une des deux vedettes doit comporter plusieurs noms. L'article moderne conservé
   est le premier dans l'ordre du document ; l'autre, y compris son <renvoi>, est supprimé.

Article de forme moderne 1 :

    <article>
        <vedette><i>Bonvaux</i> ou <i>le Val-Notre-Dame</i></vedette>
        <localisationde>Côte-d’Or</localisationde>
        <localisationca>c<sup>on</sup> de Dijon</localisationca>
        <localisationco>c<sup>ne</sup> de Daix</localisationco>
        <forme_ancienne>— <fa>Vallis Beate Marie</fa>.</forme_ancienne>
    </article>

Article de forme moderne 2 :

    <article>
        <vedette><i>Val-Notre-Dame</i> (<i>le</i>) ou <i>Bonvaux</i></vedette>
        <localisationde>Côte-d’Or</localisationde>
        <localisation>arr. de Dijon</localisation>
        <localisationco>c<sup>ne</sup> de Daix</localisationco>
        <renvoi>voir <i>Bonvaux</i>.</renvoi>
    </article>

Article reconstitué : l'article 1 (vedette, localisations, formes anciennes munies d'une
<reference> provenant du groupe). L'article 2 est supprimé.

Cas 6 : Une forme ancienne n'est pas présente dans l'article de la forme moderne.
-> Elle est ajoutée à l'article reconstitué.

Article de forme moderne :

    <article>
        <vedette><i>Hauteville</i></vedette>
        <localisationde>Haute-Marne</localisationde>
        <localisationca>c<sup>on</sup> d’Auberive</localisationca>
        <localisationco>c<sup>ne</sup> de Bay</localisationco>
        <forme_ancienne>— <fa>Altavilla</fa>.</forme_ancienne>
    </article>

Article de forme ancienne :

    <article>
        <forme_ancienne><fa>Altavilla</fa>, <reference>126 e</reference>;</forme_ancienne>
        <forme_ancienne><fa>Alta Villa</fa>, <reference>160 a</reference>.</forme_ancienne>
        <vedette><i>Hauteville</i></vedette>
        <localisationde>Haute-Marne</localisationde>
        <localisationca>c<sup>on</sup> d’Auberive</localisationca>
        <localisationco>c<sup>ne</sup> de Bay</localisationco>
    </article>

Article reconstitué :

    <article id="PO1-01186" pg="245">
        <vedette><i>Hauteville</i></vedette>
        <localisationde>Haute-Marne</localisationde>
        <localisationca>c<sup>on</sup> d’Auberive</localisationca>
        <localisationco>c<sup>ne</sup> de Bay</localisationco>
        <forme_ancienne><fa>Altavilla</fa>, <reference>126 e</reference>;</forme_ancienne>
        <forme_ancienne><fa>Alta Villa</fa>, <reference>160 a</reference>.</forme_ancienne>
    </article>

Cas 7 : Une forme ancienne de l'article de forme moderne n'a pas d'article de forme ancienne propre.
-> Elle est supprimée (seules les formes anciennes munies d'une <reference> sont conservées).

Article de forme moderne qui contient trois formes anciennes :

    <article>
        <vedette><i>Beaumont-sur-Vingeanne</i></vedette>
        <localisationde>Côte-d’Or</localisationde>
        <localisationca>c<sup>on</sup> de Mirebeau</localisationca>
        <forme_ancienne>— <fa>Bellus Mons</fa>;</forme_ancienne>
        <forme_ancienne><fa>Sanctus Martinus subtus Bellum Montem</fa>;</forme_ancienne>
        <forme_ancienne><fa>Sanctus Martinus subtus Belmont</fa>.</forme_ancienne>
    </article>

Un seul article de forme ancienne correspondant :

    <article>
        <forme_ancienne><fa>Bellus Mons</fa>, <reference>124 e, 156 g</reference>.</forme_ancienne>
        <vedette><i>Beaumont-sur-Vingeanne</i></vedette>
        <localisationde>Côte-d’Or</localisationde>
        <localisationca>c<sup>on</sup> de Mirebeau</localisationca>
    </article>

Article reconstitué :

    <article id="PO1-00215" pg="212">
        <vedette><i>Beaumont-sur-Vingeanne</i></vedette>
        <localisationde>Côte-d’Or</localisationde>
        <localisationca>c<sup>on</sup> de Mirebeau</localisationca>
        <forme_ancienne><fa>Bellus Mons</fa>, <reference>124 e, 156 g</reference>.</forme_ancienne>
    </article>

Cas 8 : Vedette « ?? ».
-> Les articles dont la vedette est inconnue (« ?? ») sont laissés intacts et exclus de la fusion.

Cas 9 : Groupe sans article de forme moderne.
-> L'article reconstitué est construit à partir du premier article du groupe (action
   « sans_moderne » dans le rapport CSV).

SORTIES
-------

- PO_t{N}_merged.xml : XML reconstitué.
- PO_t{N}_merge.csv : rapport de relecture, une ligne par fusion ou par cas ambigu.
- PO_t{N}_merge.log : compteurs récapitulatifs.

RAPPORT CSV (PO_t{N}_merge.csv, séparateur « ; », encodage UTF-8 avec BOM pour Excel)
-------------------------------------------------------------------------------

- action        : fusion | fusion_nom_partage | fusion_inclusion | sans_moderne | ambigu
- a_verifier    : « non » pour une fusion à clé identique, « oui » pour tout le reste
- id_final      : identifiant PO{N}-… de l'article retenu (après renumérotation)
- pg            : page de l'article retenu
- vedette, departement, canton, commune : localisation du lieu
- nb_articles   : nombre d'articles fusionnés
- lignes_sources: numéros de ligne des articles sources dans le fichier d'ENTRÉE
- detail        : règle appliquée (nom commun, localisations incluses, alias ambigus)

PARAMÈTRES
----------

Le tome à traiter se règle par la constante TOME (par défaut : 1), ou en argument :

    python reconstitution_pouilles.py          # tome 1 (valeur de TOME)
    python reconstitution_pouilles.py 3        # tome 3

Les noms de fichiers en découlent : entrée PO_t{N}.xml, sortie PO_t{N}_merged.xml,
rapports PO_t{N}_merge.csv et PO_t{N}_merge.log, préfixe d'identifiant « PO{N}- ».
Pour un fichier d'entrée nommé autrement, modifier INPUT.
"""

import csv
import sys
from collections import defaultdict, Counter
from copy import deepcopy
from lxml import etree
import re
import unicodedata

# --- Paramètres (tome 1 par défaut ; un argument en ligne de commande le remplace) ---
TOME = int(sys.argv[1]) if len(sys.argv) > 1 else 1   # numéro du tome (1 à 6)

INPUT = f"PO_t{TOME}.xml"
OUTPUT = f"PO_t{TOME}_merged.xml"
CSV_OUTPUT = f"PO_t{TOME}_merge.csv"
LOG_OUTPUT = f"PO_t{TOME}_merge.log"
ID_PREFIX = f"PO{TOME}-"

parser = etree.XMLParser(remove_blank_text=False)
tree = etree.parse(INPUT, parser)
root = tree.getroot()

records = []                      # une entrée par fusion ou par cas ambigu (rapport CSV)
widened = defaultdict(list)       # clé de groupe -> règles élargies appliquées (nom partagé, inclusion)
removed_articles = 0
merged_groups = 0
missing_modern_groups = 0
skipped_unknown_vedette = 0

# Alias manuels : variantes de localisations qui ne relèvent pas de la règle BASE = BASE-SUITE.
# Clé : (département normalisé, valeur normalisée) -> valeur canonique.
LOCALISATION_ALIASES = {
    ("loire", "cne de magneux-hauterive"): "cne de magneux-haute-rive",
}


# --- Fonctions de normalisation et d'extraction ---

def text_content(node):
    """Extrait l'ensemble du texte brut contenu dans un nœud XML."""
    return "".join(node.itertext()) if node is not None else ""


def normalize_text(text):
    """Nettoie les espaces, diacritiques, minuscules et apostrophes."""
    value = " ".join((text or "").split()).lower()
    value = value.replace("’", "'").replace("‘", "'")
    decomposed = unicodedata.normalize("NFD", value)
    value = "".join(
        char for char in decomposed
        if unicodedata.category(char) != "Mn"
    )
    return re.sub(r"\s+", " ", value).strip()


def normalize_localisation(text):
    """Normalise les cantons et communes (S.- -> Saint-, etc.)."""
    value = normalize_text(text)
    value = re.sub(r"\bs\s*\.\s*-\s*", "saint-", value)
    value = re.sub(r"\bst\s*\.\s*-\s*", "saint-", value)
    value = re.sub(r"\bs\s*\.\s+", "saint ", value)
    value = re.sub(r"\bst\s*\.\s+", "saint ", value)
    value = re.sub(r"\bst-\s*", "saint-", value)
    value = re.sub(r"\bst\s+", "saint ", value)
    return re.sub(r"\s+", " ", value).strip()


def raw_vedette_names(text):
    """
    Retourne l'ensemble des noms normalisés d'une vedette, tirets conservés.

    - Renvois chronologiques : 'Oroux, auj. Saint-Aubin' -> {'saint-aubin'}
                               'Saint-Aubin, jadis Oroux' -> {'saint-aubin'}
    - Doublets et renvois : 'Sélignat, autrement dit le Val-Saint-Martin'
                            -> {'selignat', 'val-saint-martin'}
    - Articles postposés ou antéposés, abréviation « S. ».
    """
    base = normalize_text(text)

    # Abréviations de saint
    base = re.sub(r"\b(?:s|st)\.\s*-\s*", "saint-", base)
    base = re.sub(r"\b(?:s|st)\.\s*", "saint ", base)

    # Renvois chronologiques : nom actuel (auj.) ou nom principal (jadis)
    if " auj." in base or " aujourd'hui" in base:
        parts = re.split(r",?\s*(?:auj\.|aujourd'hui)\s*", base)
        if len(parts) > 1:
            base = parts[1]
    elif " jadis " in base or " autrefois " in base:
        base = re.split(r",?\s*(?:jadis|autrefois)\s*", base)[0]

    names = set()
    for part in re.split(r"\s+(?:ou|autrement dit)\s+", base):
        value = part.strip().strip(" ,;.")
        value = re.sub(r"^(.+?)\s*\(\s*(l'|la|le|les)\s*\)$", r"\2 \1", value)
        value = value.replace("l '", "l'").replace("l' ", "l'")
        value = re.sub(r"^(l'|la\s+|le\s+|les\s+)", "", value)
        value = re.sub(r"\s+", " ", value).strip()
        if value:
            names.add(value)
    return names


def get_department(article):
    for child in article:
        if isinstance(child.tag, str) and child.tag == "localisationde":
            return normalize_localisation(text_content(child))
    return ""


def localisation_children(article):
    return [
        c for c in article
        if isinstance(c.tag, str) and c.tag.startswith("localisation")
    ]


def loc_text(article, tag):
    """Texte brut d'une balise de localisation (pour le rapport CSV)."""
    node = article.find(tag)
    return " ".join(text_content(node).split()) if node is not None else ""


# --- Règle BASE = BASE-SUITE (alias déduits du corpus) ---

def build_prefix_aliases(articles):
    """
    Déduit du corpus les alias « BASE -> BASE-SUITE ».

    Localisations : contexte = (département, balise). Une valeur courte est rattachée à la
    valeur longue qui la prolonge après un trait d'union, si elle est UNIQUE.

    Vedettes : contexte = (département, canton, commune), canton obligatoire. Même principe,
    appliqué aux noms de vedette.

    Si plusieurs prolongements existent (ambiguïté), aucun alias n'est créé.
    Retourne (alias_localisations, alias_vedettes, ambiguïtés).
    """
    loc_values = defaultdict(set)
    for art in articles:
        dept = get_department(art)
        for child in localisation_children(art):
            if child.tag != "localisationde":
                loc_values[(dept, child.tag)].add(
                    LOCALISATION_ALIASES.get(
                        (dept, normalize_localisation(text_content(child))),
                        normalize_localisation(text_content(child)),
                    )
                )

    loc_alias, ambiguous = {}, []
    for (dept, tag), values in loc_values.items():
        for short in values:
            longs = sorted(v for v in values if v.startswith(short + "-"))
            if len(longs) == 1:
                loc_alias[(dept, tag, short)] = longs[0]
            elif len(longs) > 1:
                ambiguous.append(f"{dept} / {tag} / '{short}' ↔ {longs}")

    names_by_ctx = defaultdict(set)
    for art in articles:
        vedette = art.find("vedette")
        if vedette is None or normalize_text(text_content(vedette)) in ("", "??"):
            continue
        ctx = article_context(art, loc_alias)
        if ctx is None:
            continue
        names_by_ctx[ctx].update(raw_vedette_names(text_content(vedette)))

    ved_alias = {}
    for ctx, names in names_by_ctx.items():
        for short in names:
            longs = sorted(n for n in names if n.startswith(short + "-"))
            if len(longs) == 1:
                ved_alias[(ctx, short)] = longs[0]
            elif len(longs) > 1:
                ambiguous.append(f"vedette {ctx} '{short}' ↔ {longs}")

    return loc_alias, ved_alias, ambiguous


def canonical_localisation(dept, tag, value, loc_alias):
    value = LOCALISATION_ALIASES.get((dept, value), value)
    return loc_alias.get((dept, tag, value), value)


def article_context(article, loc_alias):
    """(département, canton, commune) canoniques ; None si le canton n'est pas renseigné."""
    dept = get_department(article)
    ca = co = ""
    for child in localisation_children(article):
        value = canonical_localisation(dept, child.tag, normalize_localisation(text_content(child)), loc_alias)
        if child.tag == "localisationca":
            ca = value
        elif child.tag == "localisationco":
            co = value
    if not ca:
        return None
    return (dept, ca, co)


# --- Formes anciennes ---

def extract_fa_stem(fa_node):
    """Extrait le radical du lemme pour la comparaison des formes anciennes."""
    fa_elem = fa_node.find("fa")
    if fa_elem is not None:
        raw = text_content(fa_elem)
    else:
        raw = text_content(fa_node).split(",")[0].split("(")[0].replace("—", "")

    clean = normalize_text(raw)
    clean = re.sub(r"^(.+?)\s*\(\s*(l'|la|le|les)\s*\)$", r"\2 \1", clean)
    clean = re.sub(r"^(l'|la\s+|le\s+|les\s+)", "", clean)
    clean = re.sub(r"[^a-z]", "", clean)
    return clean[:5] if len(clean) >= 5 else clean


def get_fa_dedup_key(fa_node):
    """Génère une clé de dédoublonnage basée sur (radical_lemme, references)."""
    fa_stem = extract_fa_stem(fa_node)
    refs = tuple(
        normalize_text(text_content(r))
        for r in fa_node.findall("reference")
    )
    return (fa_stem, refs)


def extract_chronological_key(fa_node):
    """
    Extrait l'année ou le repère numérique pour ordonner
    les formes anciennes chronologiquement.
    """
    full_text = text_content(fa_node)

    # 1. Recherche d'une année explicite à 3 ou 4 chiffres (ex: 980, 1180, 1345)
    year_match = re.search(r"\b(1?\d{3})\b", full_text)
    if year_match:
        return int(year_match.group(1))

    # 2. Recherche du premier repère numérique dans la balise <reference>
    ref_texts = " ".join(text_content(r) for r in fa_node.findall("reference"))
    ref_match = re.search(r"\d+", ref_texts)
    if ref_match:
        return int(ref_match.group(0))

    # 3. Valeur par défaut si aucun repère n'est détecté
    return 9999


# --- Clé d'entité ---

def article_key(article):
    """Clé d'entité : (vedette normalisée, localisations canoniques, ensemble des noms)."""
    vedette = article.find("vedette")
    if vedette is None:
        return None

    raw_vedette = text_content(vedette).strip()
    if not raw_vedette or normalize_text(raw_vedette) == "??":
        return None

    names = raw_vedette_names(raw_vedette)
    ctx = article_context(article, LOC_PREFIX_ALIASES)
    if ctx is not None:
        names = {VEDETTE_PREFIX_ALIASES.get((ctx, n), n) for n in names}
    variants = frozenset(re.sub(r"\s+", " ", n.replace("-", " ")).strip() for n in names)
    if not variants:
        return None

    heading_key = " | ".join(sorted(variants))

    dept = get_department(article)
    locations = frozenset(Counter(
        (child.tag, canonical_localisation(dept, child.tag, normalize_localisation(text_content(child)), LOC_PREFIX_ALIASES))
        for child in localisation_children(article)
    ).items())
    return heading_key, locations, variants


# --- Traitement principal ---

# 0. Prise en compte de la pagination (<pg>NUM</pg>) au fil du document XML
current_pg = None
for child in root:
    if child.tag == "pg":
        current_pg = text_content(child).strip()
    elif child.tag == "article":
        if "pg" not in child.attrib and current_pg:
            child.set("pg", current_pg)

# 0bis. Alias « BASE = BASE-SUITE » déduits du corpus
LOC_PREFIX_ALIASES, VEDETTE_PREFIX_ALIASES, ambiguities = build_prefix_aliases(root.findall("article"))
for line in sorted(set(ambiguities)):
    records.append({"action": "ambigu", "a_verifier": "oui", "element": None,
                    "sources": [], "detail": f"non fusionné : {line}"})
prefix_alias_count = len(LOC_PREFIX_ALIASES) + len(VEDETTE_PREFIX_ALIASES)

# 1. Regroupement des notices par clé d'entité
groups = defaultdict(list)
for article in root.findall("article"):
    key = article_key(article)
    if key is None:
        skipped_unknown_vedette += 1
        continue
    groups[key].append(article)

# 1bis. Cas 5 : regroupe les vedettes qui partagent au moins un nom
# ('A ou B', 'A, autrement dit B'), dans un même département.
# Sécurité : au moins l'une des deux vedettes doit être multi-noms.
intersection_merges = 0
dept_by_key = {key: get_department(articles[0]) for key, articles in groups.items()}

uf_parent = {key: key for key in groups}


def find(x):
    while uf_parent[x] != x:
        uf_parent[x] = uf_parent[uf_parent[x]]
        x = uf_parent[x]
    return x


by_name = defaultdict(list)
for key in groups:
    for name in key[2]:
        by_name[(dept_by_key[key], name)].append(key)

for (dept, name), shared_keys in by_name.items():
    for k1 in shared_keys:
        if len(k1[2]) < 2:
            continue
        for k2 in shared_keys:
            if k1 == k2:
                continue
            r1, r2 = find(k1), find(k2)
            if r1 != r2:
                uf_parent[r2] = r1
                intersection_merges += 1
                widened[k1].append(f"nom partagé : {name}")

new_groups = defaultdict(list)
for key, articles in groups.items():
    new_groups[find(key)].extend(articles)
groups = new_groups

remapped = defaultdict(list)
for key, rules in widened.items():
    remapped[find(key)].extend(rules)
widened = remapped

# 1ter. Cas 4 : regroupe les clés de même vedette dont les localisations sont incluses
# l'une dans l'autre (une notice peut être moins précise que l'autre).
subset_merges = 0
by_heading = defaultdict(list)
for key in groups:
    by_heading[key[0]].append(key)

for heading, heading_keys in by_heading.items():
    if len(heading_keys) < 2:
        continue
    changed = True
    while changed:
        changed = False
        for i, k1 in enumerate(heading_keys):
            if k1 not in groups:
                continue
            c1 = Counter(dict(k1[1]))
            for k2 in heading_keys[i + 1:]:
                if k2 not in groups:
                    continue
                c2 = Counter(dict(k2[1]))
                if c1 <= c2 or c2 <= c1:
                    target, source = (k1, k2) if len(c1) >= len(c2) else (k2, k1)
                    groups[target].extend(groups[source])
                    del groups[source]
                    widened[target].extend(widened.pop(source, []))
                    widened[target].append(f"inclusion : {sorted(dict(source[1]).items())}")
                    subset_merges += 1
                    changed = True
                    break
            if changed:
                break

# 2. Reconstitution des groupes d'articles
for key, art_list in groups.items():
    if len(art_list) == 1:
        continue

    # Repérage de l'entrée moderne principale (commençant par <vedette>)
    modern = [a for a in art_list if len(a) > 0 and a[0].tag == "vedette"]
    has_modern = bool(modern)
    if not has_modern:
        # Cas 9 : aucun article moderne ; on reconstitue à partir du premier article du groupe.
        modern = art_list
        missing_modern_groups += 1

    primary = modern[0]
    other_articles = [a for a in art_list if a is not primary]
    sources = sorted(a.sourceline for a in art_list if a.sourceline is not None)

    # A. Collecte et dédoublonnage des <forme_ancienne> valides (contenant <reference>)
    fa_by_key = {}
    for art in art_list:
        for fa_node in art.findall("forme_ancienne"):
            if fa_node.find("reference") is not None:
                dedup_key = get_fa_dedup_key(fa_node)
                if dedup_key not in fa_by_key:
                    fa_by_key[dedup_key] = deepcopy(fa_node)
                else:
                    # Conservation de la forme la plus détaillée/descriptive
                    if len(text_content(fa_node)) > len(text_content(fa_by_key[dedup_key])):
                        fa_by_key[dedup_key] = deepcopy(fa_node)

    # B. Suppression de toutes les anciennes formes d'origine de la notice principale
    for old_fa in list(primary.findall("forme_ancienne")):
        primary.remove(old_fa)

    # C. Tri chronologique des formes anciennes retenues
    sorted_fa = sorted(fa_by_key.values(), key=extract_chronological_key)

    # D. Réinsertion ordonnée dans la notice principale
    for valid_fa in sorted_fa:
        primary.append(valid_fa)

    # E. Suppression des notices secondaires réconciliées
    for other in other_articles:
        article_parent = other.getparent()
        if article_parent is not None:
            article_parent.remove(other)
            removed_articles += 1

    merged_groups += 1

    # F. Enregistrement pour le rapport CSV
    rules = sorted(set(widened.get(key, [])))
    if not has_modern:
        action = "sans_moderne"
    elif any(r.startswith("nom partagé") for r in rules):
        action = "fusion_nom_partage"
    elif any(r.startswith("inclusion") for r in rules):
        action = "fusion_inclusion"
    else:
        action = "fusion"
    records.append({
        "action": action,
        "a_verifier": "non" if action == "fusion" else "oui",
        "element": primary,
        "sources": sources,
        "detail": " ; ".join(rules),
    })

# 3. Formatage et réordonnancement strict des attributs (<article id="..." pg="...">)
for idx, article in enumerate(root.findall("article"), start=1):
    new_id = f"{ID_PREFIX}{idx:05d}"
    pg_val = article.get("pg", "XXX")

    # Conservation des attributs complémentaires éventuels
    other_attribs = {k: v for k, v in article.attrib.items() if k not in ("id", "pg")}

    # Reconstruction forcée dans l'ordre : 'id' puis 'pg'
    article.attrib.clear()
    article.set("id", new_id)
    article.set("pg", pg_val)
    for k, v in other_attribs.items():
        article.set(k, v)

# 4. Écriture du fichier reconstitué
tree.write(OUTPUT, encoding="utf-8", xml_declaration=True, pretty_print=True)

# 5. Rapport CSV (identifiants résolus après renumérotation)
fields = ["action", "a_verifier", "id_final", "pg", "vedette", "departement",
          "canton", "commune", "nb_articles", "lignes_sources", "detail"]
with open(CSV_OUTPUT, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields, delimiter=";")
    writer.writeheader()
    for r in records:
        el = r["element"]
        writer.writerow({
            "action": r["action"],
            "a_verifier": r["a_verifier"],
            "id_final": el.get("id", "") if el is not None else "",
            "pg": el.get("pg", "") if el is not None else "",
            "vedette": " ".join(text_content(el.find("vedette")).split()) if el is not None else "",
            "departement": loc_text(el, "localisationde") if el is not None else "",
            "canton": loc_text(el, "localisationca") if el is not None else "",
            "commune": loc_text(el, "localisationco") if el is not None else "",
            "nb_articles": len(r["sources"]),
            "lignes_sources": ",".join(map(str, r["sources"])),
            "detail": r["detail"],
        })

# 6. Compteurs récapitulatifs
with open(LOG_OUTPUT, "w", encoding="utf-8") as f:
    f.write("=== RAPPORT DE RECONSTITUTION ===\n")
    f.write(f"Groupes d'articles reconstitués : {merged_groups}\n")
    f.write(f"Alias BASE = BASE-SUITE déduits du corpus : {prefix_alias_count}\n")
    f.write(f"Fusions par nom partagé (ou / autrement dit) : {intersection_merges}\n")
    f.write(f"Fusions par inclusion de localisations : {subset_merges}\n")
    f.write(f"Articles anciens/doublons supprimés : {removed_articles}\n")
    f.write(f"Notices '??' conservées intactes : {skipped_unknown_vedette}\n")
    f.write(f"Groupes sans notice moderne (reconstitués depuis les formes anciennes) : {missing_modern_groups}\n")
    f.write(f"Détail des fusions et cas ambigus : {CSV_OUTPUT}\n")

print(f"Traitement terminé. XML reconstitué : {OUTPUT} ; rapport : {CSV_OUTPUT}")