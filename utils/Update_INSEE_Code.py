import xml.etree.ElementTree as ET
import csv
import re
#Changer le numéro du département
dep = "55"
d = {}
#Crée un dictionnaire qui contient le numéro de l'article en clé à corriger et en valeur le code INSEE et le texte contenu dans la balise commune à partir du fichier corriger
with open("/home/corentink/Bureau/Dicotopo/Tableau_Correction/DT" + dep + "/DT" + dep + "_liageINSEE_localisation-commune-desambiguisation_OC.csv", newline='') as csvfile:
    ListcommunesInsee = csv.reader(csvfile, delimiter='\t')
    for communeInsee in ListcommunesInsee :
        if communeInsee[4] == "Non" or communeInsee[4] == "NON":
            continue
        if communeInsee[0] in d.keys():

            d[communeInsee[0]].update({communeInsee[3]:communeInsee[4]})
        else:
            d[communeInsee[0]] = {communeInsee[3]: communeInsee[4]}

tree= ET.parse("/home/corentink/Bureau/Dicotopo/Tableau_Correction/DT" + dep + "/output4.xml")
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
                    for NArticle, ValeurCorrection in d.items():
                        if NArticle == NumArticle :
                            #Rest[0] == typologie
                            for Candidat, Insee in ValeurCorrection.items():
                                if Candidat == typologie :
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
                                    #test si INSEE plus de 5 caractères alors c'est qu'il y a plusieurs codes et il faut les séparer pour pouvoir les compléter et les utiliser
                                    if len(Insee) > 5 :
                                        codesInsee = Insee.split("/")
                                        count = 0
                                        for commune in phrasexml.iter("commune"):
                                            #test si il y a bien un codes INSEE dans le count et supprime s'il y a des espaces, contrôle s'il peut être possible qu'un déséquilibre arrive s'il y a un ' dans le nom des communes
                                            try :
                                                codeI = codesInsee[count].replace(" ","")
                                            #Renvoie le numéro de l'article qui pose problème et on n'ajoute rien dans le count car il doit s'agir du même numéro de que le précédent
                                            except :
                                                print(NArticle)
                                                continue
                                            if "NON" in codeI:
                                                count += 1
                                                continue
                                            commune.set('insee', codeI)
                                            count += 1
                                    else :
                                        #Ajoute le code insee dans les balises communes rajoutées
                                        for commune in phrasexml.iter("commune"):
                                            commune.set('insee', Insee)
                                    localisation.append(phrasexml)
                             #Transforme phrase avec l'ensemble des informations en balise xml puis l'ajoute dans localisation. Il faudra supprimer les balises <div> et </div> dans le fichier final


tree.write("/home/corentink/Bureau/Dicotopo/Tableau_Correction/DT" + dep + "/output5.xml",encoding="UTF-8",xml_declaration=True)
