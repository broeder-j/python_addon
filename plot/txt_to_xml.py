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

def find_nodes(tree):
    root   = tree.getroot()
    Eopt   = root.find("plot_option")
    Eparam = root.find("parameter")
    Elabel = root.find("label")
    Edata  = root.find("data")
    return Eopt, Eparam, Elabel, Edata

def get_old_tree(dest):
    tree   = xml.parse(dest)
    Eopt, Eparam, Elabel, Edata = find_nodes(tree)
    Eparam.clear()
    Elabel.clear()
    Edata.clear()
    return tree

def get_new_tree():
    root   = xml.Element("plot")
    Eopt   = xml.Element("plot_option")
    Eparam = xml.Element("parameter")
    Elabel = xml.Element("label")
    Edata  = xml.Element("data")
    tree   = xml.ElementTree(root)
    root.append(Eopt)
    root.append(Eparam)
    root.append(Elabel)
    root.append(Edata)
    return tree

def fill_data(tree, param, label, data, file_, comment):
    # idx addition
    if label[0] != "index":
        label.insert(0, "index")
        for line, line_i in zipi(data):
            line.insert(0, line_i)
    
    Eopt, Eparam, Elabel, Edata = find_nodes(tree)
    Eparam.attrib = param
    Elabel.text = " ".join(label)
    for line in data:
        d = xml.Element("d")
        d.text = " ".join([str(i) for i in line])
        Edata.append(d)
    Eopt.attrib["file_"] = file_
    Eopt.attrib["comment"] = to_str(comment)
    
def txt_to_intermed(file_, p):
    comment = p.get("comment", ["-", "#"])
    
    if not readable(file_):
        ERROR("could not read {}".format(src))
    
    ifs = open(file_, "r")
    #------------------- data -------------------
    label = []
    data =  []
    param = {}
    #------------------- read txt file -------------------
    all_lines = ifs.readlines()
    if len(all_lines[1]) > 6 and all_lines[1][:6] == "#param": #read param line if there
        for param_item in split_clean(all_lines[1][6:]):
            key, val = to_number(param_item.split("="))
            param[key] = val
    
    lines = [to_number(split_clean(l)) for l in all_lines if l[0] not in comment]
    label = lines[0]
    data = lines[1:]
    
    return param, label, data, file_, comment

def txt_to_tree(file_, p):
    tree = get_new_tree()
    l = txt_to_intermed(file_, p)
    fill_data(tree, *l)
    return tree

def txt_to_xml(file_, dest, p): #output
    #------------------- generate/read xml -------------------
    if filetype(dest) == None: #if folder
        create_folder(dest)
        dest += "/" + filename(file_, suffix = "xml")
    
    if readable(dest):
        tree = get_old_tree(dest)
    else:
        tree = get_new_tree()
    
    l = txt_to_intermed(file_, p)
    fill_data(tree, *l)
    
    prettify(tree.getroot())
    tree.write(dest, encoding="utf-8", xml_declaration = True)
    
    if "update" in p.flag:
        desc = "updated"
    else:
        desc = "converted"
    print("{yellow}{} {yellowb}{}{yellow} to {yellowb}{}{none}".format(desc, file_, dest, **color))
