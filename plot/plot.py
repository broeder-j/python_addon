#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 
# Author:  Mario S. Könz <mskoenz@gmx.net>
# Date:    22.01.2015 14:27:01 CET
# File:    plot.py

from ..helper import *
from ..parameter import *

from .help_plot import *
from .xml_parser import *
from .import_pyplot import *

import collections
import copy

lower_min = np.array([ np.inf,  np.inf])
upper_max = np.array([-np.inf, -np.inf])

def reset_lim():
    global lower_min, upper_max
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

def plot_helper(nsx, p):
    #------------------- show available labels -------------------
    if p.has_flag("l"):
        for l, l_i in zipi(nsx.label):
            print("{green}pos {greenb}{:0>2}{green} = {green}{}{none}".format(l_i, l, **color))
        return
    #=================== plot ===================
    #------------------- prepare plot opt dict -------------------
    valid_plot_option = [
                       # data
                         "x"
                       , "y"
                       , "xerr"
                       , "yerr"
                       # param
                       , "parameter"
                       , "parameter_loc"
                       # manipulation
                       , "acc"
                       , "select"
                       , "linreg"
                       # destination
                       , "o"
                       # style
                       , "title"
                       , "size_inch"
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
    special_option = ["update", "isel", "osel", "conv", "l", "cp_opt", "conf"]
    
    
    #------------------- defaults options -------------------
    legend_dict = {"best": 0, "upper_right": 1, "upper_left": 2, "lower_left": 3, "lower_right": 4, "right": 5, "center_left": 6, "center_right": 7, "lower_center": 8, "upper_center": 9, "center": 10}
    opt = namespace()
    opt.legend_loc = "best"
    opt.o = "unnamed.pdf"
    opt.x = 0
    opt.y = 1
    opt.border = .05
    opt.style = ["r^-", "b^-", "g^-", "y^-"] 
    opt.size_inch = [8.0, 6.0]
    isel = p.get("isel", 0)
    osel = p.get("osel", isel)
    
    if len(nsx.plot_option) > isel:
        opt.update(dict_select(nsx.plot_option[isel], valid_plot_option)) #overwrite by xml info
    opt.update(dict_select(p, valid_plot_option))               #overwrite by argv info
    
    #------------------- delete parameter if given as flags -------------------
    for f in p.flag:
        if f in opt.keys():
            del opt[f]
    
    opt_save = copy.deepcopy(opt) # for saving (we want to keep human readable labels, not 1,2,0)
    
    #=================== help and config print ===================
    if p.has_key("conf"):
        print(nsx.source)
        print_conf(p, opt, legend_dict)
        return
    if p.has_key("help"):
        print_help(valid_plot_option, special_option, p.get("help", "all"))
        return
    
    #------------------- convert labels/string to numbers -------------------
    label_to_number = lambda x: (-1 if x == "none" else nsx.label.index(x)) if is_str(x) else x
    get_label = lambda lbl_nr, label, idx = None: (opt[label] if idx == None else opt[label][idx]) if label in opt.keys() else nsx.label[lbl_nr]
    
    if is_str(opt.legend_loc):
        opt.legend_loc = legend_dict[opt.legend_loc]
        
    opt.y = make_list(opt.y)
    if not is_list(opt.x):
        opt.x = [opt.x for i in range(len(opt.y))]
    
    for i in range(len(opt.x)):
        opt.x[i] = label_to_number(opt.x[i])
    
    for i in range(len(opt.y)):
        opt.y[i] = label_to_number(opt.y[i])
    
    if "xerr" in opt.keys():
        if not is_list(opt.yerr):
            opt.xerr = [opt.xerr  for i in range(len(opt.x))]
        for i in range(len(opt.xerr)):
            opt.xerr[i] = label_to_number(opt.xerr[i])
        
    if "yerr" in opt.keys():
        if not is_list(opt.yerr):
            opt.yerr = [opt.yerr  for i in range(len(opt.y))]
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
        if not is_list(opt.linreg[0]):
            opt.linreg = [opt.linreg for i in range(len(opt.y))]
    
    #------------------- lazy notation -------------------
    if opt.o[-4] != ".":
        opt.o += "/" + filename(nsx.file_)[:-4] + ".pdf"
    
    #=================== main plot ===================
    fig, ax = pyplot.subplots()
    opt.style = collections.deque(opt.style)
    
    additional = {}
    plot_fct = ax.errorbar
    
    
    for y, y_i in zipi(opt.y):
        #------------------- set x data -------------------
        xdata = nsx.data[opt.x[y_i]]
        if "xerr" in opt.keys():
            additional["xerr"] = nsx.data[opt.xerr[y_i]]
        
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
    
    ax.set_xlabel(get_label(opt.x[0], "xlabel"))
    if len(opt.y) == 1:
        ax.set_ylabel(get_label(opt.y[0], "ylabel", 0))
    else:
        ax.legend(loc = opt.legend_loc)
        if "ylabel" in opt.keys():
            if len(opt.ylabel) > len(opt.y):
                ax.set_ylabel(opt.ylabel[-1])
    
    #------------------- set parameter box -------------------
    if "parameter" in opt.keys():
        if opt.parameter == "all":
            opt.parameter = ""
            for k in nsx.param.keys():
                opt.parameter += k + ": {" + k + "}{nl}"
            opt.parameter = opt.parameter[:-4]
        loc = opt.get("parameter_loc", [0, 0])
        
        text = opt.parameter.format(**merge_dict({"nl": "\n"}, nsx.param))
        
        ax.text(loc[0], loc[1]
            , text
            , transform=ax.transAxes
            , fontsize=12
            , verticalalignment='center'
            , horizontalalignment='left'
            , bbox=dict(boxstyle='square', facecolor=background_color, edgecolor=grid_color, alpha=1)
        )
    
    print("{green}ploted {greenb}{} {green}to {greenb}{}{green} with selection {greenb}{}{green} (-> {}){none}".format(nsx.file_, opt.o, isel, osel, **color))
    
    fig.set_size_inches(*opt.size_inch)
    #~ fig.subplots_adjust(left=0.05, right=.95, top=0.9, bottom=0.1)
    fig.tight_layout()
    fig.savefig(opt.o)
    
    nsx.plot_option_to_xml(opt_save, sel = osel, mod="overwrite")
    reset_lim()

def plot(args = parameter):
    #------------------- get file names -------------------
    p = args
    files = p["arg"]
    
    #=================== helper fct ===================
    #------------------- convert txt to xml, conv specifies dest location / update xml -------------------
    if "conv" in p.param:
        for file_ in files:
            txt_to_xml(file_, p.conv)
        return
    
    if "update" in p.flag:
        for file_ in files:
            dir_ = path(file_)
            nsx = xml_to_plot(file_)
            txt_to_xml(nsx.source, dir_)
    
    #------------------- read all file in namespace plot -------------------
    nsp = []
    for file_ in files:
        nsp.append(xml_to_plot(file_))
    
    #------------------- copy plot_options from file specified in cp_opt -------------------
    if "cp_opt" in p.param:
        ncp = nsp[0]
        opt = ncp.plot_option
        isel, osel =  p.cp_opt
        for nsx in nsp[1:]:
            nsx.plot_option_to_xml(opt[isel], sel = osel, mod="overwrite")
            GREEN("{green}copied plot_option from {greenb}{} {green}sel:{greenb}{} {green}to {greenb}{} {green}sel:{greenb}{}{green}".format(ncp.file_, isel, nsx.file_, osel, **color))
        return
    
    if "parallel" in p.flag:
        for ns in nsp:
            plot_helper(ns, p)
    else:
        #------------------- join data from different files -------------------    
        for ns, ns_i in zipi(nsp):
            if ns_i == 0:
                nsx = ns
                param_compare = nsx.param
                if len(nsp) > 1:
                    p.isel = p.get("isel", 1)
                    nsx.label = ["{:0>2}_{}".format(ns_i, l) for l in nsx.label]
                    nsx.data = list(nsx.data)
            else:
                if param_compare != ns.param:
                    ERROR("parameter not the same in {} and {}".format(nsx.file_, ns.file_))
                else:
                    nsx.data += list(ns.data)
                    nsx.label += ["{:0>2}_{}".format(ns_i, l) for l in ns.label]
        plot_helper(nsx, p)
