import sys
import csv
import re

# utils % python tp.py dt_id

dt_id = sys.argv[1]
dt_dir = '../data/'+dt_id+'/'
dt_f = dt_dir+'/output6.xml'
mapping_f  = dt_dir+'IDS_MAP.tsv'
mapping_d = {} # mapping dans un dict

with open(mapping_f) as tsvfile:
	tsvreader = csv.reader(tsvfile, delimiter="\t")
	for row in tsvreader:
		old_id = row[1]
		new_id = row[0]
		mapping_d[old_id] = new_id

inFile = open(dt_f, 'r')
outFile = open(dt_dir+'output7.xml', 'w')
id_pattern = re.compile('article id="([^"]+)"')

for line in inFile:
	dt_old_id = re.search(id_pattern, line)
	if dt_old_id is not None:
		old_id = dt_old_id.group(1)
		line = line.replace(
        	'id="{}"'.format(old_id),
        	'id="{}" old-id="{}"'.format(mapping_d[old_id], old_id))
	outFile.write(line)

tsvfile.close()
inFile.close()
outFile.close()
