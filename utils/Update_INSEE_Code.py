import xml.etree.ElementTree as ET
import csv
import re

d = {}
#Crée un dictionnaire qui contient le numéro de l'article en clé à corriger et en valeur le code INSEE et le texte contenu dans la balise commune
with open("/home/corentink/Bureau/Dicotopo/Dossier_correction/DT44/DT44_LocalisationEchec_revuSN-2.csv", newline='') as csvfile:
    ListcommunesInsee = csv.reader(csvfile, delimiter='\t', quotechar='|')
    for communeInsee in ListcommunesInsee :
        if communeInsee[3] == "":
            continue
        d[communeInsee[0]] = communeInsee[3], communeInsee[4]
print(d)
tree= ET.parse("/home/corentink/Bureau/Dicotopo/Dossier_correction/DT44/output3.xml")
xml = tree.getroot()
#Liste qui doit contenir les informations des communes pour pouvoir contrôler les échecs de correspondance
controleList = []
n = 0
nb = 0


for article in xml :
    NumArticle = article.attrib.get("id")
    for balises in article:
        if balises.tag == "vedette":
            for sm in balises :
                if sm.tag =="sm":
                    vedette = sm.text
        if balises.tag == "definition":
            for localisation in balises :
                if localisation.tag == "localisation":
                    typologie = localisation.text
                    for NArticle, Rest in d.items():
                        if NArticle == NumArticle and Rest[1] == typologie:
                            #divise le string si le caractère n'est pas une lettre majuscule et minuscule, accentué ou non ou un tiret
                            co = re.split('([^a-zA-Z0-9À-ÿ\)\-])', localisation.text)
                            localisation.text = ""
                             #Ajout de la balise div dans la phrase final pour permettre un ajout aisé de la modification directement dans la balise localisation
                            phrase = "<tmp>"
                            for mot in co:
                                try:
                                    testadd = mot[0].isupper() and ")" not in mot
                                except:
                                    phrase = phrase + mot
                                if testadd is True:
                                    phrase = phrase + "<commune>" + mot + "</commune>"
                                else :
                                    phrase = phrase + mot
                            phrase = phrase + "</tmp>"
                            phrasexml = ET.fromstring(phrase)
                            for commune in phrasexml.iter("commune"):
                                commune.set('insee', Rest[0])
                            localisation.append(phrasexml)
                             #Transforme phrase avec l'ensemble des informations en balise xml puis l'ajoute dans localisation. Il faudra supprimer les balises <div> et </div> dans le fichier final


tree.write("/home/corentink/Bureau/Dicotopo/Dossier_correction/DT44/output4.xml",encoding="UTF-8",xml_declaration=True)
