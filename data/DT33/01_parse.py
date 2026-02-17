import xml.etree.ElementTree as ET
from pathlib import Path
import pandas as pd

XML_PATH = Path("ref_DT33.xml")

def parse_dt33(path: Path):
    tree = ET.parse(path)
    root = tree.getroot()
    for art in root.findall(".//article"):
        art_id = art.get("id", "").strip()
        vedette_el = art.find("./vedette/sm")
        vedette = (vedette_el.text or "").strip() if vedette_el is not None else ""
        loc_el = art.find("./definition/localisation")
        localisation = (loc_el.text or "").strip() if loc_el is not None else ""
        is_commune = "commune" not in localisation.lower()
        yield {
            "id": art_id,
            "is_commune": is_commune,
            "vedette": vedette,
            "localisation": localisation,
        }

if __name__ == "__main__":
    rows = list(parse_dt33(XML_PATH))
    df = pd.DataFrame(rows)
    out_path = Path(__file__).with_name("01_DT33_parsed.xlsx")
    df.to_excel(out_path, index=False)   # creates DT33_export.xlsx in same folder as script [web:29][web:38]
    print(f"Written: {out_path}")
