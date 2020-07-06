import xml.etree.ElementTree as ET
from lxml import etree
import csv

dep = "07"

dir_path = "../data/"
file_in = dir_path+"DT"+dep+"/DT"+dep+".xml"
file_out = dir_path+"DT"+dep+"/output5.xml"
file_result = "out/DT"+dep+"_result.csv"


tree_original = etree.parse(file_in)
tree = etree.parse(file_out)

"""
# sortir les alt labels
for vedette in tree.xpath("//vedette[.//sm[position() > 1]]"):
    print(etree.tostring(vedette, method="xml", encoding=str))
exit()
"""

#compte le nombre d'article dans le fichier xml
count_article_in = 0
count_article_out = 0
for article in tree_original.xpath("article"):
    count_article_in += 1
for article in tree.xpath("article"):
    count_article_out += 1

#Vérifier que le nombre de charactère d'un label soit inférieur à 30
count_long_vedette_in = 0
count_long_vedette_out = 0
for article in tree_original.xpath("//article"):
    for com in article.xpath(".//vedette//sm"):
        if len(etree.tostring(com, method="text", encoding=str)) > 31:
            print("in : " + article.get('id')+ " " + com.text)
            count_long_vedette_in += 1
for article in tree.xpath("//article"):
    for com in article.xpath(".//vedette//sm"):
        if len(etree.tostring(com, method="text", encoding=str)) > 31:
            count_long_vedette_out += 1
            print("out:" + article.get('id') + " " + etree.tostring(com, method="text", encoding=str))

#Compte le nombre de vedette
count_vedette_in = 0
count_vedette_out = 0
for article in tree_original.xpath("//vedette//sm"):
    count_vedette_in += 1
for article in tree.xpath("//vedette//sm"):
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
for commune in tree_original.xpath("//commentaire"):
    commentary_in += 1
for article in tree.xpath("//commentaire"):
    commentary_out += 1

#Compte le nombre de formes anciennes, on ne doit pas en perdre
forme_ancienne_in = 0
forme_ancienne_out = 0
for commune in tree_original.xpath("//forme_ancienne"):
    forme_ancienne_in += 1
for article in tree.xpath("//forme_ancienne"):
    forme_ancienne_out += 1

#Compte le nombre de definition, on ne doit pas en perdre
definition_in = 0
definition_out = 0
for commune in tree_original.xpath("//definition"):
    definition_in += 1
for article in tree.xpath("//definition"):
    definition_out += 1

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

#Controle que toutes les communes sont plus gros que 2
count_commune_len_in = 0
count_commune_len_out = 0
for article in tree_original.xpath("//article"):
    for com in article.xpath(".//commune"):
        if len(etree.tostring(com, method="text", encoding=str)) < 3:
            print("in:" + article.get('id') + etree.tostring(com, method="text", encoding=str))
for article in tree.xpath("//article"):
    for com in article.xpath(".//commune"):
        if len(etree.tostring(com, method="text", encoding=str)) < 3:
            print("out:" + article.get('id') + etree.tostring(com, method="text", encoding=str))
#Controle que les valeurs de localisation sont identiques
count_localisation_ok = 0
list_localisation_in = []
list_localisation_out =[]
dict_localisation_in = {}
for article in tree_original.xpath("//article"):
    count_loc = 0
    for loc in article.xpath(".//localisation"):
        count_loc += 1
        dict_localisation_in[article.get('id')+"-"+str(count_loc)] = etree.tostring(loc, method="text", encoding=str).replace("’","'").replace("\n","")
        list_localisation_in.append([article.get('id')+"-"+str(count_loc),etree.tostring(loc, method="text", encoding=str).replace("’","'").replace("\n","")])

for article in tree.xpath("//article"):
    count_loc = 0
    for loc in article.xpath(".//localisation"):
        count_loc += 1
        if etree.tostring(loc, method="text", encoding=str).replace("\n","").replace("’","'") == dict_localisation_in[article.get('id')+"-"+str(count_loc)]:
            continue
        else:
            count_localisation_ok += 1
            list_localisation_out.append([article.get('id'),etree.tostring(loc, method="text", encoding=str), dict_localisation_in[article.get('id')+"-"+str(count_loc)]])

count_sup_out = 0
#Controle que les vedettes  ne contiennet pas St ou S<sup>t
for article in tree.xpath("//article"):
    count_sup_out += 1
    for sup in article.xpath(".//sm/sup"):
        if "t" in sup.text :
            print("problème de sup: ",article.get('id'))
    for su in article.xpath(".//sm"):
        if "St-" in etree.tostring(su, method="text", encoding=str):
            print("problème ST : ", article.get("id"))
        elif "St " in etree.tostring(su, method="text", encoding=str):
            print("problème ST : ", article.get("id"))



#Créer un fichier csv avec les différents résultats
with open(file_result, "w") as csvfile:
    ListresultatTest = csv.writer(csvfile)
    ListresultatTest.writerow (["", "DT_input", "DT_output(CF)"])
    ListresultatTest.writerow (["place(article)", count_article_in, count_article_out])
    ListresultatTest.writerow (["place.label(//vedette/sm)", count_vedette_in, count_vedette_out])
    ListresultatTest.writerow (["place.label(//sm) > 30", count_long_vedette_in, count_long_vedette_out])
    ListresultatTest.writerow (["place.commune_insee_code(//insee)", count_insee_in, count_insee_out])
    ListresultatTest.writerow (["place.localization_commune_insee_code(//commune/@insee)", commune_insee_in, commune_insee_out])
    ListresultatTest.writerow(["codes insee non résolu(//commune[@insee='article_not_found'])", article_not_found_in, article_not_found_out])
    ListresultatTest.writerow(["place_comment.content (//commentaire)", commentary_in, commentary_out])
    ListresultatTest.writerow(["place_old_label (//forme_ancienne)", forme_ancienne_in, forme_ancienne_out])
    ListresultatTest.writerow(["place_description.content (//definition)", definition_in, definition_out])
    ListresultatTest.writerow(["place_feature_type.term(//typologie)", typologie_in, typologie_out])
    ListresultatTest.writerow(["place sans forme ancienne(//article[not(forme_ancienne)]) – total", article_not_forme_ancienne_in, article_not_forme_ancienne_out])
    ListresultatTest.writerow(["place sans forme ancienne(//article[not(forme_ancienne)]) – %", article_not_forme_ancienne_in/count_article_in, article_not_forme_ancienne_out/count_article_out])
    ListresultatTest.writerow(["article sans id (//article[not(@id)])",article_not_id_in, article_not_id_out])

#Renvoie un fichier csv des localisation qui peuvent poser problème
with open("{0}_commune.csv".format(file_result), "w") as csvfile:
    ListCommuneResult = csv.writer(csvfile)
    ListCommuneResult.writerow(["article", "ProblemeLocalisation ?"])
    for com in list_localisation_out :
        ListCommuneResult.writerow(com)
