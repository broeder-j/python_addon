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

def set_lim(ax, opt):
    border = opt.border
    
    if is_list(border):
        dperc = np.array(border)
    else:
        dperc = np.array([border, border])
    
    if "xlim" in opt.keys():
        lower_min[0] = opt.xlim[0]
        upper_max[0] = opt.xlim[1]
    if "ylim" in opt.keys():
        lower_min[1] = opt.ylim[0]
        upper_max[1] = opt.ylim[1]
    
    range_ = upper_max - lower_min
    
    lower = lower_min - range_ * dperc
    upper = upper_max + range_ * dperc
    ax.set_xlim(lower[0], upper[0])
    ax.set_ylim(lower[1], upper[1])

def apply_manipulator(data, idx, opt, error = False):
    if "acc" in opt.keys():
        if opt.acc[idx] == 1:
            if error:
                data = np.sqrt(np.add.accumulate(np.square(data)))
            else:
                data = np.add.accumulate(data)
        
    return data

def get_select(xdata, ydata, additional, y_i, opt):
    if "select" in opt.keys():
        if len(opt.select[y_i]) == 2:
            b, sp = opt.select[y_i]
            e = len(xdata)
        else:
            b, e, sp = opt.select[y_i]
        
        xdata = xdata[b:e][0::sp]
        ydata = ydata[b:e][0::sp]
        
        if "xerr" in additional.keys():
            additional["xerr"] = additional["xerr"][b:e][0::sp]
        if "yerr" in additional.keys():
            additional["yerr"] = additional["yerr"][b:e][0::sp]
    
    return xdata, ydata

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
                       , "select"
                       , "linreg"
                       # destination
                       , "o"
                       # style
                       , "title"
                       , "style"
                       , "xticks"
                       , "yticks"
                       , "xlabel"
                       , "ylabel"
                       , "xlim"
                       , "ylim"
                       , "border"
                       , "markersize"
                       , "legend_loc"
                       ]
    
    #------------------- defaults options -------------------
    legend_dict = {"best": 0, "upper_right": 1, "upper_left": 2, "lower_left": 3, "lower_right": 4, "right": 5, "center_left": 6, "center_right": 7, "lower_center": 8, "upper_center": 9, "center": 10}
    opt = namespace()
    opt.legend_loc = "best"
    opt.o = "unnamed.pdf"
    opt.x = 0
    opt.y = 1
    opt.border = .05
    opt.style = ["r^-", "b^-", "g^-", "y^-"] 
    
    opt.update(dict_select(nsx.plot_option, valid_plot_option)) #overwrite by xml info
    opt.update(dict_select(p, valid_plot_option))               #overwrite by argv info
    
    #------------------- delete parameter if given as flags -------------------
    for f in p.flag:
        if f in opt.keys():
            del opt[f]
    
    opt_save = copy.deepcopy(opt) # for saving (we want to keep human readable labels, not 1,2,0)
    
    if p.has_key("conf"):
        if p.has_flag("conf"):
            print(opt)
        if p.has_param("conf"):
            print(opt.print_item(p.conf))
            if p.conf == "style":
                print("possible colors:       b g r c m y k w")
                print("possible markers:      . , o v ^ < > 1 2 3 4 s p * h H + x D d | _")
                print("possible linestyles:   - -- -. :")
        return
    
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
        if not is_list(opt.yerr):
            opt.yerr = [opt.yerr  for i in range(len(opt.y))]
        else:
            opt.yerr = opt.yerr
        for i in range(len(opt.yerr)):
            opt.yerr[i] = label_to_number(opt.yerr[i])
    
    #------------------- handle shorthand notation -------------------
    if "acc" in opt.keys():
        if not is_list(opt.acc):
            opt.acc = [opt.acc for i in range(len(opt.y))]
    
    if "select" in opt.keys():
        if not is_list(opt.select[0]):
            opt.select = [opt.select for i in range(len(opt.y))]
    
    if "markersize" in opt.keys():
        if not is_list(opt.markersize):
            opt.markersize = [opt.markersize for i in range(len(opt.y))]
    
    if "linreg" in opt.keys():
        if not is_list(opt.linreg):
            opt.linreg = [opt.linreg for i in range(len(opt.y))]
    
    #=================== main plot ===================
    fig, ax = pyplot.subplots()
    opt.style = collections.deque(opt.style)
    
    for nsx in nsp:
        additional = {}
        plot_fct = ax.errorbar
        
        
        for y, y_i in zipi(opt.y):
            #------------------- set x data -------------------
            xdata = nsx.data[opt.x]
            if "xerr" in opt.keys():
                additional["xerr"] = nsx.data[opt.xerr]
            
            #------------------- set y data -------------------
            ydata = apply_manipulator(nsx.data[y], y_i, opt)
            if "yerr" in opt.keys() and opt.yerr[y_i] != -1:
                additional["yerr"] = apply_manipulator(nsx.data[opt.yerr[y_i]], y_i, opt, error = True)
            
            #------------------- style -------------------
            if "markersize" in opt.keys():
                additional["markersize"] = opt.markersize[y_i]
                
            additional["fmt"] = opt.style[0]
            opt.style.rotate(-1)
            
            #------------------- get plot selection -------------------
            xdata, ydata = get_select(xdata, ydata, additional, y_i, opt)
            
            plot_fct(xdata, ydata, label = get_label(y, "ylabel", y_i), **additional)
            update_lim(xdata, ydata)
            #------------------- linreg -------------------
            if "linreg" in opt.keys():
                linreg = opt.linreg[y_i]
                if linreg != "none":
                    m,b = np.polyfit(xdata, ydata, 1)
                    if is_list(linreg):
                        xdata = np.array(linreg)
                    ax.plot(xdata, m*xdata+b, opt.style[0])
                    opt.style.rotate(-1)
    
    #------------------- set lims -------------------
    set_lim(ax, opt)
    
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
        ax.set_ylabel(get_label(opt.y[0], "ylabel", 0))
    else:
        ax.legend(loc = opt.legend_loc)
    
    print("{green}ploted {greenb}{} {green}to {greenb}{}{none}".format(nsp[0].file_, opt.o, **color))
    fig.savefig(opt.o)
    
    nsp[0].plot_option_to_xml(opt_save, mod="overwrite")
