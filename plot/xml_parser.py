#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 
# Author:  Mario S. Könz <mskoenz@gmx.net>
# Date:    24.01.2015 14:45:10 CET
# File:    xml_parser.py

from ..helper import *

import xml.etree.ElementTree as xml

def xml_to_plot(file_):
    root = xml.parse(file_).getroot()
    
    res = namespace()
    
    res.param = root.find("parameter").attrib # i.o. not to collide with HTML "param"
    res.label = split_clean(root.find("label").text)
    res.data = to_number(split_clean([c.text for c in root.find("data").findall("d")]))
    res.file_ = file_
    res.xml_root = root
    
    return res
