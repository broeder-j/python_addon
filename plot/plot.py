#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 
# Author:  Mario S. Könz <mskoenz@gmx.net>
# Date:    22.01.2015 14:27:01 CET
# File:    plot.py

from ..helper import *
from ..parameter import *

from .help_plot import *
from .xml_parser import *
from .translator import *
from .error_propagation import *
from .import_pyplot import *
from . import valid_options as vo

import copy
import collections

lower_min = np.array([ np.inf,  np.inf])
upper_max = np.array([-np.inf, -np.inf])

def reset_lim():
    global lower_min, upper_max
    lower_min = np.array([ np.inf,  np.inf])
    upper_max = np.array([-np.inf, -np.inf])

def update_lim(xdata, ydata):
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
        if opt.xlim[0] != "#":
            lower_min[0] = opt.xlim[0]
        if opt.xlim[1] != "#":
            upper_max[0] = opt.xlim[1]
    if "ylim" in opt.keys():
        if opt.ylim[0] != "#":
            lower_min[1] = opt.ylim[0]
        if opt.ylim[1] != "#":
            upper_max[1] = opt.ylim[1]
    
    range_ = upper_max - lower_min
    
    lower = lower_min - range_ * dperc
    upper = upper_max + range_ * dperc
    ax.set_xlim(lower[0], upper[0])
    ax.set_ylim(lower[1], upper[1])

def get_select(data, y_i, opt, kw):
    if kw in opt.keys():
        if len(opt[kw][y_i]) == 2:
            b, sp = opt[kw][y_i]
            e = len(data[0])
        else:
            b, e, sp = opt[kw][y_i]
        
        for i in range(len(data)):
            data[i] = data[i][b:e][0::sp]
        
    return data

def plot_handler(pns, p):
    #------------------- show available labels -------------------
    if "l" in p.flag:
        for l, l_i in zipi(pns.label):
            print("{green}pos {greenb}{:0>2}{green} = {green}{}{none}".format(l_i, l, **color))
        return
    #=================== plot ===================
    #------------------- valid plot options -------------------
    vpo = collections.OrderedDict([
           # data
             ("x", [label_translator, expand])
           , ("y", [label_translator, expand])
           , ("xerr", [label_translator, expand])
           , ("yerr", [label_translator, expand])
           # param
           , ("parameter", [])
           , ("parameter_loc", [])
           # manipulation
           , ("dsel", [expand])
           , ("psel", [expand])
           , ("linreg", [expand])
           # destination
           , ("o", [o_translator])
           , ("assoz_file", [])
           # style
           , ("alpha", [])
           , ("fontsize", [])
           , ("title", [])
           , ("size_inch", [])
           , ("style", [])
           , ("xticks", [])
           , ("yticks", [])
           , ("xlabel", [label_styler])
           , ("ylabel", [label_styler, expand])
           , ("ylabel2", [label_styler])
           , ("xlim", [])
           , ("ylim", [])
           , ("border", [])
           , ("markersize", [expand])
           , ("legend_loc", [legend_translator])
           , ("ncol", [])
           ])
    
    #------------------- force sync -------------------
    if set(vo.valid_options) != set(vpo.keys()):
        ERROR("update valid_options.py or plot.py! diff in valid_options: {}".format(set(vpo.keys()).symmetric_difference(set(vo.valid_options))))
    
    #------------------- defaults options -------------------
    opt = namespace()
    opt.legend_loc = "best"
    opt.o = "unnamed.pdf"
    opt.x = 0
    opt.y = 1
    opt.border = .02
    opt.style = ["r^-", "b^-", "g^-", "y^-"] 
    opt.size_inch = [8.0, 6.0]
    spez = namespace()
    spez.isel = p.isel # has to be set
    spez.osel = p.get("osel", spez.isel)
    
    if pns != None and len(pns.plot_option) > spez.isel:
        opt.update(dict_select(pns.plot_option[spez.isel], vpo.keys())) #overwrite by xml info
    opt.update(dict_select(p, vpo.keys()))               #overwrite by argv info
    
    #------------------- delete parameter if given as flags -------------------
    for f in p.flag:
        if f in opt.keys():
            del opt[f]
    
    opt_save = copy.deepcopy(opt) # for saving (we want to keep human readable labels, not 1,2,0)
    
    #------------------- non save defaults -------------------
    opt.fontsize = opt.get("fontsize", 12)
    opt.linreg = opt.get("linreg", "none")
    opt.markersize = opt.get("markersize", 6)
    opt.usetex = p.usetex
    
    #=================== help and config print ===================
    if print_conf(p, opt):
        return 
    if print_help(p):
        return 
    
    for k, pipe in vpo.items():
        if k in opt.keys():
            for fct in reversed(pipe): # order: matrix mult convention
                opt[k] = fct(k, opt, pns)
            #~ print(k, opt[k])
    
    #=================== main plot ===================
    fig, ax = pyplot.subplots()
    opt.style = collections.deque(opt.style)
    
    additional = {}
    plot_fct = ax.errorbar
    
    for y, y_i in zipi(opt.y):
        data = copy.deepcopy(pns.data)
        #------------------- apply manipulatros to data -------------------
        data = get_select(data, y_i, opt, "dsel")
        
        #------------------- set data -------------------
        xdata, xerr = calc_expr(pns.label, data, opt.x[y_i])
        ydata, yerr = calc_expr(pns.label, data, opt.y[y_i])
        
        if xerr != None:
            additional["xerr"] = xerr
        if yerr != None:
            additional["yerr"] = yerr
        
        #------------------- get plot selection -------------------
        data = get_select(data, y_i, opt, "psel")
        
        #------------------- style -------------------
        additional["markersize"] = opt.markersize[y_i]
        additional["fmt"] = opt.style[0]
        opt.style.rotate(-1)
        
        plot_fct(xdata, ydata, label = label_chooser("ylabel", opt, pns, y_i), **additional)
        update_lim(xdata, ydata)
        #------------------- linreg -------------------
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
        ax.set_title(opt.title.format(**pns.param), fontsize = opt.fontsize)
    
    #------------------- set labels / legend -------------------
    if "xticks" in opt.keys():
        ax.set_xticks(ticks_converter("xticks", opt, lower_min[0], upper_max[0]))
    if "yticks" in opt.keys():
        ax.set_yticks(ticks_converter("yticks", opt, lower_min[1], upper_max[1]))
    
    ax.set_xlabel(label_chooser("xlabel", opt, pns), fontsize = opt.fontsize)
    if len(opt.y) == 1:
        ax.set_ylabel(label_chooser("ylabel", opt, pns), fontsize = opt.fontsize)
    else:
        ax.legend(loc = opt.legend_loc
                , framealpha = opt.get("alpha", 1)
                , fontsize = opt.fontsize
                , ncol = opt.get("ncol", 1)
                 )
        if "ylabel2" in opt.keys():
            ax.set_ylabel(opt.ylabel2[0], fontsize = opt.fontsize)
    
    #------------------- set parameter box -------------------
    if "parameter" in opt.keys():
        if opt.parameter == "all":
            opt.parameter = ""
            for k in pns.param.keys():
                opt.parameter += k + ": {" + k + "}{nl}"
            opt.parameter = opt.parameter[:-4]
        loc = opt.get("parameter_loc", [0.5, 0.5])
        
        text = opt.parameter.format(**merge_dict({"nl": "\n"}, pns.param))
        
        ax.text(loc[0]
              , loc[1]
              , text
              , transform=ax.transAxes
              , fontsize = opt.fontsize
              , verticalalignment='center'
              , horizontalalignment='center'
              , bbox=dict(boxstyle='square', facecolor=background_color, edgecolor=grid_color, alpha = opt.get("alpha", 1))
        )
    
    
    fig.set_size_inches(*opt.size_inch)
    fig.tight_layout()
    
    create_folder(path(opt.o))
    fig.savefig(opt.o)
    
    pns.plot_option_to_xml(opt_save, sel = spez.osel, mod="overwrite")
    print("{green}plotted {greenb}{} {green}to {greenb}{}{green} with selection {greenb}{}{green} (-> {}){none}".format(pns.file_, opt.o, spez.isel, spez.osel, **color))
    reset_lim()

def join_pns(all_pns, p):
    if len(all_pns) == 0:
        return None
        
    elif len(all_pns) == 1:
        return all_pns[0]
        
    else:
        all_param = []
        for ns, ns_i in zipi(all_pns):
            if ns_i == 0:
                pns = ns
                p.isel = p.get("isel", 1)
                
                pns.label = ["_{:0>2}_{}".format(ns_i, l) for l in pns.label]
                pns.data = list(pns.data)
                s = set(pns.param.items())
            else:
                pns.data += list(ns.data)
                pns.label += ["_{:0>2}_{}".format(ns_i, l) for l in ns.label]
                s = s.intersection(set(ns.param.items()))
        
        # different parameters
        pns.minor_param = [dict([item for item in ns.param.items() if item not in dict(s).items()]) for ns in all_pns]
        # equal parameters for all files
        pns.param = dict(s)
        
        return pns
    
def plot(p = parameter):
    p.flag = p.get("flag", []) #since a namespace may lack flag
    files = p.arg
    
    p.usetex = p.get("usetex", 1)
    if p.usetex:
        usetex()
    
    if "conv" in p.keys():
        for file_ in files:
            txt_to_xml(file_, p.conv, p)
        return
    
    if "update" in p.flag:
        for file_ in files:
            pns = xml_to_plot(file_)
            dir_ = path(file_)
            if pns.source != None:
                p.comment = p.get("comment", pns.source["comment"])
                txt_to_xml(pns.source["file_"], pns.file_, p)
        return
    
    if "cp_opt" in p.keys() or "cp_opt" in p.flag:
        if "cp_opt" in p.keys():
            isel, osel =  p.cp_opt
        else:
            isel, osel =  0, 0
        
        opt = xml_to_plot(files[0]).plot_option
        for file_ in files[1:]:
            xml_to_plot(file_).plot_option_to_xml(opt[isel], sel = osel, mod="overwrite")
            YELLOW("copied opt {yellowb}{} {yellow}from {yellowb}{} {yellow}to {yellowb}{} {yellow}opt {yellowb}{}".format(isel, files[0], file_, osel, **color))
        return
    
    
    #------------------- read first file -------------------
    all_pns = []
    file_ = files[0]
    tree = file_to_tree(file_, p)
    pns0 = tree_to_plot(tree, file_)
    all_pns.append(pns0)
    
    #------------------- read assoz file -------------------
    if len(files) > 1:
        if "parallel" in p.flag:
            p.isel = p.get("isel", 0)
            for file_ in files[1:]:
                file_ = file_
                tree = file_to_tree(file_, p)
                all_pns.append(tree_to_plot(tree, file_))
        else:
            p.isel = p.get("isel", 1)
            if p.isel < len(pns0.plot_option) and "assoz_file" in pns0.plot_option[p.isel].keys():
                p.assoz_file = pns0.plot_option[p.isel]["assoz_file"]
            else:
                p.assoz_file = [relpath(f, path(files[0])) for f in files[1:]]
            
            for file_ in p.assoz_file:
                file_ = path(files[0]) + "/" + file_
                tree = file_to_tree(file_, p)
                all_pns.append(tree_to_plot(tree, file_))
    else:
        p.isel = p.get("isel", 0)
    
    #------------------- execute plot -------------------
    if "parallel" in p.flag:
        for pns in all_pns:
            plot_handler(pns, p)
    else:
        pns = join_pns(all_pns, p)
        plot_handler(pns, p)
        
def plot2(args = parameter):
    if "parallel" in p.flag:
        if "split" in p.keys() and "a3data" in p.keys():
            #------------------- prepare join namespace -------------------
            join = namespace()
            join.label = nsp[0].label + [p.a3data[0]]
            join.data = [[] for i in range(len(nsp[0].data) + 1)]
            
            #------------------- join all data -------------------
            for ns, ns_i in zipi(nsp):
                for d, d_i in zipi(ns.data):
                    join.data[d_i] += list(d)
                join.data[-1] += [p.a3data[ns_i+1] for i in range(len(d))]
            
            join.data = transpose(join.data)
            join.data = sorted(join.data, key = lambda x: x[p.split])
            
            #------------------- write out .txt files -------------------
            join.data = split_list(join.data, key = lambda x: x[p.split])
            
            for data, data_i in zipi(join.data):
                #------------------- extract identical data to dict_ -------------------
                dict_ = {}
                for l, l_i in zipi(join.label):
                    compare = data[0][l_i]
                    for i in range(1, len(data)):
                        if compare != data[i][l_i]:
                            break
                    else:
                        dict_[l] = compare
                
                file_ = p.o.format(**dict_)
                create_folder(path(file_))
                
                if file_[-3:] == "txt":
                    ofs = open(file_, "w")
                    ofs.write(" ".join(join.label)+"\n")
                    for d in data:
                        ofs.write(" ".join([str(x) for x in d])+"\n")
                    GREEN("written {greenb}{}".format(file_, **color))
                    ofs.close()
                elif file_[-3:] == "xml":
                    temp = open("temp.txt", "w")
                    temp.write(" ".join(join.label)+"\n")
                    for d in data:
                        temp.write(" ".join([str(x) for x in d])+"\n")
                    temp.close()
                    
                    txt_to_xml("temp.txt", file_)
                
                bash("rm temp.txt", silent = True)
    
