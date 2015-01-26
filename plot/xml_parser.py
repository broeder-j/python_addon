#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 
# Author:  Mario S. Könz <mskoenz@gmx.net>
# Date:    24.01.2015 14:45:10 CET
# File:    xml_parser.py

from ..helper import *

import xml.etree.ElementTree as xml
import numpy as np

def prettify(node, indent = "    ", level = 0):
    node.tail = "\n" + indent * level
    if len(node) != 0:
        node.text = "\n" + indent * (level + 1)
        for c in node:
            prettify(c, indent, level + 1)
            if c == node[-1]:
                c.tail = "\n" + indent * level
    else:
        if node.text:
            node.text = node.text.strip()
        node.tail = "\n" + indent * level

def plot_option_to_xml(nsx, popt, mod = "update"):
    p = nsx.root.find("plot_option")
    
    popt = dict([(k, str(v)) for k, v in popt.items()])
    
    if p == None: #------------------- create new element if tag not found -------------------
        p = xml.Element("plot_option", popt)
        nsx.root.insert(0, p)
    else: #------------------- update or overwrite current tag -------------------
        if mod == "update":
            p.attrib.update(popt)
        elif mod == "overwrite":
            p.attrib = popt
    
    #------------------- make xml nicer (it changes and strips text) -------------------
    prettify(nsx.root)
    # write back to file
    nsx.tree.write(nsx.file_, encoding="utf-8", xml_declaration = True)


def xml_to_plot(file_):
    nsx = namespace()
    nsx.file_ = file_
    
    nsx.tree = xml.parse(nsx.file_)
    nsx.root = nsx.tree.getroot()
    
    nsx.param = nsx.root.find("parameter").attrib # i.o. not to collide with HTML "param"
    nsx.label = split_clean(nsx.root.find("label").text)
    nsx.data = np.array(to_number(split_clean([c.text for c in nsx.root.find("data").findall("d")]))).transpose()
    
    p = nsx.root.find("plot_option")
    if p == None:
        nsx.plot_option = {}
    else:
        nsx.plot_option = to_number(p.attrib)
    
    nsx.plot_option_to_xml = lambda popt, mod = "update": plot_option_to_xml(nsx, popt, mod)
    
    return nsx
