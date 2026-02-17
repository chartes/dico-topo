from pathlib import Path
import re
import pandas as pd

XML_PATH = Path("src_DT03.XML")
OUT_XLSX = Path("01_DT03_parsed.xlsx")


def is_localisation_commune(loc: str) -> bool:
    if not loc:
        return False
    txt = loc.lower().lstrip()
    return txt.startswith("commune ")


def parse_dt03_text(path: Path):
    txt = path.read_text(encoding="utf-8", errors="replace")

    # Keep the original XML id
    article_pattern = re.compile(
        r'<article[^>]*id="([^"]+)"[^>]*>(.*?)</article>',
        re.DOTALL
    )

    for xml_id, body in article_pattern.findall(txt):
        # --- vedette ---
        m_v = re.search(r'<vedette>(.*?)</vedette>', body, re.DOTALL)
        vedette = ""
        if m_v:
            raw_v = m_v.group(1)
            raw_v = re.sub(r'<pg>.*?</pg>', '', raw_v, flags=re.DOTALL)
            vedette = re.sub(r'<[^>]+>', '', raw_v)
            vedette = vedette.replace("\n", " ").strip().rstrip(",")

        # --- typologie presence ---
        m_t = re.search(r'<typologie>(.*?)</typologie>', body, re.DOTALL)
        has_typologie = m_t is not None

        # --- localisation (may be empty) ---
        m_l = re.search(r'<localisation>(.*?)</localisation>', body, re.DOTALL)
        localisation = ""
        if m_l:
            raw_l = m_l.group(1)
            localisation = re.sub(r'<[^>]+>', '', raw_l)
            localisation = localisation.replace("\n", " ").strip().rstrip(".")

        starts_with_commune = is_localisation_commune(localisation)
        is_commune = (not has_typologie) and (not starts_with_commune)

        yield {
            "id": xml_id,            # preserve original id, e.g. DT03-13225
            "is_commune": is_commune,
            "vedette": vedette,
            "localisation": localisation,
        }


if __name__ == "__main__":
    rows = list(parse_dt03_text(XML_PATH))
    df = pd.DataFrame(rows)
    df.to_excel(OUT_XLSX, index=False)
    print(f"Written: {OUT_XLSX}")
    print(f"Rows: {len(df)}")
