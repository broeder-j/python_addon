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

import collections
import copy

lower_min = np.array([ np.inf,  np.inf])
upper_max = np.array([-np.inf, -np.inf])

def update_lim(xdata, ydata):
    if lower_min[0] == np.inf:
        lower_min[0] = min(lower_min[0], min(xdata))
        upper_max[0] = max(upper_max[0], max(xdata))
    lower_min[1] = min(lower_min[1], min(ydata))
    upper_max[1] = max(upper_max[1], max(ydata))

def set_lim(ax, border):
    if is_list(border):
        dperc = np.array(border)
    else:
        dperc = np.array([border, border])
    
    range_ = upper_max - lower_min
    
    lower = lower_min - range_ * dperc
    upper = upper_max + range_ * dperc
    ax.set_xlim(lower[0], upper[0])
    ax.set_ylim(lower[1], upper[1])

def plot():
    #------------------- get file names -------------------
    p = parameter
    files = p["arg"]
    
    #------------------- read all file in namespace plot -------------------
    nsp = []
    
    for file_ in files:
        nsp.append(xml_to_plot(file_))
    
    #=================== plot ===================
    nsx = nsp[0]
    if p.has_flag("l"):
        print(nsx.label)
        return
    
    #------------------- prepare plot opt dict -------------------
    valid_plot_option = ["x", "y", "yerr", "o", "border", "legend_loc", "title"]
    
    
    
    #------------------- defaults options -------------------
    legend_dict = {"best": 0, "upper_right": 1, "upper_left": 2, "lower_left": 3, "lower_right": 4, "right": 5, "center_left": 6, "center_right": 7, "lower_center": 8, "upper_center": 9, "center": 10}
    opt = namespace()
    opt.legend_loc = legend_dict["best"]
    opt.o = "unnamed.png"
    opt.x = 0
    opt.y = 1
    opt.border = .05
    opt.update(dict_select(nsx.plot_option, valid_plot_option)) #overwrite by xml info
    opt.update(dict_select(p, valid_plot_option))               #overwrite by argv info
    
    for f in p.flag:
        if f in opt.keys():
            del opt[f]
    
    if is_str(opt.legend_loc):
        opt.legend_loc = legend_dict[opt.legend_loc]
    
    #------------------- convert labels to numbers and copy -------------------
    label_to_number = lambda x: nsx.label.index(x) if is_str(x) else x
    
    x = label_to_number(opt.x)
    
    yl = copy.deepcopy(make_list(opt.y))
    for i in range(len(yl)):
        yl[i] = label_to_number(yl[i])
    
    if "yerr" in opt.keys():
        yerrl = copy.deepcopy(make_list(opt.yerr))
        for i in range(len(yerrl)):
            yerrl[i] = label_to_number(yerrl[i])
    
    fig, ax = pyplot.subplots()
    colors = collections.deque(["r^-", "b^-", "g^-", "y^-"])
    additional = {}
    plot_fct = ax.errorbar
    
    ax.set_xlabel(nsx.label[x])
    xdata = nsx.data[x]
    if "xerr" in opt.keys():
        xerr = label_to_number(opt.xerr)
        additional["xerr"] = nsx.data[xerr]
    
    for y, y_i in zipi(yl):
        ydata = nsx.data[y]
        additional["fmt"] = colors[0]
        colors.rotate(-1)
        if "yerr" in opt.keys():
            additional["yerr"] = nsx.data[yerrl[y_i]]
        
        plot_fct(xdata, ydata, markersize = 3, label = nsx.label[y], **additional)
        
        update_lim(xdata, ydata)
    
    #------------------- set title -------------------
    if "title" in opt.keys():
        ax.set_title(opt.title)
    #------------------- set lims -------------------
    set_lim(ax, opt.border)
    
    #------------------- set labels / legend -------------------
    if len(opt.y) == 1:
        ax.set_ylabel(nsx.label[opt.y[0]])
    else:
        ax.legend(loc = opt.legend_loc)
    
    fig.savefig(opt.o)
    
    nsx.plot_option_to_xml(opt, mod="overwrite")
