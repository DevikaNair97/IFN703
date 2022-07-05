import os
import xml.etree.ElementTree as ET
import json
import xml.dom.minidom

path = os.getcwd()
# print(path)

tree = ET.parse(path + '/file1.xml')

root = tree.getroot()

children = list(root)
dict_pages = {}
i =0
for child in children:
    print(" entered child")
    if "page" in child.tag and i<11:
        got_id = False
        # print(child)
        dict_try = {}
        for elem in child.iter():
            if "id" in elem.tag and got_id == False:
                id = elem.text
                print(id)
                got_id = True
            if "timestamp" in elem.tag:
                ts = elem.text
                # ts = ts.split('T')[0] + " " + timestamp.split('T')[1].split('Z')[0]
                # timestamp.append(ts)
            elif "text" in elem.tag:
                txt = elem.text
                dict_try[ts] = txt

        dict_pages[id] = dict_try
        i = i+1

print(len(dict_pages))