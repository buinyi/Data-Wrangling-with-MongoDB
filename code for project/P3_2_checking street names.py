#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import collections
"""
This is a modification of 'checking street names' script used in Lesson 6.
First, I categorize the potential dictionary keys from 'tag' tags. This is similar to what was done in Lesson 6.
The output is:
{'lower': 346273, 'lower_colon': 114553, 'other': 491, 'problemchars': 1}
So, there is the only key with problematic character. Later I replace this key.

Second, I explore the last words in 'addr:street' and 'name' in order to replace invalid values in 'addr:street'.
Based on the results, I created a mapping for the next script to replace error street names values in 'addr:street'.
At this moment it is not possible identify errors in street names in 'name', because 'name' contains information
about a multitude of objects other than streets. I will return to this task while working with the data in MongoDB.

Third, I use the same script to process 'addr:city' (the key should be replaced for output to be seen).
Later I will keep only objects from the Kyiv city or without the city attribute and eliminate all the other objects.


"""


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'([a-z]|_)*:([a-z]|_)*$')
#lower_colon = re.compile(r'\w*:\w*')
problemchars = re.compile(r'.+[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
problemchars2 =re.compile(r'\W')

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected=['вулиця','проспект','провулок','бульвар','тупик','шосе','набережна','площа','узвіз','дорога','проїзд','алея']
# this is the the list of Ukrainian analogs for the words "street", "lane", "boulevard" etc.


def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    streets1_dict={} # street names from 'addr:street'
    streets2_dict={} # names (including street names) from 'name'
    errors_dict={}   # this is a special dict for invalid street names from 'addr:street'

    previous_tag=""

    for _, element in ET.iterparse(filename):

        if element.tag == "tag":
        
            key= element.attrib['k']
            value=element.attrib['v']
            m= street_type_re.search(value)

        #categorize the potential keys into lowerchar, lowerchar&colon, problemchar, other
            if lower.match(key):
                keys["lower"]+=1
            elif lower_colon.match(key):
                #print(element.attrib)
                keys["lower_colon"]+=1
            elif problemchars.match(key) or problemchars2.match(key):
                print(element.attrib)
                keys["problemchars"]+=1
            else:
                #print(element.attrib)
                keys["other"]+=1

            if m and (previous_tag=="node" or previous_tag=="way"):
                # extract value from 'addr:street', then count how namy times each value is found
                if key=="addr:street":
                    last_word = m.group()
                    #print(last_word)
                    if last_word in streets1_dict:
                        streets1_dict[last_word]+=1
                    else:
                        streets1_dict[last_word]=1
                #if the street name is invalid, store it in errors_dict
                # then I will use the output to create a mapping for fixing the street names
                    if last_word  not in expected:
                        if last_word in errors_dict:
                            if value in errors_dict[last_word]:
                                errors_dict[last_word][value]+=1
                            else:
                                errors_dict[last_word][value]=1
                        else:
                            errors_dict[last_word]={}
                            errors_dict[last_word][value]=1
                # extract value from 'name', then count how namy times each value is found
                elif key=="name":
                    last_word = m.group()
                    #print(last_word)
                    if last_word in streets2_dict:
                        streets2_dict[last_word]+=1
                    else:
                        streets2_dict[last_word]=1

        if (element.tag != "tag") and (element.tag != "nd"):
            previous_tag=element.tag
        
    return keys ,streets1_dict, streets2_dict, errors_dict



def test():
    
    keys, streets1_dict, streets2_dict, errors_dict  = process_map('D:/Udacity/IntroToMongoDB/kyiv_ukraine.osm')

    
    pprint.pprint(keys)
    #sort by the value (not by key)
    sorted1_list = [(k,v) for v,k in sorted([(v,k) for k,v in streets1_dict.items()]
)]
    sorted2_list = [(k,v) for v,k in sorted([(v,k) for k,v in streets2_dict.items()]
)]
    #count the total number of names in streets2_dict
    number=0
    for element in streets2_dict:
        number+=streets2_dict[element]
        #print(ordered)
    pprint.pprint(sorted1_list)
    #pprint.pprint(sorted2_list)
    pprint.pprint(errors_dict)
    print(number)

if __name__ == "__main__":
    test()
