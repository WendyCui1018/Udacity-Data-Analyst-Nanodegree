# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import csv
import codecs
import re
import xml.etree.cElementTree as ET
from collections import defaultdict

import pandas as pd



def count_tags(filename):
    #read file
    LA_osm = ET.ElementTree(file = filename)
    #get root
    root = LA_osm.getroot()

    #structure: 'osm' is the root, then 'node': changeset
    #a changeset consists of a group of changes made by a single user
    #‘obdl' means 'Open Database License’
    #'NHS' means 'National Highway System'
    
    #initialize dictionary
    #get root tag and count tags
    tags_count_dic = {root.tag: 0}
    #loop
    for event, element in ET.iterparse(filename, events = ('start',)):
        if element.tag in tags_count_dic:
            tags_count_dic[element.tag] += 1
        else:
            tags_count_dic[element.tag] = 1
    return tags_count_dic

#regulation expression
lower = re.compile(r'^([a-z]|_)*$') #valid only inculde lower character
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$') #valid information with ":" in it
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]') #including problematic character
#'other' category may contain more ':', numbers or capital letters

def key_type(element,keys,prob):

    if element.tag == 'tag':
        key = element.attrib['k']
        if lower.search(key):
            keys['lower'] += 1
        elif lower_colon.search(key):
            keys['lower_colon'] += 1
        elif problemchars.search(key):
            keys['problemchars'] += 1
            
        else:
            keys['other'] += 1
            prob.append(key)
    return keys,prob

def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    prob = []
    for event, element in ET.iterparse(filename):
        keys, prob = key_type(element, keys, prob)

    return keys, prob


def observe_user(filename):
    userID = set()
    for event, element in ET.iterparse(filename):
        if element.tag == 'node':
            if('uid' in element.attrib):
                userID.add(element.attrib['uid'])
    user_num = len(userID)
    return userID,user_num
 
     
if __name__ == "__main__":
    file = "../MyLA_sample.osm"
    
    keys,prob = process_map(file)
    prob = set(prob)
    prob_num = len(prob)
    print("audit 'k' in dataset:")
    print("the number of each regulation expression match result:", keys)
    print("the number of unique 'k' and 'k':", prob_num, prob)
    
    dic = count_tags(file)
    print("the number of different tags in dataset:", dic)
    
    userID, user_num = observe_user(file)
    print("the number of unique users in dataset and unique userID:",user_num, userID)
    


