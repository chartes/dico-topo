import xml.etree.ElementTree as ET
from lxml import etree
import csv
import os

# ── Configuration ──────────────────────────────────────────────────────────────
DEP            = "66"
FILE_ORIGINAL  = "DT66.xml"
FILE_ENRICHED  = "output7.xml"
OUTPUT_DIR     = "out"
# ───────────────────────────────────────────────────────────────────────────────

os.makedirs(OUTPUT_DIR, exist_ok=True)
file_result = os.path.join(OUTPUT_DIR, f"@DT{DEP}_result")

tree_original = etree.parse(FILE_ORIGINAL)
tree          = etree.parse(FILE_ENRICHED)

# Nombre d'articles
count_article_in  = len(tree_original.xpath("//article"))
count_article_out = len(tree.xpath("//article"))

# Longueur des vedettes > 30 caractères
count_long_vedette_in  = 0
count_long_vedette_out = 0
for article in tree_original.xpath("//article"):
    for com in article.xpath(".//vedette//sm"):
        if len(etree.tostring(com, method="text", encoding=str)) > 31:
            print("in : " + article.get('id') + " " + (com.text or ""))
            count_long_vedette_in += 1
for article in tree.xpath("//article"):
    for com in article.xpath(".//vedette//sm"):
        if len(etree.tostring(com, method="text", encoding=str)) > 31:
            count_long_vedette_out += 1
            print("out: " + article.get('id') + " " + etree.tostring(com, method="text", encoding=str))

# Nombre de vedettes (sm)
count_vedette_in  = len(tree_original.xpath("//vedette//sm"))
count_vedette_out = len(tree.xpath("//vedette//sm"))

# Nombre de codes insee
count_insee_in  = len(tree_original.xpath("//insee"))
count_insee_out = len(tree.xpath("//insee"))

# Communes avec attribut @insee
commune_insee_in  = len(tree_original.xpath("//commune/@insee"))
commune_insee_out = len(tree.xpath("//commune/@insee"))

# Codes insee non résolus
article_not_found_in  = len(tree_original.xpath("//commune[@insee='article_not_found']"))
article_not_found_out = len(tree.xpath("//commune[@insee='article_not_found']"))

# Commentaires
commentary_in  = len(tree_original.xpath("//commentaire"))
commentary_out = len(tree.xpath("//commentaire"))

# Formes anciennes
forme_ancienne_in  = len(tree_original.xpath("//forme_ancienne"))
forme_ancienne_out = len(tree.xpath("//forme_ancienne"))

# Définitions
definition_in  = len(tree_original.xpath("//definition"))
definition_out = len(tree.xpath("//definition"))

# Typologies
typologie_in  = len(tree_original.xpath("//typologie"))
typologie_out = len(tree.xpath("//typologie"))

# Articles sans forme ancienne
article_not_forme_ancienne_in  = len(tree_original.xpath("//article[not(forme_ancienne)]"))
article_not_forme_ancienne_out = len(tree.xpath("//article[not(forme_ancienne)]"))

# Articles sans id
article_not_id_in  = len(tree_original.xpath("//article[not(@id)]"))
article_not_id_out = len(tree.xpath("//article[not(@id)]"))

# Unicité des ids
print("\n-- Vérification unicité des ids (input) --")
seen = set()
for id_val in tree_original.xpath("//article/@id"):
    if id_val in seen:
        print(f"  Doublon: {id_val}")
    seen.add(id_val)

print("-- Vérification unicité des ids (output) --")
seen = set()
for id_val in tree.xpath("//article/@id"):
    if id_val in seen:
        print(f"  Doublon: {id_val}")
    seen.add(id_val)

# Communes dont le texte est trop court (< 3 caractères)
print("\n-- Communes trop courtes --")
for article in tree_original.xpath("//article"):
    for com in article.xpath(".//commune"):
        if len(etree.tostring(com, method="text", encoding=str)) < 3:
            print("in: " + article.get('id') + " " + etree.tostring(com, method="text", encoding=str))
for article in tree.xpath("//article"):
    for com in article.xpath(".//commune"):
        if len(etree.tostring(com, method="text", encoding=str)) < 3:
            print("out: " + article.get('id') + " " + etree.tostring(com, method="text", encoding=str))

# Contrôle des localisations
print("\n-- Contrôle des localisations --")
dict_localisation_in = {}
dict_localisation_in_affichage = {}
list_localisation_out = []

for article in tree_original.xpath("//article"):
    for count_loc, loc in enumerate(article.xpath(".//localisation"), start=1):
        key = article.get('id') + "-" + str(count_loc)
        dict_localisation_in[key] = "".join(
            etree.tostring(loc, method="text", encoding=str)
            .replace("'", "'").replace("\n", "").split()
        )

for article in tree.xpath("//article"):
    art_id = article.get('id')
    if art_id and len(art_id) == 10:
        for count_loc, loc in enumerate(article.xpath(".//localisation"), start=1):
            key = art_id + "-" + str(count_loc)
            val = "".join(
                etree.tostring(loc, method="text", encoding=str)
                .replace("'", "'").replace("\n", "").split()
            )
            ref = dict_localisation_in.get(key)
            if ref and val != ref:
                list_localisation_out.append([art_id, etree.tostring(loc, method="text", encoding=str)])

# Contrôle sup / St dans les vedettes
print("\n-- Contrôle sup/St dans les vedettes --")
for article in tree.xpath("//article"):
    for sup in article.xpath(".//sm/sup"):
        if sup.text and "t" in sup.text:
            print("problème de sup: ", article.get('id'))
    for su in article.xpath(".//sm"):
        text = etree.tostring(su, method="text", encoding=str)
        if "St-" in text or "St " in text:
            print("problème ST : ", article.get("id"))

# ── Écriture des CSV ────────────────────────────────────────────────────────────
with open(f"{file_result}.csv", "w", newline="") as csvfile:
    w = csv.writer(csvfile)
    w.writerow(["", "DT_input (src_DT53)", "DT_output (06_DT53_enriched)"])
    w.writerow(["place(article)",                                   count_article_in,              count_article_out])
    w.writerow(["place.label(//vedette/sm)",                        count_vedette_in,              count_vedette_out])
    w.writerow(["place.label(//sm) > 30",                           count_long_vedette_in,         count_long_vedette_out])
    w.writerow(["place.commune_insee_code(//insee)",                count_insee_in,                count_insee_out])
    w.writerow(["place.localization_commune_insee_code(//commune/@insee)", commune_insee_in,       commune_insee_out])
    w.writerow(["codes insee non résolu(//commune[@insee='article_not_found'])", article_not_found_in, article_not_found_out])
    w.writerow(["place_comment.content (//commentaire)",            commentary_in,                 commentary_out])
    w.writerow(["place_old_label (//forme_ancienne)",               forme_ancienne_in,             forme_ancienne_out])
    w.writerow(["place_description.content (//definition)",         definition_in,                 definition_out])
    w.writerow(["place_feature_type.term(//typologie)",             typologie_in,                  typologie_out])
    w.writerow(["place sans forme ancienne – total",                article_not_forme_ancienne_in, article_not_forme_ancienne_out])
    w.writerow(["place sans forme ancienne – %",
                round(article_not_forme_ancienne_in  / count_article_in  * 100, 2) if count_article_in  else 0,
                round(article_not_forme_ancienne_out / count_article_out * 100, 2) if count_article_out else 0])
    w.writerow(["article sans id (//article[not(@id)])",            article_not_id_in,             article_not_id_out])

print(f"\n✔  Résultats écrits dans {file_result}.csv")

with open(f"{file_result}_commune.csv", "w", newline="") as csvfile:
    w = csv.writer(csvfile)
    w.writerow(["article", "ProblemeLocalisation ?"])
    for row in list_localisation_out:
        w.writerow(row)

print(f"✔  Problèmes de localisation écrits dans {file_result}_commune.csv")
