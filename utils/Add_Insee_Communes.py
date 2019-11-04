import xml.etree.ElementTree as ET
import unidecode
import csv

d = {}
 #Crée un dictionnaire qui contient le nom et le code insee pour chaque commune du dictionnaire
with open("/home/corentink/Bureau/Dicotopo/Dossier_correction/DT73/DT73.csv", newline='') as csvfile:
    ListcommunesInsee = csv.reader(csvfile, delimiter=',', quotechar='|')
    for communeInsee in ListcommunesInsee :
        #Supprime les accents pour s'assurer de la cohérence car il y a des différences d'accent entre les noms dans les corps de texte et le reste
        nCommune = unidecode.unidecode(communeInsee[1])
        d[nCommune] = communeInsee[5]

tree= ET.parse("/home/corentink/Bureau/Dicotopo/Dossier_correction/DT73/output2.xml")
xml = tree.getroot()
#Liste qui doit contenir les informations des communes pour pouvoir contrôler les échecs de correspondance
controleList = []
n = 0
nb = 0

#Choix d'utilisation de boucle en for en série car ça permet de retirer à chaque étape les données nécessaires à la correction finale du tableau
for article in xml :
    for balises in article:
        if balises.tag == "vedette":
            for sm in balises :
                if sm.tag =="sm":
                    vedette = sm.text
        if balises.tag == "definition":
            for localisation in balises :
                if localisation.tag == "typologie":
                    typologie = localisation.text
                for commune in localisation :
                    if commune.tag == "commune":
                        n = n + 1
                        try :
                            nomNorm = unidecode.unidecode(commune.text)
                        except:
                            print(article.attrib)
                        nomOk = False
                        for nom, insee in d.items():
                            if nom == nomNorm:
                                commune.set("insee", insee)
                                nomOk = True
                        if nomOk == False :
                            nb = nb + 1
                            lst = [article.attrib.get("id"), vedette, typologie, commune.text]
                            controleList.append(lst)


#Crée le fichier csv des articles et des communes qui n'ont pas trouvé d'équivalent
with open("/home/corentink/Bureau/Dicotopo/Dossier_correction/DT73/EchecCommune.csv", "w") as csvfile:
    Listcommunerest= csv.writer(csvfile)
    Listcommunerest.writerow(['Article', 'Vedette', 'Typologie', 'Localisation'])
    for communerest in controleList :
        Listcommunerest.writerow(communerest)

print(n)
print(nb)

tree.write("/home/corentink/Bureau/Dicotopo/Dossier_correction/DT73/output3.xml",encoding="UTF-8",xml_declaration=True)
