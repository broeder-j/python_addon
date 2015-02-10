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

def apply_manipulator(data, idx, opt, error = False):
    if opt.acc[idx] == 1:
        if error:
            data = np.sqrt(np.add.accumulate(np.square(data)))
        else:
            data = np.add.accumulate(data)
    return data
    
def plot(args = parameter):
    #------------------- get file names -------------------
    p = args
    files = p["arg"]
    
    #=================== helper fct ===================
    #------------------- convert txt to xml, conv specifies dest location -------------------
    if "conv" in p.param:
        for file_ in files:
            txt_to_xml(file_, p.conv)
        return
    
    #------------------- read all file in namespace plot -------------------
    nsp = []
    for file_ in files:
        nsp.append(xml_to_plot(file_))
    
    #------------------- copy plot_options from file specified in cp_opt -------------------
    if "cp_opt" in p.param:
        ncp = xml_to_plot(p.cp_opt)
        opt = ncp.plot_option
        for nsx in nsp:
            nsx.plot_option_to_xml(opt, mod="overwrite")
            GREEN("{green}copied plot_options from {greenb}{} {green}to {greenb}{}{green}".format(p.cp_opt, nsx.file_, **color))
        return
        #~ <plot_option acc="[0, 1]" border="[0.01, 0.02]" legend_loc="center" o="./sharc_plot/S2_sqr_18.pdf" title="foo" x="x" xlabel="$\frac{a}{b}$" xticks="[0, 18, 3]" y="['entropy', 'entropy']" yerr="['error', 'error']" ylabel="['entropy der', 'entropy']" yticks="[0, 6, 2]" />
    #------------------- show available labels -------------------
    nsx = nsp[0]
    if p.has_flag("l"):
        print(nsx.label)
        return
    
    #=================== plot ===================
    #------------------- prepare plot opt dict -------------------
    valid_plot_option = [
                       # data
                         "x"
                       , "y"
                       , "xerr"
                       , "yerr"
                       # manipulation
                       , "acc"
                       # destination
                       , "o"
                       # style
                       , "title"
                       , "xticks"
                       , "yticks"
                       , "xlabel"
                       , "ylabel"
                       , "border"
                       , "legend_loc"
                       ]
    
    #------------------- defaults options -------------------
    legend_dict = {"best": 0, "upper_right": 1, "upper_left": 2, "lower_left": 3, "lower_right": 4, "right": 5, "center_left": 6, "center_right": 7, "lower_center": 8, "upper_center": 9, "center": 10}
    opt = namespace()
    opt.legend_loc = "best"
    opt.o = "unnamed.png"
    opt.x = 0
    opt.y = 1
    opt.border = .05
    opt.update(dict_select(nsx.plot_option, valid_plot_option)) #overwrite by xml info
    opt.update(dict_select(p, valid_plot_option))               #overwrite by argv info
    
    #------------------- delete parameter if given as flags -------------------
    for f in p.flag:
        if f in opt.keys():
            del opt[f]
    
    opt_save = copy.deepcopy(opt) # for saving (we want to keep human readable labels, not 1,2,0)
            
    
    #------------------- convert labels/string to numbers -------------------
    label_to_number = lambda x: (-1 if x == "none" else nsx.label.index(x)) if is_str(x) else x
    get_label = lambda lbl_nr, label, idx = None: (opt[label] if idx == None else opt[label][idx]) if label in opt.keys() else nsx.label[lbl_nr]
    
    if is_str(opt.legend_loc):
        opt.legend_loc = legend_dict[opt.legend_loc]
        
    opt.x = label_to_number(opt.x)
    
    opt.y = make_list(opt.y)
    for i in range(len(opt.y)):
        opt.y[i] = label_to_number(opt.y[i])
    
    if "xerr" in opt.keys():
        opt.xerr = label_to_number(opt.xerr)
    if "yerr" in opt.keys():
        opt.yerr = make_list(opt.yerr)
        for i in range(len(opt.yerr)):
            opt.yerr[i] = label_to_number(opt.yerr[i])
    
    #=================== main plot ===================
    fig, ax = pyplot.subplots()
    colors = collections.deque(["r^-", "b^-", "g^-", "y^-"])
    
    additional = {}
    plot_fct = ax.errorbar
    
    #------------------- set x data -------------------
    xdata = nsx.data[opt.x]
    if "xerr" in opt.keys():
        additional["xerr"] = nsx.data[opt.xerr]
    
    #------------------- set (multiple) y data -------------------
    for y, y_i in zipi(opt.y):
        ydata = apply_manipulator(nsx.data[y], y_i, opt)
        if "yerr" in opt.keys() and opt.yerr[y_i] != -1:
            additional["yerr"] = apply_manipulator(nsx.data[opt.yerr[y_i]], y_i, opt, error = True)
        
        additional["fmt"] = colors[0]
        colors.rotate(-1)
        plot_fct(xdata, ydata, markersize = 3, label = get_label(y, "ylabel", y_i), **additional)
        
        update_lim(xdata, ydata)
    
    #------------------- set lims -------------------
    set_lim(ax, opt.border)
    
    #------------------- set title -------------------
    if "title" in opt.keys():
        ax.set_title(opt.title)
    
    #------------------- set labels / legend -------------------
    if "xticks" in opt.keys():
        low, upper, incr = opt.xticks
        ax.set_xticks(range(low, upper+incr, incr))
    if "yticks" in opt.keys():
        low, upper, incr = opt.yticks
        ax.set_yticks(range(low, upper+incr, incr))
    
    ax.set_xlabel(get_label(opt.x, "xlabel"))
    if len(opt.y) == 1:
        ax.set_xlabel(get_label(opt.y[0], "ylabel", 0))
    else:
        ax.legend(loc = opt.legend_loc)
    
    fig.savefig(opt.o)
    
    nsx.plot_option_to_xml(opt_save, mod="overwrite")
