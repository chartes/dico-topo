import csv
d = {}
dir_path ="/home/corentink/Bureau/Dicotopo/"
dep = 73
file_in = dir_path + "DT" + dep
file_out = dir_path + "DT" + dep

#Le fichier doit contenir la liste des communes du département de l'INSEE 2018 qui sert de dictionnaire de référence
with open("{0}/listcommune.csv".format(file_in), newline='') as csvfile:
    ListcommunesInsee = csv.reader(csvfile, delimiter=',', quotechar='|')
    for communeInsee in ListcommunesInsee :
        d[communeInsee[1]] = communeInsee[0]
listresultat = []
listrest = []
correspondance = False
#Le fichier doit contenir les communes restantes qui n'ont pas de match dans le département
with open("{0}/Rest_prepared.csv".format(file_in, dep), newline='') as csvfile:
    rest = csv.reader(csvfile, delimiter=',', quotechar='|')
    for commune in rest :
        for NCC,INSEE in d.items():
            if commune[2] in NCC:
                commune.append(INSEE)
                commune.append(NCC)

                correspondance = True
        if correspondance == False :
            listrest.append(commune)
        else :
            listresultat.append(commune)
            correspondance = False
#Il crée un premier fichier de résultats qui contient les matchs probables sur les substrings du nom des villes
with open("{0}/result2.csv".format(file_out), "w", newline='') as csvfile:
    fichierfinal = csv.writer(csvfile, delimiter=',')
    for ligne in listresultat :
        fichierfinal.writerow(ligne)

listresultat2 = []
listrest2 = []
for commune in listrest :
    for NCC,INSEE in d.items():
        if commune[3] in NCC:
            commune.append(INSEE)
            commune.append(NCC)
            correspondance = True
    if correspondance == False :
        listrest2.append(commune)
    else :
        listresultat2.append(commune)
        correspondance = False

#Il crée un fichier avec les résultats de match probable sur le premier mot du village
with open("{0}/result3.csv".format(file_out), "w", newline='') as csvfile:
    fichierfinal = csv.writer(csvfile, delimiter=',')
    for ligne in listresultat2 :
        fichierfinal.writerow(ligne)

#Il crée un fichier avec les communes qui n'ont matché avec aucune commune de l'INSEE 2018
with open("{0}/rest3.csv".format(file_out), "w", newline='') as csvfile:
    fichierfinal = csv.writer(csvfile, delimiter=',')
    for ligne in listrest2 :
        fichierfinal.writerow(ligne)





