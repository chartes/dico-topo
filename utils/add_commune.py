import xml.etree.ElementTree as ET
import re
import csv

def add_commune (localisation):
    """
    Ajout la balise commune pour les phrases ou la dernière entrée est cette commune
    :param localisation: contient les informations de la balise localisation du fichier xml
    :return:
    """
    commune = localisation.text.split()
    #localisation.text = "commune de "
    localisation.text = ' '.join(commune[:-1])+" "
    newcommune = ET.SubElement(localisation,"commune")
    newcommune.text = commune[-1]


def add_commune_d (localisation):
    """
    Ajout de la balise commune quand le mot est à la dernière place et séparé par un apostrophe
    :param localisation: contient les informations de la balise localisation du fichier xml
    :return:
    """
    commune = localisation.text.split("’")
    localisation.text = commune[0]+"’"
    newcommune = ET.SubElement(localisation,"commune")
    newcommune.text = commune[1]


def add_communes (localisation):
    """

    :param localisation: contient les informations de la balise localisation du fichier xml
    :return:
    """
     #divise le string si le caractère n'est pas une lettre majuscule et minuscule, accentué ou non ou un tiret
    co = re.split('([^a-zA-Z0-9À-ÿ\)\-])', localisation.text)
    localisation.text = ""
     #Ajout de la balise div dans la phrase final pour permettre un ajout aisé de la modification directement dans la balise localisation
    phrase = "<div>"
    for mot in co:
        try:
            testadd = mot[0].isupper() and ")" not in mot
        except:
            phrase = phrase + mot
        if testadd is True:
            phrase = phrase + "<commune>" + mot + "</commune>"
        else :
            phrase = phrase + mot
    phrase = phrase + "</div>"
     #Transforme phrase avec l'ensemble des informations en balise xml puis l'ajoute dans localisation. Il faudra supprimer les balises <div> et </div> dans le fichier final
    phrasexml = ET.fromstring(phrase)
    localisation.append(phrasexml)

def check_commune (localisation, d, article):
    """

    :param localisation: contient les informations de la balise localisation du fichier xml
    :param d: dictionnaire clé nom commune, valeur code insee
    :param article: valeur de l'article
    :return:
    """
    valide = False
    for nom, insee in d.items():
        if nom == localisation.text:
            localisation.text = ""
            newcommune = ET.SubElement(localisation,"commune", insee=insee, precision="certain")
            newcommune.text = nom
            valide = True
    if valide is not True :
        print(article.attrib, localisation.text)


tree= ET.parse("/home/corentink/Bureau/Dicotopo/DT44/DT44.xml")
xml = tree.getroot()
nbalone = 0
nbcommune = 0
nbelement = 0
nb = 0
d = {}
 #Crée un dictionnaire qui contient le nom et le code insee pour chaque commune du dictionnaire
with open("/home/corentink/Bureau/Dicotopo/DT44/FichierCorrection", newline='') as csvfile:
    ListcommunesInsee = csv.reader(csvfile, delimiter='{', quotechar='|')
    for communeInsee in ListcommunesInsee :
        commune = communeInsee[1].split()
        d[commune[0]] = communeInsee[4]

for article in xml:
    for balises in article :
        if balises.tag == "definition":
            for localisation in balises :
                if localisation.tag == "localisation":
                    if "commune de" in localisation.text or "commune du" in localisation.text or "arrondissement de" in localisation.text or "canton de" in localisation.text or "canton du" in localisation.text or "village de" in localisation.text or "ville de" in localisation.text or "ville du" in localisation.text:
                        add_commune(localisation)
                    elif "commune d’" in localisation.text or "ville d’" in localisation.text or "village d’" in localisation.text or "arrondissement d’" in localisation.text or "canton d’" in localisation.text:
                        add_commune_d(localisation)
                    elif "communes" in localisation.text or "arrondissements" in localisation.text or "cantons" in localisation.text:
                        add_communes(localisation)
                    else :
                        if len(localisation.text.split()) == 1:
                            check_commune(localisation, d, article)
                            nbalone = nbalone + 1
                        else :
                            print(article.attrib, localisation.text)
                            nb = nb +1

tree.write("output2.xml",encoding="UTF-8",xml_declaration=True)



