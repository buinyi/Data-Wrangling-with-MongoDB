#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a modification of iterative parsing script used in Lesson 6.
In this script I:
- count the number of different tags and save to a csv file
- count the number of second level tags stored in 'k' field of 'tag'
and save them to a csv file
- count the number of uniques users
- check whether potential dictionary keys contain problematic characters
(it is needed to uncomment a few rows to see the problematic
rows printed)

"""
import xml.etree.cElementTree as ET
import pprint
import collections
import csv
import re

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'.+[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
problemchars2 = re.compile(r'\W')

def count_tags(filename):

        tags_count={} #tags in file
        users = set() #unique users
        tag_keys={}   #keys from tag named 'tag'
  
        #parse file
        for _,element in ET.iterparse(filename):
            tag=element.tag
            #count the number of different tags... 
            if tag in tags_count:
                tags_count[tag]["_found"]+=1
            else:
                tags_count[tag]={}
                tags_count[tag]["_found"]=1

        #...and their attributes
            for attr in element.attrib:
                if attr in tags_count[tag]:
                    tags_count[tag][attr]+=1
                else:
                    tags_count[tag][attr]=1

        # We are especially interested in tags named 'tag'.
        # Atreet names, building types, housenumbers are stored here
        # I am going to count the number different keys in 'tag'
                if tag=='tag':
                    if (element.attrib[attr] in tag_keys) and (attr=='k'):
                        tag_keys[element.attrib[attr]]+=1
                    elif (element.attrib[attr] not in tag_keys) and (attr=='k'):
                        #if(problemchars2.match(element.attrib[attr])):
                        #    print(element.attrib)
                        tag_keys[element.attrib[attr]]=1
        


        # also I counted the number of users who contributed to the dataset
        # this is similar to an assignment from PS6
            try:
                users.add(element.attrib['user'])
            except KeyError:
                pass

    
        return tags_count, users, tag_keys

def test():
    import datetime
    print("Script started: ", datetime.datetime.now())
    
    tags_count, users, tag_keys = count_tags('D:/Udacity/IntroToMongoDB/kyiv_ukraine.osm')

    pprint.pprint(tags_count)

    print("\nNumber of users: ", len(users),"\n")
    print("Keys in tags:")

    #print only keys that appear 200+ times in the dataset
    tag_keys = collections.OrderedDict(sorted(tag_keys.items()))
    tag_keys_list=[]
    for element in tag_keys:
        #if(tag_keys[element]>200):
        #if(other.match(element)):
        #    print(element, tag_keys[element])
        tag_keys_list.append([element, tag_keys[element]])
    with open('D:/Udacity/IntroToMongoDB/res_tag.csv', 'w', newline='') as fp:
        a = csv.writer(fp, delimiter=',')
        a.writerows(tag_keys_list)

    #export tags_count to csv file
    tags_count_list=[]
    for row in tags_count:
        for item in tags_count[row]:
            tags_count_list.append([row, item, tags_count[row][item]])
    with open('D:/Udacity/IntroToMongoDB/res.csv', 'w', newline='') as fp:
        a = csv.writer(fp, delimiter=',')
        a.writerows(tags_count_list)




    print("Script ended: ", datetime.datetime.now())
    
if __name__ == "__main__":
    test()
