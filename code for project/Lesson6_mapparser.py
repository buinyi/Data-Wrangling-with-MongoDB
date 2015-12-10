#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Your task is to use the iterative parsing to process the map file and
find out not only what tags are there, but also how many, to get the
feeling on how much of which data you can expect to have in the map.
Fill out the count_tags function. It should return a dictionary with the 
tag name as the key and number of times this tag can be encountered in 
the map as value.

Note that your code will be tested with a different data file than the 'example.osm'
"""
import xml.etree.cElementTree as ET
import pprint

def count_tags(filename):
        # YOUR CODE HERE
        tags_count={}
        cnt=0
        for line in ET.iterparse(filename):
            if cnt<5:
                print(line[1].tag)
            cnt+=1
            tag=line[1].tag
            if tag in tags_count:
                tags_count[tag]+=1
            else:
                tags_count[tag]=1
        return tags_count

def test():

    tags = count_tags('D:/Udacity/IntroToMongoDB/example.osm')
    pprint.pprint(tags)
    assert tags == {'bounds': 1,
                     'member': 3,
                     'nd': 4,
                     'node': 20,
                     'osm': 1,
                     'relation': 1,
                     'tag': 7,
                     'way': 1}

    

if __name__ == "__main__":
    test()
    
    
# Chicago full dataset results    
# 2015-08-13 14:22:04.636848
#{'bounds': 1,
# 'member': 43678,
# 'nd': 9072027,
# 'node': 7679935,
# 'osm': 1,
# 'relation': 2484,
# 'tag': 6158629,
# 'way': 1087021}
# total tags 24,043,776
# Number of unique users:  1131
# 2015-08-13 14:31:22.094848    
