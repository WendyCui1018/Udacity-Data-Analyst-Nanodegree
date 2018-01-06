#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 26 22:27:00 2017

@author: wendycui
"""

import pandas as pd
import re

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE) # ignore whether the character is lower or capital
postcode_re = re.compile(r'^\d{5}(?:[-\s]\d{4})?$') #five digit and five digit-four digit
fix_postcode_with_stateabbr = re.compile(r'^[A-Z]{2}\s\d{5}(?:[-\s]\d{4})?$')


#need to update -- nodes_tags: value, ways_tags: value (when key = name)

# update street name
street_type_abbr_map = {"Dr" : "Drive", "Ave" : "Avenue", "avenue": "Avenue", "St" : "Street", "Str" : "Street", 
                        "St." : "Street", "Blvd" : "Boulevard", "blvd" : "Boulevard", "Blvd." : "Boulevard", "Rd" : "Road", "Fl" : "Floor", 
                        "floor" : "Floor", "Ct": "Court", "Hwy": "Highway", "Pkwy" : "Parkway", "Pky" : "Parkway",
                        "S" : "South", "W" : "West", "N" : "North", "E" : "East"}            
#street name revision

def street_update(nodes_tags, ways_tags):
    # revise nodes_tags
    for i in range(0,len(nodes_tags)):
        if(i in nodes_tags.index):
            if(nodes_tags.loc[i]['type'] == 'addr' and nodes_tags.loc[i]['key'] == 'street'):
                street_name = nodes_tags.loc[i]['value']
                stan = street_type_re.search(street_name)
                if stan:
                    street_type = stan.group().lower().title()
                    #print(street_type)
                    if (len(street_type) < 2): # wrong, remove
                        nodes_tags.drop(i, inplace = True)
                        continue
                    if (str(street_type[0]).isdigit()): #begin with digit, removes
                        nodes_tags.drop(i, inplace = True)
                        continue
                    if not street_type[-1].isalpha():
                        street_type = street_type[:-1]
                    if (street_type in street_type_abbr_map.keys()):
                        street_type_update = street_name.replace(street_type, street_type_abbr_map[street_type])
                        nodes_tags['value'][i]= street_type_update
                else:
                    continue

    #revise ways_tags
    for i in range(0,len(ways_tags)):
        if(i in ways_tags.index):
            if(ways_tags.loc[i]['key'] == 'name'):
                street_name = ways_tags.loc[i]['value']
                stan = street_type_re.search(street_name)
                if stan:
                    street_type = stan.group().lower().title()
                    #print(street_type)
                    if (len(street_type) < 2): # wrong, remove
                        ways_tags.drop(i, inplace = True)
                    continue
                    if (str(street_type[0]).isdigit()): #begin with digit, removes
                        ways_tags.drop(i, inplace = True)
                        continue
                    if not street_type[-1].isalpha():
                        street_type = street_type[:-1]
                    if (street_type in street_type_abbr_map.keys()):
                        street_type_update = street_name.replace(street_type, street_type_abbr_map[street_type])
                        ways_tags['value'][i]= street_type_update
                else:
                    continue


def postcode_update(nodes_tags, ways_tags):
    # revise nodes_tags
    #cc = 0
    for i in range(0,len(nodes_tags)):
        if(i in nodes_tags.index):
            if(nodes_tags.loc[i]['type'] == 'addr' and nodes_tags.loc[i]['key'] == 'postcode'):
                postcode = nodes_tags.loc[i]['value']
                postcode = postcode.strip()

                stan = postcode_re.search(postcode)
                if(stan):
                    if(postcode.find('-') != -1):
                        postcode_update = postcode[:-5]
                        #cc += 1
                    else:
                        continue
                
                if (postcode[0:3] == 'New'): # begin with "New"
                    postcode_update = postcode[-5]
                if (fix_postcode_with_stateabbr.search(postcode)): #state abbreviation and five digit
                    postcode_update = postcode[3:]
                nodes_tags['value'][i]= postcode_update
                
    
    #revise ways_tags
    #count = 0
    for i in range(0,len(ways_tags)):
        if(i in ways_tags.index):
            if(ways_tags.loc[i]['type'] == 'addr' and ways_tags.loc[i]['key'] == 'postcode'):
                postcode = ways_tags.loc[i]['value']
                postcode = postcode.strip()

                stan = postcode_re.search(postcode)
                if(stan):
                    if(postcode.find('-') != -1):
                        #print(postcode)
                        #count += 1
                        postcode_update = postcode[:-5]
                    else:
                        continue   
                
                if (postcode[0:3] == 'New'): # begin with "New"
                #postcode = postcode[-5:]
                    postcode_update = postcode[-5]
                #nodes_tags['value'][i]= postcode_update
                if (fix_postcode_with_stateabbr.search(postcode)): #state abbreviation and five digit
                    postcode_update = postcode[3:]
                ways_tags['value'][i]= postcode_update

if __name__ == "__main__":
    
    
    
    print("loading data...")
    nodes_tags = pd.read_csv('../csv files/nodes_tags.csv')
    ways_tags = pd.read_csv('../csv files/ways_tags.csv')
    print("data loading done!")
    street_update(nodes_tags, ways_tags)
    print("street revision done")
    postcode_update(nodes_tags, ways_tags)
    print("postcode revision done")
    nodes_tags.to_csv('../csv files/nodes_tags_update.csv')
    ways_tags.to_csv('../csv files/ways_tags_update.csv')
    print("update done")
    
    
    
    
    