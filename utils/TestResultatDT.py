import xml.etree.ElementTree as ET
from lxml import etree
import csv

dep = "89"

path_file_in = "/home/corentink/Bureau/Dicotopo/Tableau_Correction/DT"
path_file_out = "/home/corentink/Bureau/Dicotopo/dico-topo/data/DT"
path_result = "/home/corentink/Bureau/Dicotopo/Tableau_Correction/"

file_in = "DT89.xml"
file_out ="output5.xml"
file_result = "result"

tree_original = etree.parse("{0}{1}/{2}".format(path_file_in, dep, file_in))
tree = etree.parse("{0}{1}/{2}".format(path_file_out, dep, file_out))

#compte le nombre d'article dans le fichier xml
count_article_in = 0
count_article_out = 0
for article in tree_original.xpath("article"):
    count_article_in += 1
for article in tree.xpath("article"):
    count_article_out += 1

#Compte le nombre de vedette
count_vedette_in = 0
count_vedette_out = 0
for article in tree_original.xpath("//vedette/sm"):
    count_vedette_in += 1
for article in tree.xpath("//vedette/sm"):
    count_vedette_out += 1

#compte le nombre d'article commune
count_insee_in = 0
count_insee_out = 0
for commune in tree_original.xpath("//insee"):
    count_insee_in += 1
for article in tree.xpath("//insee"):
    count_insee_out += 1

#compte me nombre de commune avec l'article insee
commune_insee_in = 0
commune_insee_out = 0
for commune in tree_original.xpath("//commune/@insee"):
    commune_insee_in += 1
for article in tree.xpath("//commune/@insee"):
    commune_insee_out += 1

#Compte le nombre d'article_not_found (doit être à 0 pour la sortie)
article_not_found_in = 0
article_not_found_out = 0
for commune in tree_original.xpath("//commune[@insee='article_not_found']"):
    article_not_found_in += 1
for article in tree.xpath("//commune[@insee='article_not_found']"):
    article_not_found_out += 1

#Compte le nombre de commentaire pour voir si on en a pas perdu
commentary_in = 0
commentary_out = 0
for commune in tree_original.xpath("//commentary"):
    commentary_in += 1
for article in tree.xpath("//commentary"):
    commentary_out += 1

#Compte le nombre de formes anciennes, on ne doit pas en perdre
forme_ancienne_in = 0
forme_ancienne_out = 0
for commune in tree_original.xpath("//forme_ancienne"):
    forme_ancienne_in += 1
for article in tree.xpath("//forme_ancienne"):
    forme_ancienne_out += 1

#Compte le nombre de description, on ne doit pas en perdre
description_in = 0
description_out = 0
for commune in tree_original.xpath("//description"):
    description_in += 1
for article in tree.xpath("//description"):
    description_out += 1

#Compte le nombre de typologie, on ne doit pas en perdre
typologie_in = 0
typologie_out = 0
for commune in tree_original.xpath("//typologie"):
    typologie_in += 1
for article in tree.xpath("//typologie"):
    typologie_out += 1

#Compte le nombre d'article sans forme_ancienne
article_not_forme_ancienne_in = 0
article_not_forme_ancienne_out = 0
for commune in tree_original.xpath("//article[not(forme_ancienne)]"):
    article_not_forme_ancienne_in += 1
for article in tree.xpath("//article[not(forme_ancienne)]"):
    article_not_forme_ancienne_out += 1

#Vérifie que tous les articles ont un id
article_not_id_in = 0
article_not_id_out = 0
for commune in tree_original.xpath("//article[not(@id)]"):
    article_not_id_in += 1
for article in tree.xpath("//article[not(@id)]"):
    article_not_id_out += 1

#Vérifie que tous les id sont uniques dans un fichier
id_unique_in = 0
id_unique_out = 0
num_id = ""
num_id_out = ""
for commune in tree_original.xpath("//article/@id"):
    if num_id == commune :
        print(commune)
    else:
        num_id = commune
for article in tree.xpath("//article/@id"):
    if num_id_out == article :
        print(article)
    else:
        num_id_out = article

#Créer un fichier csv avec les différents résultats
with open("{0}{1}{2}.csv".format(path_result, file_result, dep), "w") as csvfile:
    ListresultatTest = csv.writer(csvfile)
    ListresultatTest.writerow (["", "DT_input", "DT_output(CF)"])
    ListresultatTest.writerow (["place(article)", count_article_in, count_article_out])
    ListresultatTest.writerow (["place.label(//vedette/sm)", count_vedette_in, count_vedette_out])
    ListresultatTest.writerow (["place.commune_insee_code(//insee)", count_insee_in, count_insee_out])
    ListresultatTest.writerow (["place.localization_commune_insee_code(//commune/@insee)", commune_insee_in, commune_insee_out])
    ListresultatTest.writerow(["codes insee non résolu(//commune[@insee='article_not_found'])", article_not_found_in, article_not_found_out])
    ListresultatTest.writerow(["place_comment.content (//commentaire)", commentary_in, commentary_out])
    ListresultatTest.writerow(["place_old_label (//forme_ancienne)", forme_ancienne_in, forme_ancienne_out])
    ListresultatTest.writerow(["place_description.content (//description)", description_in, description_out])
    ListresultatTest.writerow(["place_feature_type.term(//typologie)", typologie_in, typologie_out])
    ListresultatTest.writerow(["place sans forme ancienne(//article[not(forme_ancienne)]) – total", article_not_forme_ancienne_in, article_not_forme_ancienne_out])
    ListresultatTest.writerow(["place sans forme ancienne(//article[not(forme_ancienne)]) – %", article_not_forme_ancienne_in/count_article_in, article_not_forme_ancienne_out/count_article_out])
    ListresultatTest.writerow(["article sans id (//article[not(@id)])",article_not_id_in, article_not_id_out])
