import sys
import csv
import re
from lxml import etree
from lxml.etree import tostring

# DT29 % python3 insert_new-vedettes.py

tree = etree.parse('DT29.xml')
outFile = open('DT29_vedette.xml', 'w')
mapping_f  = 'DT29_vedettes-revues.tsv'
mapping_d = {} # mapping dans un dict
vedette_map_err = {} # dict pour enregistrer les erreurs

id_pattern = re.compile('<sm>([^<]+)</sm>')

with open(mapping_f) as tsvfile:
	tsvreader = csv.reader(tsvfile, delimiter="\t")
	for row in tsvreader:
		article_id =  row[0]
		mapping_d[article_id] = (row[1], row[2])

for article in tree.xpath('/DICTIONNAIRE/article'):
	article_id = article.get('id')
	article_str = tostring(article, encoding='unicode')
	
	if article_id in mapping_d:
		old_sm = re.search(id_pattern, article_str)
		
		if old_sm.group(1) == mapping_d[article_id][0]:
			old_vedette = old_sm.group(1)
			article_str = article_str.replace(
				'<sm>{}</sm>'.format(old_vedette),
				'<sm old="{}">{}</sm>'.format(old_vedette, mapping_d[article_id][1]))
		else: 
			# enregistrer les anciennes vedettes du TSV qui ne correspondent pas à celles du XML…
			vedette_map_err[article_id] = (old_sm.group(1), mapping_d[article_id][0])
	
	print(article_str)

# rapport d’erreur des remplacements attendus (article id OK) mais non effectués (comparaison des vedettes à remplacer XML/TSV)
for id in vedette_map_err:
	print(id, vedette_map_err[id][1], '(tsv) pour (xml)', vedette_map_err[id][0])

tsvfile.close()
