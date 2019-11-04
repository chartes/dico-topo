import xml.etree.ElementTree as ET
import csv

d = {}
#Crée un dictionnaire qui contient le numéro de l'article en clé à corriger et en valeur le code INSEE et le texte contenu dans la balise commune
with open("/home/corentink/Bureau/Dicotopo/Dossier_correction/DT44/DT44_EchecCommune_revuSN-3.csv", newline='') as csvfile:
    ListcommunesInsee = csv.reader(csvfile, delimiter='\t', quotechar='|')
    for communeInsee in ListcommunesInsee :
        if communeInsee[4] == "" :
           continue
        d[communeInsee[0]] = communeInsee[4], communeInsee[3]
tree= ET.parse("/home/corentink/Bureau/Dicotopo/Dossier_correction/DT44/output4.xml")
xml = tree.getroot()
#Liste qui doit contenir les informations des communes pour pouvoir contrôler les échecs de correspondance
controleList = []
n = 0
nb = 0

print(d)
for article in xml :
    NumArticle = article.attrib.get("id")
    for balises in article:
        if balises.tag == "definition":
            for localisation in balises :
                if localisation.tag == "localisation":
                    typologie = localisation.text
                for commune in localisation :
                    if commune.tag == "commune":
                        for NArticle, Rest in d.items():
                            if NArticle == NumArticle and Rest[1] == commune.text:
                                commune.set('insee',Rest[0])

tree.write("/home/corentink/Bureau/Dicotopo/Dossier_correction/DT44/output5.xml",encoding="UTF-8",xml_declaration=True)

print(n)
