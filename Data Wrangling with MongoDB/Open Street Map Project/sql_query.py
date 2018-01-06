#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 26 00:08:41 2017

@author: wendycui
"""

#import csv
import sqlite3

def number_of_nodes():
	result = cur.execute('SELECT COUNT(*) FROM nodes')
	return result.fetchone()[0]

def number_of_ways():
	result = cur.execute('SELECT COUNT(*) FROM ways')
	return result.fetchone()[0]

def number_of_unique_users():
	result = cur.execute('SELECT COUNT(DISTINCT(all_user.uid)) \
                          FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways) all_user')
	return result.fetchone()[0]
    
def top_contributing_users():
	top_users = []
	for row in cur.execute('SELECT all_user.user, COUNT(*) as num \
                            FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) all_user \
                            GROUP BY all_user.user \
                            ORDER BY num DESC \
                            LIMIT 10'):
		top_users.append(row)
	return top_users

def number_of_users_contributing_once():
	result = cur.execute('SELECT COUNT(*) \
                          FROM \
                          (SELECT all_user.user, COUNT(*) as num \
                          FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways) all_user \
                          GROUP BY all_user.user \
                          HAVING num = 1) u')
	return result.fetchone()[0]

def common_amenities():
    common = []
    for row in cur.execute('SELECT value, COUNT(*) as num \
                            FROM nodes_tags \
                            WHERE key="amenity" \
                            GROUP BY value \
                            ORDER BY num DESC \
                            LIMIT 10'):
        common.append(row)
    return common

def tourism():
    
    result = []
    
    for row in cur.execute('SELECT DISTINCT(value) as tour_type, COUNT(*) as num \
                           FROM (SELECT id, value FROM nodes_tags \
                                 WHERE key = "tourism") \
                           GROUP BY tour_type \
                           ORDER BY num DESC'):
        result.append(row)
    return result


def popular_cuisines():
    pop = []
    for row in cur.execute('SELECT nodes_tags.value, COUNT(*) as num \
            FROM nodes_tags \
                JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value="restaurant") re \
                ON nodes_tags.id=re.id \
            WHERE nodes_tags.key="cuisine" \
            GROUP BY nodes_tags.value \
            ORDER BY num DESC \
            LIMIT 5'):
        pop.append(row)
          
    return pop

def oneway_count():
    result = cur.execute('SELECT COUNT(DISTINCT(id)) FROM ways_tags \
                         WHERE key = "oneway" and value = "yes"')
    return result.fetchone()[0]

def start_date():
    
    total_result = cur.execute('SELECT COUNT(DISTINCT(id)) FROM ways_tags \
                         WHERE key = "start_date" and (value > "1800" and value <= "2017")')
    
    print("total number of nodes having start_date:", total_result.fetchone()[0])
    century19 = cur.execute('SELECT COUNT(DISTINCT(id)) FROM ways_tags \
                         WHERE key = "start_date" and (value >= "1800" and value < "1900")')
    print("number of nodes that start_date is in 19 century:", century19.fetchone()[0])
    century20 = cur.execute('SELECT COUNT(DISTINCT(id)) FROM ways_tags \
                         WHERE key = "start_date" and (value >= "1900" and value < "2000")')
    print("number of nodes that start_date is in 20 century:", century20.fetchone()[0])
    century21 = cur.execute('SELECT COUNT(DISTINCT(id)) FROM ways_tags \
                         WHERE key = "start_date" and (value >= "2000" and value < "2017")')
    print("number of nodes that start_date is in 21 century:", century21.fetchone()[0])


    ''' 
    # the year that the oldest building or a street was built.
    minres = cur.execute('SELECT MIN(value) FROM ways_tags \
                         WHERE key = "start_date"')
    
    return minres.fetchone()[0]
    '''
def edge_of_map():
    #min_lat, min_lon, max_lat, max_lon
    result = cur.execute('SELECT MIN(lat), MIN(lon), MAX(lat), MAX(lon) FROM nodes')
    return result.fetchone()
   # min_lat = cur.execute('SELECT MIN(lat) FROM nodes')
    #return min_lat.fetchone()[0]
if __name__ == '__main__':
	
    con = sqlite3.connect("../udacity_project1_final.db")
    cur = con.cursor()
    
    
    
    print ("the edge of map is:", edge_of_map())
    print ("Number of nodes: " , number_of_nodes())
    print ("Number of ways: " , number_of_ways())
    print ("Number of unique users: " , number_of_unique_users())
    print ("Top contributing users: " , top_contributing_users())
    print ("Number of users contributing once: " , number_of_users_contributing_once())
    print ("Common amenities: " , common_amenities())
    print ("Popular cuisines: " , popular_cuisines())
    print("oneway street is:", oneway_count())
    start_date()
    print("tourism:",tourism())
    