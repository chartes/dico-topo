import csv
import xml.etree.ElementTree as ET

INPUT_FILE = "output7.xml"
OUTPUT_FILE = "output7_parsed.csv"

def get_text(element):
    return "".join(element.itertext()).strip()

def get_vedette(article):
    vedette_el = article.find("vedette")
    if vedette_el is None:
        return ""
    # Always use the first <sm> if present, ignoring <pg> and other content
    first_sm = vedette_el.find("sm")
    if first_sm is not None:
        return get_text(first_sm).strip()
    # Fallback: full text minus any <pg> content
    for pg in vedette_el.findall("pg"):
        pg.text = ""
    return get_text(vedette_el).rstrip(",").strip()

def parse_xml(input_path, output_path):
    tree = ET.parse(input_path)
    root = tree.getroot()
    rows = []

    for article in root.findall(".//article"):
        article_id = article.get("id", "")
        vedette = get_vedette(article)

        definition = article.find("definition")
        typologies = []
        communes = []

        if definition is not None:
            for typo_el in definition.findall("typologie"):
                typologies.append(get_text(typo_el))
            localisation = definition.find("localisation")
            if localisation is not None:
                for commune_el in localisation.findall("commune"):
                    insee = commune_el.get("insee", "")
                    commune_name = get_text(commune_el)
                    communes.append((commune_name, insee))

        typologie_str = " ; ".join(typologies)
        article_type = typologie_str if typologie_str else ""

        insee_el = article.find("insee")
        if insee_el is not None:
            rows.append({
                "id": article_id, "commune_dt": vedette,
                "insee": get_text(insee_el), "type": article_type,
                "vedette": vedette, "typologie": typologie_str,
            })
        elif communes:
            for commune_name, insee in communes:
                rows.append({
                    "id": article_id, "commune_dt": commune_name,
                    "insee": insee, "type": article_type,
                    "vedette": vedette, "typologie": typologie_str,
                })
        else:
            rows.append({
                "id": article_id, "commune_dt": "",
                "insee": "", "type": article_type,
                "vedette": vedette, "typologie": typologie_str,
            })

    fieldnames = ["id", "commune_dt", "insee", "type", "vedette", "typologie"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Done — {len(rows)} rows written to {output_path}")

if __name__ == "__main__":
    parse_xml(INPUT_FILE, OUTPUT_FILE)