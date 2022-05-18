import xml.etree.ElementTree as ET
import csv
#Variable qui set à déterminer sur quel département on travaille
dep = "36"
dir_path ="../data"
csv_in = dir_path + "/DT" + dep + "/DT" + dep + "_liageINSEE_localisation-commune.csv"
xml_in = dir_path + "/DT" + dep + "/output3.xml"
xml_out = dir_path + "/DT" + dep + "/output4.xml"
listC = []
# ! Supprimer la colonne Définition qui peut créer des problèmes au moment de la réinjection des données!
#Crée une liste qui contient le numéro de l'article en clé à corriger et en valeur le code INSEE et le texte contenu dans la balise commune et la valeur à corriger si nécessaire
with open(csv_in, newline='') as csvfile:
    ListcommunesInsee = csv.reader(csvfile, delimiter='\t', quotechar='|')
    for communeInsee in ListcommunesInsee :
        print(communeInsee)
        if communeInsee[4] != "Non" or communeInsee[4] != "NON":
            listC.append([communeInsee[0],communeInsee[3], communeInsee[2], communeInsee[4]])

tree = ET.parse(xml_in)
xml = tree.getroot()
#Liste qui doit contenir les informations des communes pour pouvoir contrôler les échecs de correspondance
controleList = []
n = 0
nb = 0

for article in xml :
    NumArticle = article.attrib.get("id")
    for balises in article:
        if balises.tag == "definition":
            for localisation in balises :
                if localisation.tag == "localisation":
                    typologie = localisation.text
                for commune in localisation :
                    if commune.tag == "commune":
                        for CommuneCorrection in listC:
                            #Pour ajouter l'attribut insee dans le champs commune, il faut que le numéro d'article soit bon et que la valeur compris entre les balises communes soit équivalentes à celle du tableur et que la valeur du code INSEE ne soit pas Non
                            if CommuneCorrection[0] == NumArticle and CommuneCorrection[2] == commune.text and CommuneCorrection[1] != "NON" and CommuneCorrection[1] != "Non":
                                commune.set('insee', CommuneCorrection[1])
                                #Si une entrée est présente dans le cominl[3] alors on doit la supprimer pour assurer qu'aucune erreur ne soit possible
                                if CommuneCorrection[3] != "":
                                    commune.text = CommuneCorrection[3]


tree.write(xml_out,encoding="UTF-8",xml_declaration=True)
