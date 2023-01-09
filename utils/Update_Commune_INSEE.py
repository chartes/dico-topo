import xml.etree.ElementTree as ET
import csv
from pprint import pprint

dep = "37"
dir_path ="../data"
csv_in = dir_path + "/DT" + dep + "/DT" + dep + "_liageINSEE_localisation-commune.csv"
xml_in = dir_path + "/DT" + dep + "/output3.xml"
xml_out = dir_path + "/DT" + dep + "/output4.xml"
listC = []
# ! Supprimer la colonne Définition qui peut créer des problèmes au moment de la réinjection des données!
with open(csv_in, newline='') as csvfile:
    ListcommunesInsee = csv.reader(csvfile, delimiter='\t', quotechar='"')
    for communeInsee in ListcommunesInsee :
        if communeInsee[3].lower() != "non":
            '''
            communeInsee[0]: Article (article_id)
            communeInsee[2]: Localisation (commune.text)
            communeInsee[3]: INSEE_corrigé (code ou 'Non')
            communeInsee[4]: Nom_corrigé (label)
            '''
            listC.append([communeInsee[0], communeInsee[2], communeInsee[3].lower(), communeInsee[4]])
    #pprint(listC)

tree = ET.parse(xml_in)
xml = tree.getroot()

for article in xml :
    NumArticle = article.attrib.get("id")
    for balises in article:
        if balises.tag == "definition":
            for localisation in balises :
                if localisation.tag == "localisation":
                    #print(''.join(localisation.itertext()))
                    for commune in localisation :
                        if commune.tag == "commune":
                            #print(commune.text)
                            for CommuneCorrection in listC:
                                if CommuneCorrection[0] == NumArticle and CommuneCorrection[1] == commune.text:
                                    print(NumArticle + ' insert @insee: ' + CommuneCorrection[2])
                                    commune.set('insee', CommuneCorrection[2])
                                    #Si une entrée est présente dans le cominl[3] alors on doit la supprimer pour assurer qu'aucune erreur ne soit possible
                                    if CommuneCorrection[3] != "":
                                        print(NumArticle + ' ' + commune.text + ' => ' + CommuneCorrection[3])
                                        commune.text = CommuneCorrection[3]


tree.write(xml_out,encoding="UTF-8",xml_declaration=True)
