import os
from lxml import etree
import csv

dep = "37"
dir_path = "../data/"
xml_entry = dir_path + "DT" + dep + "/DT{0}.xml".format(dep)
Correct_CSV = dir_path + "DT" + dep + "/DT{0}_liageINSEE_article-commune.csv".format(dep)
xml_out = dir_path + "DT" + dep + "/DT" + dep + "_CommuneINSEE.xml"


def main():
    """
        Update the TEIHeader of all the XML files in the different folder of the input path
    """
    dict = {}
    xml = etree.parse(xml_entry)
    with open(Correct_CSV, 'r', newline='') as meta:
        reader = csv.DictReader(meta, delimiter='\t', dialect="unix")
        for line in reader:
            dict[line["ID"]] = line["INSEE"]
            article = xml.xpath("//article[@id='{0}']".format(line["ID"]))
            article[0].attrib['type'] = "commune"
            template = etree.parse("./INSEE_template.xml")
            INSEE = template.find("//insee")
            INSEE.text = line["INSEE"]
            article[0].append(template.getroot())
            etree.strip_tags(article[0], 'tmp')

    with open(xml_out, 'wb') as f:
        tree_str = etree.tostring(xml, pretty_print=True, doctype='<?xml version="1.0" encoding="utf-8"?>', encoding="utf-8")
        f.write(tree_str)




if __name__ == "__main__":
    main()