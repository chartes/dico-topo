import xml.etree.ElementTree as ET
from lxml import etree
import csv

dep = "55"
tree = etree.parse("/home/corentink/Bureau/Dicotopo/Tableau_Correction/DT" + dep + "/output4.xml")
#compte le nombre d'article dans le fichier xml
count_article = 0
for article in tree.xpath("article"):
    count_article += 1
#compte le nombre d'article qui contiennent la balise insee et test si les données contenus dans chaque balise insee contiennent bien 5 caractères
count_insee = 0
count_leninsee =0
for commune in tree.xpath("//insee"):
    count_insee += 1
    if len(commune.text) != 5:
        count_leninsee += 1
#compte le nombre d'article qui ne contient pas @type = commune et une balise insee
count_notype = 0
for commune in tree.xpath("//article[not(@type='commune')]/insee") :
    count_notype += 1
#compte le nombre d'article qui ne contient pas @type = commune et une balise insee
count_noinsee = 0
for commune in tree.xpath("//article[@type='commune'][not(insee)]") :
    count_noinsee += 1
#compte le nombre d'article qui contient une balise commune avec un attribut insee non vide et qui n'est pas une commune
count_commune_insee = 0
for commune in tree.xpath("//article[not(@type='commune')]/descendant::commune[not(@insee='')][1]"):
    count_commune_insee += 1
#compte le nombre d'article qui contient balise commune où manque l'attribut insee
count_commune_inseemissing = 0
for commune in tree.xpath("//localisation/commune[not(@insee)]"):
    count_commune_inseemissing += 1
#compte le nombre d'article qui contient balise commune avec un attribut insee vide et donc invalide
count_commune_inseeempty = 0
for commune in tree.xpath("//localisation/commune[@insee='']"):
    count_commune_inseeempty += 1
#contrôle que les entrées dans les attributs insee compte bien 5 chiffres
count_invalideinsee = 0
for commune in tree.xpath("//localisation/commune/@insee"):
    if len(commune) != 5 :
        print(commune)
        count_invalideinsee += 1

#Créer un fichier csv avec les différents résultats
with open("/home/corentink/Bureau/Dicotopo/Tableau_Correction/ResultatTest/DT"+ dep +"_3.csv", "w") as csvfile:
    ListresultatTest = csv.writer(csvfile)
    ListresultatTest.writerow(["Nombre d'article", "Nombre de commune", "Code INSEE invalide", "Manque attribut type", "Manque balise insee", "Nombre article lié", "Balise commune sans attribut insee," ,"Balise commune avec attribut insee vide", "Attribut insee mal formé", "Pourcentage de réussite"])
    ListresultatTest.writerow([count_article, count_insee, count_leninsee, count_notype, count_noinsee, count_insee+count_commune_insee, count_commune_inseemissing, count_commune_inseeempty, count_invalideinsee, ((count_insee + count_commune_insee)/count_article)*100])

