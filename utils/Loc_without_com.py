from lxml import etree
import re
import csv
import unidecode
from bs4 import BeautifulSoup
dep = "60"
dir_path = "/home/corentink/Bureau/Dicotopo/Tableau_Correction/"
file_in = dir_path + "DT" + dep + "/output4.xml"
file_correction = dir_path + "DT" + dep+ "/DT" + dep + "_liageINSEE_localisation-commune-desambiguisation_2.csv"
#Donner l'emplacement du fichier XML du dictionnaire à utiliser pour la recherche
tree= etree.parse(file_in)
child_commune = False
list_desamb = []

#
for article in tree.xpath("//article"):
    for vedette in article.xpath(".//vedette"):
        ved = vedette.text
    for definition in article.xpath(".//definition"):
        defini = etree.tostring(definition, method="text", encoding=str)
        for typologie in definition.xpath(".//typologie"):
            typ = typologie.text
        for localisation in definition.xpath(".//localisation"):
            child_commune = False
            loc = etree.tostring(localisation, method="text", encoding=str)
            #Essaye de voir s'il y a un child commune à localisation si non ajoute les infos dans un tableau de correction
            try:
                for com in localisation.xpath(".//commune"):
                    child_commune = True
            except:
                child_commune = False
            if child_commune == False:
                list_desamb.append([article.get('id'), ved, typ, loc," " ,defini])
        #print((etree.tostring(vedette, method="text", encoding=str)))
print(list_desamb)

#Crée le fichier csv des fichiers localisations dans lequelles on ne peut pas garantir la présence d'une commune
with open(file_correction, "w") as csvfile:
    Listcommunerest= csv.writer(csvfile)
    Listcommunerest.writerow(['Article', 'Vedette', 'Type vedette', 'Candidat', 'INSEE', 'Définition'])
    testDefinition= ""
    for communerest in list_desamb :
        Listcommunerest.writerow(communerest)


