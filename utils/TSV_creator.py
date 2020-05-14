import csv
import click
from lxml import etree

@click.command()
@click.argument('path')
@click.argument('output_file')
def main (path, output_file):
    list_final = []
    dict_commune = {}
    dict_codepostaux = {}
    #création d'un dictionnaire des communes de 2011 pour pouvoir trouver le nom des communes qui datent de 2011 et non celle des DT qui peuvent avoir des noms de communes disparus ou pas forcément bien orthographier
    with open("Listedescommunes2011.csv") as csvfile:
        ListcommunesInsee = csv.reader(csvfile, delimiter=',', quotechar='|')
        for communeInsee in ListcommunesInsee :
            dict_commune[communeInsee[0]] = communeInsee[2]
    #création d'un dictionnaire codes postaux grâce au code insee, dnnée récupéré sur data.gouv.fr/fr/datasets/correspondance-entre-les-codes-postaux-et-codes-insee-des-communes-francaises/
    with open("correspondance-code-insee-code-postal.csv") as csvfile:
        ListcommunesInsee = csv.reader(csvfile, delimiter=';', quotechar='|')
        for communeInsee in ListcommunesInsee :
            dict_codepostaux[communeInsee[0]] = communeInsee[1]
    tree= etree.parse("{}".format(path))
    for article in tree.xpath("//article") :
        id_article = article.attrib.get("id")
        vedette = article.xpath("./vedette/sm/text()")[0]
        #suppression des diacritiques
        vedette = vedette.replace(",", "").split("(")[0]
        #On passe si l'article est une commune, nous n'avons pas besoin de les tester car ils sont déjà géolocalisée et peuvent créer du bruit
        if article.attrib.get("type") == "commune":
            code_insee = article.xpath("./insee/text()")[0]
            code_postal = dict_codepostaux.get(article.xpath("./insee/text()")[0])
            nom_commune = dict_commune.get(article.xpath("./insee/text()")[0])
            list_final.append([id_article, vedette, code_insee, code_postal, nom_commune])
        #Récupère les données des articles qui contiennent une balise commune avec un code insee
        elif article.xpath("./definition/localisation/commune/@insee") != []:
            code_insee = article.xpath("./definition/localisation/commune/@insee")[0]
            code_postal = dict_codepostaux.get(article.xpath("./definition/localisation/commune/@insee")[0])
            nom_commune = dict_commune.get(article.xpath("./definition/localisation/commune/@insee")[0])
            list_final.append([id_article, vedette, code_insee, code_postal, nom_commune])
        else:
            code_insee = ""
            code_postal = ""
            nom_commune = ""
            list_final.append([id_article, vedette, code_insee, code_postal, nom_commune])
    #création du fichier de sortie
    with open(output_file, "w") as csvfile:
        Listresultat = csv.writer(csvfile)
        Listresultat.writerow(["IdArticle", "NomVedette", "codeInsee", "codePostal", "NomInsee"])
        for commune in list_final:
            Listresultat.writerow(commune)
if __name__ == "__main__":
    main()
