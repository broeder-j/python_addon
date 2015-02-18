#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 
# Author:  Mario S. Könz <mskoenz@gmx.net>
# Date:    24.01.2015 14:45:10 CET
# File:    xml_parser.py

from ..helper import *

from .txt_to_xml import *
from .xml_helper import *

import xml.etree.ElementTree as xml
import numpy as np

def plot_option_to_xml(nsx, popt, sel = 0, mod = "update"):
    opts = nsx.root.find("plot_option")
    
    popt = dict([(k, to_str(v)) for k, v in popt.items()])
    
    if opts == None: #------------------- create new element if tag not found -------------------
        opts = xml.Element("plot_option")
        opts.append(xml.Element("opt", popt))
        nsx.root.insert(0, opts)
    else: #------------------- update or overwrite current tag -------------------
        opt = opts.findall("opt")
        if len(opt) <= sel:
            for i in range(sel - len(opt) + 1):
                opts.append(xml.Element("opt"))
        
        opt = opts.findall("opt")
        
        if mod == "update":
            opt[sel].attrib.update(popt)
        elif mod == "overwrite":
            opt[sel].attrib = popt
    
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
    nsx.data = transpose(to_number(split_clean([c.text for c in nsx.root.find("data").findall("d")])))
    
    opts = nsx.root.find("plot_option")
    if opts == None:
        nsx.plot_option = [{}]
        nsx.source = None
    else:
        opt = opts.findall("opt")
        nsx.source = to_number(opts.attrib)
        nsx.plot_option = [to_number(p.attrib) for p in opt]
    
    nsx.plot_option_to_xml = lambda popt, sel = 0, mod = "update": plot_option_to_xml(nsx, popt, sel, mod)
    
    return nsx
