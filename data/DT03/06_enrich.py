from pathlib import Path
import re
import xml.etree.ElementTree as ET
import pandas as pd

# ---------- Paths ----------

XML_PATH = Path("src_DT03.xml")
XLSX_PATH = Path("05_DT03_validated.xlsx")
OUT_PATH = Path("06_DT03_enriched.xml")

# ---------- 1. Load Excel: id → info ----------

df = pd.read_excel(
    XLSX_PATH,
    dtype={"id": str, "insee_code": str}
)

df["id"] = df["id"].astype(str).str.strip()

info_by_id = {}
for _, row in df.iterrows():
    art_id = row["id"]
    if not isinstance(art_id, str):
        continue

    info_by_id[art_id] = {
        "is_commune": bool(row["is_commune"]),
        "insee_code": (str(row["insee_code"]).strip()
                       if pd.notna(row["insee_code"]) else None),
        "localisation": (str(row["localisation"]).strip()
                         if pd.notna(row["localisation"]) else None),
    }

# ---------- 2. Load XML ----------

tree = ET.parse(XML_PATH)
root = tree.getroot()

# motif générique « commune de X », « commune du X », « communes de X et de Y », etc.
COMMUNE_SIMPLE_RE = re.compile(
    r"""^\s*
        (commune[s]?\s+d['’]|commune[s]?\s+de|commune[s]?\s+du|commune[s]?\s+des)
        \s*(.+?)\s*$
    """,
    re.IGNORECASE | re.VERBOSE,
)

# pour séparer plusieurs communes dans la localisation Excel, si besoin
SEP_RE = re.compile(r"\s*,\s*|\s+et\s+")


# ---------- 3. Update articles ----------

for art in root.findall(".//article"):
    art_id = (art.get("id") or "").strip()
    if not art_id or art_id not in info_by_id:
        continue

    info = info_by_id[art_id]
    is_commune = info["is_commune"]
    insee_code = info["insee_code"]
    loc_xlsx = info["localisation"]

    # --- Cas 1 : is_commune == TRUE -> type="commune" + <insee> ----
    if is_commune and insee_code:
        # ajouter / forcer l’attribut type="commune"
        if art.get("type") != "commune":
            art.set("type", "commune")

        # ajouter la balise <insee> si absente
        if art.find("insee") is None:
            insee_el = ET.Element("insee")
            insee_el.text = insee_code
            art.append(insee_el)

    # --- Cas 2 : is_commune == FALSE -> réécrire <localisation> ----
    else:
        loc_el = art.find("./definition/localisation")
        if loc_el is None:
            continue

        # texte complet actuel de la balise localisation
        loc_text = "".join(loc_el.itertext()).strip()
        if not loc_text:
            continue

        # on ne fait rien si pas de code INSEE ou pas de localisation Excel structurée
        if not insee_code or not loc_xlsx:
            continue

        # Ex. Excel : « communes de Bazouges et de Château-Gontier »
        m = COMMUNE_SIMPLE_RE.match(loc_xlsx)
        if not m:
            # si le motif ne colle pas, on ne tente pas de restructurer
            continue

        connector = m.group(1)   # « commune de », « communes de », etc.
        communes_part = m.group(2)  # « Bazouges et de Château-Gontier », etc.

        # on va juste mettre UNE commune, car on n’a qu’un insee_code par id
        # si tu veux gérer plusieurs communes/insee, il faudra une structure plus riche dans l’Excel
        # pour l’instant, on prend la partie après le connecteur comme nom à afficher
        commune_name = communes_part.strip()

        # nettoyage de localisation actuelle
        for child in list(loc_el):
            loc_el.remove(child)

        # texte avant la balise <commune>
        # ex. « communes de »
        loc_el.text = connector + " "

        # balise <commune insee="XXX">Nom</commune>
        c_el = ET.SubElement(loc_el, "commune")
        c_el.set("insee", insee_code)
        c_el.text = commune_name

        # rien après dans la localisation (on garde éventuellement la ponctuation finale de l’ancienne localisation)
        # ici on récupère juste la ponctuation finale si elle existait
        punct = ""
        if loc_text.endswith("."):
            punct = "."
        loc_el.tail = punct

# ---------- 4. Save ----------

tree.write(OUT_PATH, encoding="utf-8", xml_declaration=True)