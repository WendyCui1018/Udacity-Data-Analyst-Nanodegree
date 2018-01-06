#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 25 01:20:58 2017

@author: wendycui
"""


"""
Build database of the CSV files with the repective table names.
"""

import csv
import sqlite3

con = sqlite3.connect("../udacity_project1_final.db")
con.text_factory = str
cur = con.cursor()

# create nodes table
cur.execute('''CREATE TABLE nodes (id, uid, user, lat, lon, version, timestamp, changeset)''')
with open('../csv files/nodes.csv','r') as fin:
    dic = csv.DictReader(fin) 
    to_db = [(i['id'], i['uid'], i['user'], i['lat'], i['lon'], i['version'], i['timestamp'], i['changeset']) for i in dic]
             

cur.executemany("INSERT INTO nodes (id, uid, user, lat, lon, version, timestamp, changeset) VALUES (?, ?, ?, ?, ?, ?, ?, ?);", to_db)
con.commit()

#create nodes_tags table
cur.execute("CREATE TABLE nodes_tags (id, key, value, type);")
with open('../csv files/nodes_tags_update.csv','r') as fin:
    dic = csv.DictReader(fin) 
    to_db = [(i['id'], i['key'], i['value'], i['type']) for i in dic]

cur.executemany("INSERT INTO nodes_tags (id, key, value, type) VALUES (?, ?, ?, ?);", to_db)
con.commit()

#Create ways table
cur.execute("CREATE TABLE ways (id, user, uid, version, changeset, timestamp);")
with open('../csv files/ways.csv','r') as fin:
    dic = csv.DictReader(fin) 
    to_db = [(i['id'], i['user'], i['uid'], i['version'], i['changeset'], i['timestamp']) for i in dic]

cur.executemany("INSERT INTO ways (id, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?);", to_db)
con.commit()

#Create ways_nodes table
cur.execute("CREATE TABLE ways_nodes (id, node_id, position);")
with open('../csv files/ways_nodes.csv','r') as fin:
    dic = csv.DictReader(fin) 
    to_db = [(i['id'], i['node_id'], i['position']) for i in dic]

cur.executemany("INSERT INTO ways_nodes (id, node_id, position) VALUES (?, ?, ?);", to_db)
con.commit()

#Create ways_tags table
cur.execute("CREATE TABLE ways_tags (id, key, value, type);")
with open('../csv files/ways_tags_update.csv','r') as fin:
    dic = csv.DictReader(fin) 
    to_db = [(i['id'], i['key'], i['value'], i['type']) for i in dic]

cur.executemany("INSERT INTO ways_tags (id, key, value, type) VALUES (?, ?, ?, ?);", to_db)
con.commit()
con.close()