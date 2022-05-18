import xml.etree.ElementTree as ET
import re
import csv
import unidecode
from bs4 import BeautifulSoup

def add_commune (localisation, precision):
    """
    Ajout la balise commune pour les phrases ou la dernière entrée est cette commune
    :param localisation: contient les informations de la balise localisation du fichier xml
    :return:
    """
    commune = localisation.text.split()
    #supprime le saut de ligne en fin de phrase qui peut gêner pour la reconnaissance du caractère par la suite
    if "\n" in commune[-1] :
        commune[-1] = commune[-1].split("\n")[0]
    #Contrôle que la dernière valeur commence par une majuscule pour qu'on soit sûr de bien récupérer le nom d'une commune
    if commune[-1][0].isupper() :
        localisation.text = ' '.join(commune[:-1])+" "
        #ajout de la balise commune
        newcommune = ET.SubElement(localisation,"commune", precision=precision)
        newcommune.text = commune[-1]
    else :
        #Sépare tous les mots à l'exception des caractères et de -
        co = re.split('([^a-zA-Z0-9À-ÿ\)\-])', localisation.text)
        localisation.text = ""
         #Ajout de la balise div dans la phrase final pour permettre un ajout aisé de la modification directement dans la balise localisation
        phrase = "<tmp>"
        testadd = False
        for mot in co:
            try:
                #Le mot peut-être considéré comme une commune s'il commence par une majuscule, si il est plus grand que 2 lettres et n'est pas Les
                testadd = mot[0].isupper() and ")" not in mot and len(mot) > 2 and "Les" not in mot
            except:
                phrase = phrase + mot
            if testadd is True:
                phrase = phrase + "<commune>" + mot + "</commune>"
            else :
                phrase = phrase + mot
        phrase = phrase + "</tmp>"
         #Transforme phrase avec l'ensemble des informations en balise xml puis l'ajoute dans localisation. Il faudra supprimer les balises <tmp> et <tmp> dans le fichier final
        phrasexml = ET.fromstring(phrase)
        localisation.append(phrasexml)


def add_commune_d(localisation, precision):
    """
    Ajout de la balise commune quand le mot est à la dernière place et séparé par un apostrophe
    :param localisation: contient les informations de la balise localisation du fichier xml
    :return:
    """
    commune = localisation.text.replace("'","’").split("’")
    #supprime le saut de ligne en fin de phrase qui peut gêner pour la reconnaissance du caractère par la suite
    if "\n" in commune[-1] :
        commune[-1] = commune[-1].split("\n")[0]
    #SI deux éléments après l'élément final, on le traite comme une communes car on doit gérer plusieurs éléments avec des majuscules
    if len(commune[-1].split()) == 2 :
        add_communes (localisation, precision=precision)
        return
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
    #Les communes qui contenait ' sont séparés par le split précédent donc on les réformes avec ce code pour éviter de compliquer la tache
    try :
        numApo = co.index("'")
        if len(co[numApo-1]) > 3:
            co[numApo-1:numApo+2] = [''.join(co[numApo-1:numApo+2])]
    except :
        pass
    #Les communes qui contenait ’ sont séparés par le split précédent donc on les réformes avec ce code pour éviter de compliquer la tache
    try :
        numApo = co.index("’")
        if len(co[numApo-1]) > 3:
            co[numApo-1:numApo+2] = [''.join(co[numApo-1:numApo+2])]
    except :
        pass
    localisation.text = ""
     #Ajout de la balise div dans la phrase final pour permettre un ajout aisé de la modification directement dans la balise localisation
    phrase = "<tmp>"
    testadd = False
    for mot in co:
        try:
            testadd = mot[0].isupper() and ")" not in mot and "Les" not in mot and len(mot) > 2
        except:
            phrase = phrase + mot
        if testadd is True:
            phrase = phrase + "<commune>" + mot + "</commune>"
        else :
            phrase = phrase + mot
    phrase = phrase + "</tmp>"
     #Transforme phrase avec l'ensemble des informations en balise xml puis l'ajoute dans localisation. Il faudra supprimer les balises <div> et </div> dans le fichier final
    phrasexml = ET.fromstring(phrase)
    for commune in phrasexml.iter("commune"):
        commune.set('precision', precision)
    localisation.append(phrasexml)

def check_commune (localisation, d, precision):
    """

    :param localisation: contient les informations de la balise localisation du fichier xml
    :param d: dictionnaire clé nom commune, valeur code insee
    :param article: valeur de l'article
    :return:
    """
    valide = False
    # Si plus grand que deux utilise la méthode de add_communes au pluriel
    if len(localisation.text.split()) == 2 :
        co = localisation.text.split()
        localisation.text = ""
         #Ajout de la balise div dans la phrase final pour permettre un ajout aisé de la modification directement dans la balise localisation
        phrase = "<tmp>"
        testadd = False
        for mot in co:
            try:
                testadd = mot[0].isupper() and ")" not in mot and len(mot) > 2 and "Les" not in mot
            except:
                phrase = phrase + mot
            if testadd is True:
                phrase = phrase + "<commune>" + mot + "</commune>"
            else :
                phrase = phrase + mot
        phrase = phrase + "</tmp>"
         #Transforme phrase avec l'ensemble des informations en balise xml puis l'ajoute dans localisation. Il faudra supprimer les balises <div> et </div> dans le fichier final
        phrasexml = ET.fromstring(phrase)
        localisation.append(phrasexml)
    else :
        nomNorm = unidecode.unidecode(localisation.text)
        nomNorm = nomNorm.strip()
        #Test si le nom est connu dans la base de dictionnaire et si oui l'ajoute avec le code INSEE
        for nom, insee in d.items():
            if nom == nomNorm:
                localisation.text = ""
                newcommune = ET.SubElement(localisation,"commune", precision=precision)
                newcommune.text = nom
                valide = True
    return valide


dep = "37"
dir_path = "../data/"
xml_entry = dir_path + "DT" + dep + "/DT" + dep + ".xml"
dict_commune_2011 = dir_path + "DT" + dep + "/DT" + dep + "_liageINSEE_article-commune.csv"
xml_out = dir_path + "DT" + dep + "/output2.xml"
tsv_out =  dir_path + "DT" + dep + "/DT" + dep + "_liageINSEE_localisation-commune-desambiguisation.csv"
#Donner l'emplacement du fichier XML du dictionnaire à utiliser pour la recherche
tree= ET.parse(xml_entry)
xml = tree.getroot()

#Changer nom variable en indice commune précise
listOfCommuneIndiceP = ["commune de", "commune du", "ville du", "ville de", "village de"]
listOfCommunedIndiceP = ["commune d’", "ville d’", "village d’", "près d’","commune d'", "ville d'", "village d'","près d'"]
listofComumunesIndiceU = ["arrondissements", "cantons"]
listofCommuneIndiceU = ["arrondissement de", "canton de", "canton du", "près de", "près du", "forêt de", "territoire de", "territoire du", "paroisse de"]
listofCommunedIndiceU = ["arrondissement d’", "canton d’", "territoire d’","canton d'","arrondissement d'", "territoire d'", "paroisse d’", "paroisse d'"]

#initialisation des variables
n= 0
rest_list = []
d = {}
test = ""
typologie = ""
savevedette = ""


 #Crée un dictionnaire qui contient le nom et le code insee pour chaque commune du dictionnaire
with open(dict_commune_2011, newline='') as csvfile:
    ListcommunesInsee = csv.reader(csvfile, delimiter='\t', quotechar='|')
    for communeInsee in ListcommunesInsee :
        #Supprime les accents pour s'assurer de la cohérence car il y a des différences d'accent entre les noms dans les corps de texte et le reste
        nCommune = unidecode.unidecode(communeInsee[1])
        d[nCommune] = communeInsee[2]

#Utilisation de boucle for imbriqué pour pouvoir avoir accès à chaque niveau de l'information et faire les exports les plus précis possible
for article in xml:
    dep = xml.attrib.get("dep")
    for balises in article :
        if balises.tag == "vedette":
            for sm in balises :
                if sm.tag =="sm":
                    vedette = sm.text
        if balises.tag == "definition":
            #Changer la méthode pour récupérer la définition, utiliser xslt pour faire un apply-templates et récupérer les données
            definition = balises.itertext()
            for localisation in balises :
                communeOk = False
                if localisation.tag == "typologie":
                    typologie = localisation.text
                    #savevedette permet de sauvegarder le nom de la vedette et quand il y a un changement d'article et pas de balise typologie, on vide la balise pour éviter les erreurs.
                    savevedette = vedette
                elif savevedette != vedette :
                    savevedette = vedette
                    typologie = ""

                if localisation.tag == "localisation":
                    n = n+1
                    if localisation.text is None:
                        continue
                    #Test si c'est une commune dont la précision est connu
                    for testCommune in listOfCommuneIndiceP  :
                        if testCommune in localisation.text :
                            add_commune (localisation, precision="certain")
                            communeOk = True
                    #Test si c'est une commune dont la précision est connu dont la séparation est d'
                    for testCommune in listOfCommunedIndiceP :
                        if testCommune in localisation.text :
                            add_commune_d (localisation, precision="certain")
                            communeOk = True
                    #Test si c'est la commune désignée est à travers un canton ou un arrondissement
                    for testCommune in listofCommuneIndiceU :
                        if testCommune in localisation.text :
                            add_commune (localisation, precision="approximatif")
                            communeOk = True
                    #Test si c'est la liste des communes désignée est à travers un canton ou un arrondissement
                    for testCommune in listofComumunesIndiceU :
                        if testCommune in localisation.text :
                            add_communes (localisation, precision="approximatif")
                            communeOk = True
                    #Test si c'est une commune dont la précision est inconnu (canton, arrondissement) dont la séparation est d'
                    for testCommune in listofCommunedIndiceU :
                        if testCommune in localisation.text :
                            add_commune_d (localisation, precision="approximatif")
                            communeOk = True
                    if communeOk == True :
                        communeOk = False
                   #Test si c'est la liste des communes désignée est à travers un canton ou un arrondissement
                    elif "communes" in localisation.text :
                        add_communes (localisation, precision="certain")
                        communeOk = False
                    #Test si le mot seul dans localisation est une commune ou non
                    elif len(localisation.text.split()) == 1 or 2 :
                        testmot = localisation.text.split()
                        if (len(testmot) == 2 and len(testmot[-1]) < 3) or len(testmot) == 1:
                            testvalide = check_commune (localisation, d, precision="certain")
                            if testvalide is not True :
                                if article.attrib.get("id") == "DT56-14845" :
                                    print(localisation.text)
                                lst = [article.attrib.get("id"), vedette, typologie, localisation.text, "", definition]
                                rest_list.append(lst)
                            communeOk = False
                        else :
                            lst = [article.attrib.get("id"), vedette, typologie, localisation.text, "", definition]
                            rest_list.append(lst)
                    #Renvoi une liste des communes sans
                    else:
                        lst = [article.attrib.get("id"), vedette, typologie, localisation.text, "",  definition]
                        rest_list.append(lst)

print(n)

#Crée le fichier csv des fichiers localisations dans lequelles on ne peut pas garantir la présence d'une commune
with open(tsv_out, "w") as csvfile:
    Listcommunerest= csv.writer(csvfile)
    Listcommunerest.writerow(['Article', 'Vedette', 'Type vedette', 'Candidat', 'INSEE', 'Définition'])
    testDefinition= ""
    for communerest in rest_list :
        if communerest[-1] == testDefinition:
            communerest[-1] = PhraseDefinition
            Listcommunerest.writerow(communerest)
        else :
            testDefinition = communerest[-1]
            PhraseDefinition = ""
            for mot in communerest[-1]:
                PhraseDefinition = PhraseDefinition + mot
            communerest[-1] = PhraseDefinition
            Listcommunerest.writerow(communerest)

tree.write(xml_out,encoding="UTF-8",xml_declaration=True)



