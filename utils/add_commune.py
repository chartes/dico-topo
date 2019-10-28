import xml.etree.ElementTree as ET
import re
import csv
import unicodedata

def add_commune (localisation, precision):
    """
    Ajout la balise commune pour les phrases ou la dernière entrée est cette commune
    :param localisation: contient les informations de la balise localisation du fichier xml
    :return:
    """
    commune = localisation.text.split()
    localisation.text = ' '.join(commune[:-1])+" "
    newcommune = ET.SubElement(localisation,"commune", precision=precision)
    newcommune.text = commune[-1]


def add_commune_d(localisation, precision):
    """
    Ajout de la balise commune quand le mot est à la dernière place et séparé par un apostrophe
    :param localisation: contient les informations de la balise localisation du fichier xml
    :return:
    """
    commune = localisation.text.split("’")
    localisation.text = commune[0]+"’"
    newcommune = ET.SubElement(localisation,"commune", precision=precision)
    newcommune.text = commune[-1]

def add_communes (localisation, precision):
    """

    :param localisation: contient les informations de la balise localisation du fichier xml
    :return:
    """
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
     #Transforme phrase avec l'ensemble des informations en balise xml puis l'ajoute dans localisation. Il faudra supprimer les balises <div> et </div> dans le fichier final
    phrasexml = ET.fromstring(phrase)
    phrasexml.set('precision', precision)
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
            newcommune = ET.SubElement(localisation,"commune", insee=insee, precision="approximatif")
            newcommune.text = nom
            valide = True
    if valide is not True :
        print(article.attrib, localisation.text)

#Donner l'emplacement du fichier XML du dictionnaire à utiliser pour la recherche
tree= ET.parse("/home/corentink/Bureau/Dicotopo/DT44/DT44.xml")
xml = tree.getroot()
#Changer nom variable en indice commune précise
listOfCommuneIndiceP = ["commune de", "commune du", "ville de"]
listOfCommunedIndiceP = ["commune d’", "ville d’"]
listofComumunesIndiceU = ["arrondissements", "cantons"]
listofCommuneIndiceU = ["arrondissement de", "canton de", "canton du" ]
listofCommunedIndiceU = ["arrondissement d'", "canton d'" ]
nb = 0
d = {}
 #Crée un dictionnaire qui contient le nom et le code insee pour chaque commune du dictionnaire
with open("/home/corentink/Bureau/Dicotopo/Dossier_correction/DT44.csv", newline='') as csvfile:
    ListcommunesInsee = csv.reader(csvfile, delimiter=',', quotechar='|')
    for communeInsee in ListcommunesInsee :
        nCommune = unicodedata.normalize('NFKD',communeInsee[1]).encode('ascii','ignore').decode('utf-8')
        d[nCommune] = communeInsee[5]

#Utilisation de boucle for imbriqué pour pouvoir avoir accès à chaque niveau de l'information et faire les exports les plus précis possible
for article in xml:
    for balises in article :
        if balises.tag == "definition":
            for localisation in balises :
                if localisation.tag == "localisation":
                    nb = nb +1
                    for testCommune in listOfCommuneIndiceP  :
                        if testCommune in localisation.text :
                            add_commune(localisation, precision="certain")
                    for testCommune in listOfCommunedIndiceP :
                        if testCommune in localisation.text :
                            add_commune_d(localisation, precision="certain")
                    for testCommune in listofCommuneIndiceU :
                        if testCommune in localisation.text :
                            add_commune(localisation, precision="approximatif")
                    for testCommune in listofComumunesIndiceU :
                        if testCommune in localisation.text :
                            add_communes(localisation, precision="approximatif")

n = 0

tree.write("output2.xml",encoding="UTF-8",xml_declaration=True)



