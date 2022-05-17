import xml.etree.ElementTree as ET
import unidecode
import csv

dep = "37"
dir_path = "../data/"
xml_entry = dir_path + "DT" + dep + "/output2.xml"
dict_commune_2011 = dir_path + "DT" + dep + "/DT" + dep + "_liageINSEE_article-commune.csv"
xml_out = dir_path + "DT" + dep + "/output3.xml"
tsv_out =  dir_path + "DT" + dep + "/DT" + dep + "_liageINSEE_localisation-commune.csv"
d = {}
 #Crée un dictionnaire qui contient le nom et le code insee pour chaque commune du dictionnaire
with open(dict_commune_2011, newline='') as csvfile:
    ListcommunesInsee = csv.reader(csvfile, delimiter='\t', quotechar='|')
    for communeInsee in ListcommunesInsee :
        #Supprime les accents pour s'assurer de la cohérence car il y a des différences d'accent entre les noms dans les corps de texte et le reste
        nCommune = unidecode.unidecode(communeInsee[1])
        d[nCommune] = communeInsee[4]
print(d)
tree= ET.parse(xml_entry)
xml = tree.getroot()
#Liste qui doit contenir les informations des communes pour pouvoir contrôler les échecs de correspondance
controleList = []
n = 0
nb = 0
typologie = ""
savevedette = ""

#Choix d'utilisation de boucle en for en série car ça permet de retirer à chaque étape les données nécessaires à la correction finale du tableau
for article in xml :
    dep = xml.attrib.get("dep")
    for balises in article:
        if balises.tag == "vedette":
            for sm in balises :
                if sm.tag =="sm":
                    vedette = sm.text
        if balises.tag == "definition":
            definition = balises.itertext()
            for localisation in balises :
                if localisation.tag == "typologie":
                    typologie = localisation.text
                    #savevedette permet de sauvegarder le nom de la vedette et quand il y a un changement d'article et pas de balise typologie, on vide la balise pour éviter les erreurs.
                    savevedette = vedette
                elif savevedette != vedette :
                    savevedette = vedette
                    typologie = ""
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
                            lst = [article.attrib.get("id"), vedette, definition, commune.text]
                            controleList.append(lst)


#Crée le fichier csv des articles et des communes qui n'ont pas trouvé d'équivalent
with open(tsv_out, "w") as csvfile:
    Listcommunerest= csv.writer(csvfile)
    Listcommunerest.writerow(['Article', 'Vedette', 'Definition', 'Localisation', 'INSEE_corrigé', 'Nom_corrigé','Commentaire'])
    testDefinition= ""
    for communerest in controleList :
        if communerest[2] == testDefinition:
            communerest[2] = PhraseDefinition
            Listcommunerest.writerow(communerest)
        else :
            testDefinition = communerest[2]
            PhraseDefinition = ""
            for mot in communerest[2]:
                PhraseDefinition = PhraseDefinition + mot
            communerest[2] = PhraseDefinition
            Listcommunerest.writerow(communerest)


print(n)
print(nb)

tree.write(xml_out, encoding="UTF-8",xml_declaration=True)
