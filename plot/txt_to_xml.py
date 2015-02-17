#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 
# Author:  Mario S. Könz <mskoenz@gmx.net>
# Date:    10.02.2015 10:05:32 CET
# File:    txt_parser.py

from ..helper import *
from ..parameter import *
from .xml_helper import *

import xml.etree.ElementTree as xml
import numpy as np

def txt_to_xml(file_, dest, p):
    comment = p.get("comment", ["-", "#"])
    
    if not readable(file_):
        ERROR("could not read {}".format(src))

    if filetype(dest) == None: #if folder
        create_folder(dest)
        dest += "/" + filename(file_, suffix = "xml")
    
    ifs = open(file_, "r")
    #------------------- data -------------------
    label = []
    data =  []
    param = {}
    #------------------- read txt file -------------------
    all_lines = ifs.readlines()
    if all_lines[1][:6] == "#param": #read param line if there
        for param_item in split_clean(all_lines[1][6:]):
            key, val = to_number(param_item.split("="))
            param[key] = val
    
    lines = [to_number(split_clean(l)) for l in all_lines if l[0] not in comment]
    label = lines[0]
    
    data = transpose(lines[1:])
    
    #------------------- transform indentical data to parameter -------------------
    #~ del_idx = []
    #~ for k in range(len(data)):
        #~ same = True
        #~ for i in range(len(data[k])):
            #~ if i == 0:
                #~ compare = data[k][i]
            #~ else:
                #~ if compare != data[k][i]:
                    #~ same = False
                    #~ break
        #~ if same:
            #~ del_idx.insert(0, k)
            #~ param[label[k]] = str(compare)
    #~ 
    #~ for d in del_idx:
        #~ del data[d]
        #~ del label[d]

    data = transpose(data)
    #------------------- generate/read xml -------------------
    if readable(dest):
        tree   = xml.parse(dest)
        root   = tree.getroot()
        Eopt   = root.find("plot_option")
        Eopt.attrib["file_"] = file_
        Eopt.attrib["comment"] = to_str(comment)
        Eparam = root.find("parameter")
        Eparam.clear()
        Elabel = root.find("label")
        Elabel.clear()
        Edata  = root.find("data")
        Edata.clear()
    else:
        root   = xml.Element("plot")
        Eopt   = xml.Element("plot_option", {"file_": file_, "comment": to_str(comment)})
        Eparam = xml.Element("parameter")
        Elabel = xml.Element("label")
        Edata  = xml.Element("data")
        tree   = xml.ElementTree(root)
        root.append(Eopt)
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
    
    if "update" in p.flag:
        desc = "updated"
    else:
        desc = "converted"
    print("{yellow}{} {yellowb}{}{yellow} to {yellowb}{}{none}".format(desc, file_, dest, **color))
