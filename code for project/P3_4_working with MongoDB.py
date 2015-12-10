#!/usr/bin/env python
"""
This file contains information queries to MongoDB
"""

from datetime import datetime
import pprint
  


def get_db():
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client.osmap
    return db

if __name__ == "__main__":
    # For local use
    db = get_db()

# Number of documents
    print("Number of documents: ",db.kyiv.find().count())

# Number of nodes
    print("Number of nodes: ",db.kyiv.find({"type":"node"}).count())

# Number of ways
    print("Number of ways: ",db.kyiv.find({"type":"way"}).count())
#As I mentioned before, tag way can store information about very different objects
#including bus stops and street lamps. So, “way” here should not be interpreted as “road”. 


# Number of unique users
    print("Number of unique users: ",len(db.kyiv.distinct("created.user")))

# Top 10 contributing users
    print("Top 10 contributing users: ")
    pprint.pprint(list(db.kyiv.aggregate([#{"$match":{"created.user":{"$exists":True}}},
                                          {"$group":{"_id":"$created.user", "count":{"$sum":1}}},
                                          {"$sort":{"count":-1}},
                                          {"$limit":10}
                                          ])))

# Total amenities
    print("Total amenities: ", db.kyiv.find({"amenity":{"$exists":True}}).count())

# Unique amenity type
    print("Unique amenity types: ", len(db.kyiv.distinct("amenity",{"amenity":{"$exists":True}})))


# Top 10 amenity types
    print("Top 10 amenity types: ")
    pprint.pprint(list(db.kyiv.aggregate([{"$match":{"amenity":{"$exists":True}}},
                                          {"$group":{"_id":"$amenity", "count":{"$sum":1}}},
                                          {"$sort":{"count":-1}},
                                          {"$limit":10}
                                          ])))

    
# Highway tag vs name tag    
    print("higway: ")
    pprint.pprint(list(db.kyiv.aggregate([{"$match":{"highway":{"$exists":True}}},
                                          {"$project": {'_id':0, "highway":1, "name":1,
                                                        "value":{"$ifNull": [ "$name", "_withoutname" ]}}},
                                          {"$project": {'_id':0, "highway":1, "name":1,
                                                        "value":{"$cond":[{"$eq":["$value","_withoutname"]},0,1]}}},
                                          {"$group":{"_id":"$highway", "found":{"$sum":1}, "with_name":{"$sum":"$value"}}},
                                          {"$sort":{"found":-1}},
                                          {"$limit":100}
                                          ])))


    highway_list=["residential","unclassified","tertiary","secondary","primary", "trunk","living_street", "pedestrian"]
# Unique street names:
    print("Unique street names: ", len(db.kyiv.distinct("name",{"name":{"$exists":True},"highway":{"$in":highway_list}})))

# Number of unique street names
    print("Number of unique street names: ",len(db.kyiv.distinct("address.street")))
  
"""
    pprint.pprint(list(db.kyiv.aggregate([{"$match":{"highway":{"$exists":True},"name":{"$exists":True}, "highway":{"$in":highway_list} }},
                                          {"$project": {'_id':0, "highway":1, "name":1}},
                                          {"$group":{"_id":{"name":"$name", "highway":"$highway"}, "count":{"$sum":1}}},
                                          {"$project": {'_id':0, "highway":"$_id.highway", "name":"$_id.name"}},
                                          {"$sort":{"name":-1}}
                                          ])))
"""    

"""
# Number of tags by month of creation or last change
    l=list(db.kyiv.aggregate([{"$match":{"created.timestamp":{"$exists":True}}},
                              {"$project": {'_id':0, "type":1, "timestamp":"$created.timestamp"}}
                              ]))

    #pprint.pprint(l)
    print(len(l))
    res={}
    for item in l:
        month=item['timestamp'][0:7]
        if month not in res:
            res[month]={}
            res[month]['node']=0
            res[month]['way']=0
            
        res[month][item['type']]+=1
    pprint.pprint(res)
"""



