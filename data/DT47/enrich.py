from pathlib import Path
import xml.etree.ElementTree as ET
import pandas as pd

BASE = Path(__file__).parent
XML_PATH = BASE / "1_DT47.xml"
XLSX_PATH = BASE / "6_DT47_validated.xlsx"
OUT_PATH = BASE / "7_DT47_enriched.xml"

# ---------- 1. Charger l’Excel : id → info ----------

df = pd.read_excel(XLSX_PATH, dtype={"id": str, "insee_code": str})
df["id"] = df["id"].astype(str).str.strip()

info_by_row = {}
for _, row in df.iterrows():
    # id Excel = DT47-00001, DT47-00002, ...
    art_id = row["id"]
    if not isinstance(art_id, str):
        continue
    info_by_row[art_id] = {
        "is_commune": bool(row["is_commune"]),
        "insee_code": (str(row["insee_code"]).strip()
                       if pd.notna(row["insee_code"]) else None),
        "NCCENR": (str(row["NCCENR"]).strip()
                   if pd.notna(row["NCCENR"]) else None),
    }

# ---------- 2. Charger l’XML ----------

tree = ET.parse(XML_PATH)
root = tree.getroot()

# ---------- 3. Parcourir les <article> dans l’ordre et appliquer les règles ----------

counter = 1
for art in root.findall(".//article"):
    # 1) Assigner id + type="commune" si is_commune=VRAI

    excel_id = f"DT47-{counter:05d}"
    art_info = info_by_row.get(excel_id)
    if art_info is None:
        counter += 1
        continue

    is_commune = art_info["is_commune"]
    insee_code = art_info["insee_code"]

    if is_commune:
        # id et type
        art.set("id", excel_id)
        art.set("type", "commune")

        # 2) Ajouter <insee> à la fin de l’article
        if insee_code:
            if art.find("insee") is None:
                insee_el = ET.Element("insee")
                insee_el.text = insee_code
                art.append(insee_el)

    else:
        # pour les non‑communes, on met quand même l'id, sans type
        art.set("id", excel_id)

        # 3) Ajouter insee dans <localisation> → <commune ...>
        if insee_code:
            loc_el = art.find("./definition/localisation")
            if loc_el is not None:
                com_el = loc_el.find("./commune")
                if com_el is not None:
                    com_el.set("insee", insee_code)
                    if "precision" not in com_el.attrib:
                        com_el.set("precision", "certain")

    counter += 1

# ---------- 4. Sauvegarde ----------

tree.write(OUT_PATH, encoding="utf-8", xml_declaration=True)
print(f"Écrit : {OUT_PATH}")
