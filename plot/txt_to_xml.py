#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 
# Author:  Mario S. Könz <mskoenz@gmx.net>
# Date:    10.02.2015 10:05:32 CET
# File:    txt_parser.py

from ..helper import *
from .xml_helper import *

import xml.etree.ElementTree as xml
import numpy as np

def txt_to_xml(src, dest, comment = ["-"]):
    dest = dest + os.path.basename(src[:-3]) + "xml"
    
    ifs = open(src, "r")
    
    #------------------- data -------------------
    label = []
    data = []
    param = {}
    #------------------- read txt file -------------------
    lines = [to_number(split_clean(l)) for l in ifs.readlines() if l[0] not in comment]
    label = lines[0]
    
    data = transpose(lines[1:])
    
    #------------------- transform indentical data to parameter -------------------
    del_idx = []
    for k in range(len(data)):
        same = True
        for i in range(len(data[k])):
            if i == 0:
                compare = data[k][i]
            else:
                if compare != data[k][i]:
                    same = False
                    break
        if same:
            del_idx.insert(0, k)
            param[label[k]] = str(compare)
    
    for d in del_idx:
        del data[d]
        del label[d]
    
    data = transpose(data)
    #------------------- generate/read xml -------------------
    if readable(dest):
        tree   = xml.parse(dest)
        root   = tree.getroot()
        Eparam = root.find("parameter")
        Eparam.clear()
        Elabel = root.find("label")
        Elabel.clear()
        Edata  = root.find("data")
        Edata.clear()
    else:
        root   = xml.Element("plot")
        Eparam = xml.Element("parameter")
        Elabel = xml.Element("label")
        Edata  = xml.Element("data")
        tree   = xml.ElementTree(root)
        root.append(Eparam)
        root.append(Elabel)
        root.append(Edata)
    
    
    Eparam.attrib = param
    Elabel.text = " ".join(label)
    for line in data:
        d = xml.Element("d")
        d.text = " ".join([str(i) for i in line])
        Edata.append(d)
    
    
    prettify(root)
    
    tree.write(dest, encoding="utf-8", xml_declaration = True)
    
    print("{green}converted {greenb}{}{green} to {greenb}{}{none}".format(src, dest, **color))
