import sys, codecs
import csv
import re
import time

# utils % python insert_new-ids.py DT76

start_time = time.time()

dt_id = sys.argv[1]
dt_dir = '../data/'+dt_id+'/'
dt_file_path = dt_dir+'/output7.xml'
dt_ids_path  = dt_dir+'IDS_MAP.tsv'

new_ids_dict = {}

with open(dt_ids_path) as tsvfile:
    tsvreader = csv.reader(tsvfile, delimiter="\t")
    for row in tsvreader:
        new_ids_dict[row[1]] = row[0]

# search/replace in new file
inFile = codecs.open(dt_file_path, "r", "utf-8")
outFile = codecs.open(dt_dir + "output7.xml", "w", "utf-8")
id_pattern = re.compile('article id="([^"]+)"')

for line in inFile:
    dt_old_id = re.search(id_pattern, line)
    if dt_old_id is not None:
        old_id = dt_old_id.group(1)
        """
        line = re.sub(
            'id="({})"'.format(old_id),
            'id="{}" old_id="\\1"'.format(new_ids_dict[old_id]),
            line)
        """
        line = line.replace(
            'id="{}"'.format(old_id),
            'id="{}" old_id="{}"'.format(new_ids_dict[old_id], old_id))
    #print(line)
    outFile.write(line)
    
inFile.close()
outFile.close()

print("--- %s seconds ---" % (time.time() - start_time))
