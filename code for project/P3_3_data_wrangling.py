#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
"""
This cript used the insights I obtained before and creates a JSON file with dictionaries of the following format:

{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}


The following are the rules for my data processing:
-	include only 2 types of top level tags: "node" and "way"
-	all attributes of "node" and "way" should be turned into regular key/value pairs, except:
    *	attributes in the CREATED array should be added under a key "created"
    *	attributes for latitude and longitude should be added to a "pos" array,
    *	for use in geospacial indexing. Make sure the values inside "pos" array are floats and not strings. 
-	one second level tag "k" value with problematic characters is replaced with the correct value
-	if second level tag "k" value starts with "addr:", it should be added to a dictionary "address"
-	if second level tag "k" value does not start with "addr:", but contains ":", you can process it same as any other tag.
-	if there is a second ":" that separates the type/direction of a street, the tag should be ignored
-	2 occurrences of ‘addr:street_1’ tag are ignored
-	The data nodes with ‘addr:city’ attribute value outside Kyiv are ignored
-	The attributes ‘addr:city:en’ are ignored
-	If second level tag "k" value is "type", change it to “typeinner”




"""


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'.+[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
problemchars2 =re.compile(r'\W')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
LONLAT = ["lon", "lat"]

# mapping to correct city names and replace the onjects outside Kyiv (in Ukrainian: "Київ")
mapping_city = {
"київ": "Київ", 
"Киів"	: "Київ", 
"Киев"	: "Київ", 
"Kyiv"	: "Київ",
"Kiev"	: "Київ"} 

# mapping to correct street names
mapping_street = { "Срибнокильская": "Срібнокільська вулиця", 
"Sortuvalna str."	: "Сортувальна вулиця", 
"вул. Антонова"	: "Антонова вулиця", 
"ул. Бориспольская"	: "Бориспільська вулиця", 
"Ботанічна"	: "Ботанічна вулиця", 
"Бучми"	: "Бучми вулиця", 
"Большая Васильковская"	: "Велика Васильківська вулиця", 
"вулиця Виставкова"	: "Виставкова вулиця", 
"пров. Вишневий"	: "Вишневий провулок", 
"Декабристів"	: "Декабристів вулиця", 
"Златоустовская"	: "Златоустівська вулиця", 
"Котовского"	: "Котовського вулиця", 
"проспект Леся Курбаса"	: "Леся Курбаса вулиця", 
"Леніна"	: "Леніна вулиця", 
"Лучистая"	: "Лучиста вулиця", 
"Лісківська"	: "Лісківська", 
"вул. Андрея Малышко"	: "Андрія Малишко вулиця", 
"вул. Микільсько-Слобідська"	: "Микільсько-Слобідська назва", 
"Набережная"	: "Дніпровська набережна", 
"Олійника"	: "Олійника вулиця", 
"Червоного Орача"	: "Червоного Орача вулиця", 
"Осенняя"	: "Осіння вулиця", 
"проспект Перемоги"	: "Перемоги проспект", 
"С. Петлюри"	: "Симона Петлюри вулиця", 
"вул. Сагайдачного"	: "Сагайдачного вулиця", 
"вул. Григорія Сковороди"	: "Григорія Сковороди вулиця", 
"Совхозная"	: "Радгоспна вулиця", 
"проспект Героев Сталинграда"	: "Героїв Сталінграду проспект", 
"Чернобыльская"	: "Чорнобильська вулиця", 
"Чехова"	: "Чехова вулиця", 
"Электротехническая"	: "Електротехнічна вулиця", 
"жовтнева"	: "Жотнева вулиця", 
"Днепровская набережная"	: "Дніпровська набережна", 
"Площа Дружби народів"	: "Дружби Народів Площа", 
"Московський п"	: "Московський проспект", 
"Автодорожная улица"	: "Автодорожна вулиця", 
"Погребський шлях"	: "Погребський Шлях вулиця"}


def shape_element(element):
    node = {} #full node
    node_created={} #'created' subnode
    node_address={} #'address' subnode
    lon_exists=0    # 1 if longitude exists for the node
    lat_exists=0    # 1 if latitude exist for the node
    node_refs=[]    # list of refs
    
    # process only 'node' and 'way' tags
    if element.tag == "node" or element.tag == "way" :

        node["type"]=element.tag
        
        # look through the tag attributes
        for attr in element.attrib:
            if attr in CREATED:
                node_created[attr]=element.attrib[attr]
            elif attr =="lon":
                lon=element.attrib[attr]
                lon_exists=1
            elif attr =="lat":
                lat=element.attrib[attr]
                lat_exists=1    
            else:
                node[attr]=element.attrib[attr]

        # if bot longitude and latitude exist
        if (lon_exists+lat_exists==2): 
            node["pos"]=[float(lat),float(lon)]

        # use .iter() to deal with subtags
        # extract street name from 'addr:street'
        for item in element.iter("tag"):
            if (problemchars.match(item.attrib['k']) is None) and (problemchars2.match(item.attrib['k']) is None):

                # extract address
                if 'addr:street' == item.attrib['k'][0:11]:
                    # process only keys with single semicolon like 'addr:street'
                    if (":" not in item.attrib['k'][11:]) and (item.attrib['k']!='addr:street_1'):
                        if(item.attrib['v'] not in mapping_street):
                            node_address[item.attrib['k'][5:]]=item.attrib['v']
                        else:
                            node_address[item.attrib['k'][5:]]=mapping_street[item.attrib['v']]
                elif 'addr:city' == item.attrib['k'][0:9]:
                    if (":" not in item.attrib['k'][9:]):
                        if(item.attrib['v'] not in mapping_city):
                            node_address[item.attrib['k'][5:]]=item.attrib['v']
                        else:
                            node_address[item.attrib['k'][5:]]=mapping_city[item.attrib['v']]
                elif 'addr:' == item.attrib['k'][0:5]:
                    node_address[item.attrib['k'][5:]]=item.attrib['v']
                # extract other allowed keys
                else:
                    if item.attrib['k']=="type":
                        node["typeinner"]=item.attrib['v']
                    else:
                        node[item.attrib['k']]=item.attrib['v']
            else:
              # deal with irregularities in tag key
              # only 1 such element found in the dataset
                if item.attrib['k'][len(item.attrib['k'])-5:]=="phone":
                    node[item.attrib['k'][len(item.attrib['k'])-5:]]=item.attrib['v']
                    
        # extract refs from subtags with the help of .iter()
        for item in element.iter("nd"):
            node_refs.append(item.attrib['ref'])

        # if CREATED subnode is not empty, add to node
        if len(node_created)>0:
            node['created']=node_created
        # if ADDRESS subnode is not empty, add to node
        if len(node_address)>0:
            node['address']=node_address
        # if REFS list is not empty, add to node
        if len(node_refs)>0:
            node['node_refs']=node_refs


        if ('address' in node) and ('city' in node['address']):
            if node['address']['city']=="Київ":
                return node # if city==Kyiv, return node
            else:
                return None # if city!=Kyiv, return nothing
        else:
            return node # if city is empty, return node
    else:
        # return nothing if tagnames are not 'node' or 'way'
        return None


def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)

    # write the dictionary into JSON file
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    # NOTE: if you are running this code on your computer, with a larger dataset, 
    # call the process_map procedure with pretty=False. The pretty=True option adds 
    # additional spaces to the output, making it significantly larger.

    import datetime
    print("Script started: ", datetime.datetime.now())
    
    data = process_map('D:/Udacity/IntroToMongoDB/kyiv_ukraine.osm', False)


    
    print("Script ended: ", datetime.datetime.now())
    
if __name__ == "__main__":
    test()
