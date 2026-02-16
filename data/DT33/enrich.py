from pathlib import Path
import re
import xml.etree.ElementTree as ET
import pandas as pd

# ---------- Paths ----------

XML_PATH = Path("1_DT33.xml")
XLSX_PATH = Path("6_DT33_validated.xlsx")
OUT_PATH = Path("7_DT33_enriched.xml")

# ---------- 1. Load Excel: id → info ----------

df = pd.read_excel(XLSX_PATH, dtype={"id": str, "insee_code": str})
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
        "NCCENR": (str(row["NCCENR"]).strip()
                   if pd.notna(row["NCCENR"]) else None),
    }

# ---------- 2. Load XML ----------

tree = ET.parse(XML_PATH)
root = tree.getroot()

# matches "commune d'XXX", "commune d’XXX", "commune de XXX", "commune des XXX"
COMMUNE_RE = re.compile(
    r"""^
        (commune\s+d['’]      # commune d' / d’
        |commune\s+de         # commune de
        |commune\s+des)       # commune des
        \s*                   # optional extra spaces
        (.+)                  # commune name
        $
    """,
    re.IGNORECASE | re.VERBOSE,
)

# ---------- 3. Update articles ----------

for art in root.findall(".//article"):
    art_id = (art.get("id") or "").strip()
    if not art_id or art_id not in info_by_id:
        continue

    info = info_by_id[art_id]
    is_commune = info["is_commune"]
    insee_code = info["insee_code"]
    nccenr = info["NCCENR"]

    # --- Case 1: is_commune == TRUE -> add <insee> ---
    if is_commune and insee_code:
        if art.find("insee") is None:
            insee_el = ET.Element("insee")
            insee_el.text = insee_code
            art.append(insee_el)

    # --- Case 2: is_commune == FALSE -> rewrite <localisation> ---
    else:
        loc_el = art.find("./definition/localisation")
        if loc_el is None:
            continue

        # full text inside localisation (handles simple nesting if any)
        loc_text = "".join(loc_el.itertext()).strip()
        if not loc_text or not insee_code or not nccenr:
            continue

        m = COMMUNE_RE.match(loc_text)
        if not m:
            continue

        connector = m.group(1)        # "commune d'", "commune d’", "commune de", "commune des"
        commune_name = nccenr         # official INSEE name

        # keep punctuation after </localisation> (e.g. final dot)
        old_tail = loc_el.tail or ""

        # clear localisation content and rebuild with embedded <commune>
        for child in list(loc_el):
            loc_el.remove(child)
        loc_el.text = connector + " "

        c_el = ET.SubElement(loc_el, "commune")
        c_el.set("insee", insee_code)
        c_el.set("precision", "certain")
        c_el.text = commune_name
        c_el.tail = ""    # nothing after </commune> inside localisation

        loc_el.tail = old_tail

# ---------- 4. Save ----------

tree.write(OUT_PATH, encoding="utf-8", xml_declaration=True)
print(f"Written updated XML to {OUT_PATH}")
