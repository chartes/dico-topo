"""
Joins DT33_kepler.csv with official French commune polygon boundaries
and outputs a GeoJSON ready to drag into Kepler.gl.

Requirements:
    pip install requests geopandas

Usage:
    python make_kepler_geojson.py
"""

import json
import csv
import urllib.request
from pathlib import Path
from collections import defaultdict

INPUT_CSV = "DT66_kepler.csv"
OUTPUT_GEOJSON = "DT66_kepler_polygons.geojson"

# Official French communes GeoJSON — département 33 only (lighter file)
# Uses geo.api.gouv.fr public API — no account needed
COMMUNES_URL = (
    "https://geo.api.gouv.fr/departements/66/communes"
    "?fields=code,nom,contour&format=geojson&geometry=contour"
)


def fetch_communes_geojson(url):
    print("Downloading commune boundaries from geo.api.gouv.fr …")
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read().decode())
    print(f"  → {len(data['features'])} communes downloaded")
    return data


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_commune_index(geojson):
    """Index commune polygons by INSEE code."""
    index = {}
    for feature in geojson["features"]:
        code = feature["properties"].get("code")
        if code:
            index[code] = feature["geometry"]
    return index


def group_by_commune(rows):
    """Group CSV rows by INSEE code, collecting vedette lists."""
    grouped = defaultdict(lambda: {"vedettes": [], "types": set()})
    for row in rows:
        insee = row["insee"].strip()
        if not insee:
            continue
        g = grouped[insee]
        if row.get("vedette"):
            g["vedettes"].append(row["vedette"])
        if row.get("type"):
            g["types"].add(row["type"])
        # Keep scalar fields from first row
        g.setdefault("NCCENR", row.get("NCCENR", ""))
        g.setdefault("insee", insee)
    return grouped


def build_geojson(commune_index, grouped):
    features = []

    for insee, data in grouped.items():
        geom = commune_index.get(insee)
        if geom is None:
            print(f"  ⚠ No geometry found for INSEE {insee}")
            continue

        features.append({
            "type": "Feature",
            "geometry": geom,
            "properties": {
                "insee": insee,
                "commune": data["NCCENR"],
                "nb_entries": len(data["vedettes"]),
                "vedettes": " | ".join(data["vedettes"][:50]),  # cap to avoid huge strings
                "has_commune_article": "commune" in data["types"],
            },
        })

    return {"type": "FeatureCollection", "features": features}


def main():
    rows = load_csv(INPUT_CSV)
    print(f"Loaded {len(rows)} rows from {INPUT_CSV}")

    communes_geojson = fetch_communes_geojson(COMMUNES_URL)
    commune_index = build_commune_index(communes_geojson)

    grouped = group_by_commune(rows)
    print(f"Found {len(grouped)} distinct INSEE codes in CSV")

    result = build_geojson(commune_index, grouped)
    print(f"Built {len(result['features'])} polygon features")

    with open(OUTPUT_GEOJSON, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Saved → {OUTPUT_GEOJSON}")
    print("  Drag this file into kepler.gl to visualize commune polygons.")
    print("  Suggested layer: Fill color by 'nb_entries' (choropleth).")


if __name__ == "__main__":
    main()