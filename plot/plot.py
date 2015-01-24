#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 
# Author:  Mario S. Könz <mskoenz@gmx.net>
# Date:    22.01.2015 14:27:01 CET
# File:    plot.py

from ..helper import *
from ..parameter import *

from .xml_parser import *
from .import_pylab import *

def plot():
    #------------------- get file names -------------------
    p = parameter
    files = p["arg"]
    
    print(files)
    
    #------------------- namespace plot -------------------
    nsp = [] 
    
    for file_ in files:
        nsp.append(xml_to_plot(file_))
    
    for n in nsp:
        print(n)
    
    #~ can = namespace(canonical)
    #~ print(can)
    #~ root.append(xml.Element("foo", {"a": "bla"}))
    
    
