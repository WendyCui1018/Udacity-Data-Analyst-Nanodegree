#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 15:58:22 2017

@author: wendycui
"""
import re
import codecs
import csv
import xml.etree.cElementTree as ET
#import schema
#import cerberus
#import pprint

#OSM_PATH = "example1.osm"
osm_file = "../MyLA_sample.osm"
node_file = "../csv files/nodes.csv"  #file generate by 'node' elements
node_tag_file = "../csv files/nodes_tags.csv"  #file generate by 'tag' in 'node'
ways_file = "../csv files/ways.csv"  #file generate by 'way' elements
ways_node_file = "../csv files/ways_nodes.csv" #file generate by 'node' in 'way'
ways_tag_file = "../csv files/ways_tags.csv" #file generate by 'tag' in 'way'

lower_colon = re.compile(r'^([a-z]|_)+:([a-z]|_)+') 
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

node_keys = ['id', 'uid','user','lat', 'lon', 'version','timestamp','changeset']
node_tags_keys = ['id', 'key', 'value', 'type']
way_keys = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
way_tags_keys = ['id', 'key', 'value', 'type']
way_nodes_keys = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields = node_keys, way_attr_fields = way_keys,
                  problem_chars = problemchars, default_tag_type = 'simple'):
    #Clean and shape node or way XML element to Python dict#

    node_dic = {} 
    way_dic = {}  
    way_nodes = []    
    tags = []  # Handle secondary tags with the same way for both node and way elements
    
    #extract 'node' elements
    if element.tag == 'node':
        #1.循环node_field表头,如果element中有key所对应的属性,则放入到node_dic字典中
        for key in node_keys:
            node_dic[key] = element.attrib[key]
        #2.loop children elements to get 'tag' information
        for child in element:
            node_tags = {} #dictionary to save nodes' tags informaiotn
            colon = re.match(lower_colon, child.attrib['k'])
            problem = re.match(problemchars, child.attrib['k'])
            #skip problematic character
            if problem:
                continue
            elif colon: #include ':' so that we can define 'type' 
                node_tags['id'] = element.attrib['id'] #'id' is the element's id(parent's node id)
                #separate k value to get 'type': use ':' to be a separation,the first part of it as 'type'
                type_value = child.attrib['k'].split(':',1)[0]
                node_tags['type'] = type_value
                #separate k value to get 'key': use ':' to be a separation,the second part of it as 'key'
                node_tags['key'] = child.attrib['k'].split(':',1)[1]
                #'v' is as value in node_tags dictionary
                node_tags['value'] = child.attrib['v']
                #add data to the dictionary
                tags.append(node_tags) # the primary key is 'id' in database
            else: 
                # do not include ':', just has 'k' and 'v'
                #'id' is the element's id(parent's node id)
                node_tags['id'] = element.attrib['id']
                node_tags['type'] = 'simple'
                node_tags['key'] = child.attrib['k']
                node_tags['value'] = child.attrib['v'] 
                tags.append(node_tags)
        #return results -- 'node' structure
        return {'node': node_dic, 'node_tags': tags}
    #extract 'way' elements
    elif element.tag == 'way':
        # loop the header of way, if element has a key, add it to dictionary
        for key in way_keys:
            way_dic[key] = element.attrib[key]
        counter = 0 #count the number of nd, save as position
        #loop child nodes of parent nodes
        for child in element:
            way_nd = {} 
            way_tags = {} 
            #'node' tag in 'way'
            if child.tag == 'nd':
                #extract id from parents' node 
                way_nd['id'] = element.attrib['id']
                #extract ref as node_id
                way_nd['node_id'] = child.attrib['ref']
                #get the value of position -- each loop of nd will make counter + 1
                way_nd['position'] = counter
                counter += 1
                way_nodes.append(way_nd)
            elif child.tag == 'tag': 
                colon = re.match(lower_colon,child.attrib['k'])
                problem = re.match(problemchars,child.attrib['k'])
                if problem:
                    continue
                elif colon:
                    way_tags['id'] = element.attrib['id']
                    type_value = child.attrib['k'].split(':',1)[0]
                    way_tags['key'] = child.attrib['k'].split(':',1)[1]
                    way_tags['type'] = type_value
                    way_tags['value'] = child.attrib['v']
                    tags.append(way_tags)
                else:
                    way_tags['id'] = element.attrib['id']
                    way_tags['key'] = child.attrib['k']
                    way_tags['type'] = 'simple'
                    way_tags['value'] = child.attrib['v']
                    tags.append(way_tags)
        return {'way': way_dic, 'way_nodes': way_nodes, 'way_tags': tags}


def get_element(osm_file, tags = ('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""
    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

               
if __name__ == "__main__":

    with codecs.open(node_file , 'w') as nodes_file, \
         codecs.open(node_tag_file, 'w') as nodes_tags_file, \
         codecs.open(ways_file, 'w') as ways_file, \
         codecs.open(ways_node_file , 'w') as way_nodes_file, \
         codecs.open(ways_tag_file, 'w') as way_tags_file:
             # dictwriters
             nodes_file_writer = csv.DictWriter(nodes_file, node_keys)
             nodes_file_writer.writeheader()
             
             nodes_tags_file_writer = csv.DictWriter(nodes_tags_file, node_tags_keys)
             nodes_tags_file_writer.writeheader()
             
             ways_file_writer = csv.DictWriter(ways_file, way_keys)
             ways_file_writer.writeheader()
             
             ways_node_file_writer = csv.DictWriter(way_nodes_file, way_nodes_keys)
             ways_node_file_writer.writeheader()
             
             ways_tag_file_writer = csv.DictWriter(way_tags_file, way_tags_keys)
             ways_tag_file_writer.writeheader()

             for element in get_element(osm_file, tags = ('node', 'way')):
                 ele = shape_element(element)
                 if ele:
                     if element.tag == 'node':
                         nodes_file_writer.writerow(ele['node'])
                         nodes_tags_file_writer.writerows(ele['node_tags'])
                     elif element.tag == 'way':
                         ways_file_writer.writerow(ele['way'])
                         ways_node_file_writer.writerows(ele['way_nodes'])
                         ways_tag_file_writer.writerows(ele['way_tags'])
             
             

    
    
    

    
    
    