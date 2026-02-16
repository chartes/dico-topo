import xml.etree.ElementTree as ET
from pathlib import Path
import pandas as pd
import re

XML_PATH = Path("1_DT47.xml")

def normalise_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def parse_dt47(path: Path):
    tree = ET.parse(path)
    root = tree.getroot()
    counter = 1
    for art in root.findall(".//article"):
        art_id = f"DT47-{counter:05d}"

        vedette_el = art.find("./vedette/sm")
        vedette = (vedette_el.text or "").strip() if vedette_el is not None else ""

        loc_el = art.find("./definition/localisation")
        if loc_el is not None:
            # join all text, including inside <commune>
            loc_text = "".join(loc_el.itertext())
            localisation = normalise_spaces(loc_text)
        else:
            localisation = ""

        is_commune = "commune" not in localisation.lower()

        yield {
            "id": art_id,
            "is_commune": is_commune,
            "vedette": vedette,
            "localisation": localisation,
        }
        counter += 1

if __name__ == "__main__":
    rows = list(parse_dt47(XML_PATH))
    df = pd.DataFrame(rows)
    out_path = Path(__file__).with_name("DT47_export.xlsx")
    df.to_excel(out_path, index=False)  # Excel export [web:29][web:38]
    print(f"Written: {out_path}")
