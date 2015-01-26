#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 
# Author:  Mario S. Könz <mskoenz@gmx.net>
# Date:    22.01.2015 14:27:01 CET
# File:    plot.py

from ..helper import *
from ..parameter import *

from .xml_parser import *
from .import_pyplot import *

def plot():
    #------------------- get file names -------------------
    p = parameter
    files = p["arg"]
    
    #------------------- read all file in namespace plot -------------------
    nsp = []
    
    for file_ in files:
        nsp.append(xml_to_plot(file_))
    
    #------------------- plot -------------------
    
    nsx = nsp[0]
    
    valid_plot_option = ["x", "y", "name", "o"]
    
    opt = namespace(dict([(k, v) for k, v in nsx.plot_option.items() if k in valid_plot_option]))
    opt.update(dict([(k, v) for k, v in p.items() if k in valid_plot_option]))
    
    if p.has_flag("l"):
        print(nsx.label)
    
    fig, ax = pyplot.subplots()
    
    xdata = nsx.data[opt.x]
    ydata = nsx.data[opt.y]
    
    ax.set_xlabel(nsx.label[opt.x])
    ax.set_ylabel(nsx.label[opt.y])
    ax.plot(xdata, ydata, "r^-")
    ax.set_xlim(min(xdata)-1, max(xdata)+1)
    ax.set_ylim(min(ydata)-1, max(ydata)+1)
    fig.savefig(opt.o)
    
    nsx.plot_option_to_xml(opt, mod="update")
