#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 30 19:53:59 2017

@author: wendycui
"""

import xml.etree.ElementTree as ET  # Use cElementTree or lxml if too slow

OSM_FILE = "MyLA3.osm"  # Replace this with your osm file
SAMPLE_FILE = "MyLA_sample.osm"

k = 40 # Parameter: take every k-th top level element

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


with open(SAMPLE_FILE, 'w') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')
output.close()
with open(SAMPLE_FILE, 'ab') as output:

    # Write every kth top level element
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            output.write(ET.tostring(element, encoding='utf-8'))
output.close()

with open(SAMPLE_FILE, 'a') as output:
    output.write('</osm>')
output.close()
