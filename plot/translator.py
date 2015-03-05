#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 
# Author:  Mario S. Könz <mskoenz@gmx.net>
# Date:    17.02.2015 19:06:45 CET
# File:    translator.py

import string
import copy

from ..helper import *

def expand(key, opt, pns):
    relevant_labels = {"x": lambda x: is_list(x)
                     , "y": lambda x: is_list(x)
                     , "xerr": lambda x: is_list(x)
                     , "yerr": lambda x: is_list(x)
                     , "ylabel": lambda x: is_list(x)
                     , "acc": lambda x: is_list(x)
                     , "triconv": lambda x: is_list(x)
                     , "linreg": lambda x: is_list(x[0])
                     , "dsel": lambda x: is_list(x[0])
                     , "psel": lambda x: is_list(x[0])
                     , "markersize": lambda x: is_list(x)
                     }
    minimal_len = 1
    if any([opt.get(k, " ")[0] == "#" for k in ["x", "y", "xerr", "yerr"] if is_str(opt.get(k, " "))]):
        minimal_len = len(pns.minor_param)
    max_ = max([minimal_len]+[len(opt[k]) for k in relevant_labels.keys() if k in opt.keys() and relevant_labels[k](opt[k])])
    
    if not relevant_labels[key](opt[key]):
        return [opt[key] for i in range(max_)]
    else:
        if len(opt[key]) != max_:
            ERROR("length of {} should be {} instaed of {} (or the other way)".format(key, max_, len(opt[key])))
        return opt[key]

def label_translator(key, opt, pns):
    def single_translate(val, idx):
        if val == "none": #for error
            return -1
        elif is_str(val):
            if key in ["xerr", "yerr"]:
                if val[0] == "p":
                    return opt[key[0]][idx] + to_number(val[1:])
                elif val[0] == "m":
                    return opt[key[0]][idx] - to_number(val[1:])
            
            if "#" in val: #lazy expansion
                val = val.replace("#", "{:0>2}".format(idx))
            
            
            
            if val not in pns.label:
                ERROR("{} is not in {}".format(val, pns.label))
            return pns.label.index(val)
        else:
            return val
    
    val = opt[key]
    if is_list(val):
        for lbl, lbl_i in zipi(val):
            val[lbl_i] = single_translate(lbl, lbl_i)
        return val
    else:
        return single_translate(val, None)

def o_translator(key, opt, pns):
    if filetype(opt[key]) == None:
        return opt[key] + "/" + filename(pns.file_, suffix = "pdf")
    else:
        return opt[key]

def legend_translator(key, opt, pns):
    legend_dict = {"best": 0, "upper_right": 1, "upper_left": 2, "lower_left": 3, "lower_right": 4, "right": 5, "center_left": 6, "center_right": 7, "lower_center": 8, "upper_center": 9, "center": 10}
    val = opt[key]
    return val
    if val in legend_dict.keys():
        return legend_dict[val]
    else:
        ASSERT(val in range(len(legend_dict)))
        return val

def latex_compatible(string):
    if len(string) > 2 and string[2] == "_":
        return string[3:]
    return string

def label_styler(key, opt, pns):
    def single_style(val, idx):
        dict_ = copy.deepcopy(pns.param)
        dict_["l"] = latex_compatible(pns.label[opt[key[0]][idx]])
        dict_["L"] = string.capwords(latex_compatible(pns.label[opt[key[0]][idx]]))
        dict_["#"] = idx
        if "minor_param" in pns.keys() and key == "ylabel":
            dict_.update(pns.minor_param[idx])
        return val.format(**dict_)
    
    val = opt[key]
    if is_list(val):
        for lbl, lbl_i in zipi(val):
            val[lbl_i] = single_style(lbl, lbl_i)
        return val
    else:
        return [single_style(val,0)]

def label_chooser(key, opt, pns, idx = 0):
    
    if key in opt.keys():
        return opt[key][idx]
    else:
        return latex_compatible(pns.label[opt[key[0]][idx]])

def ticks_converter(key, opt, lower_min, upper_max):
    low, upper, incr = opt[key]
    while low < lower_min:
        low += incr
    while upper > upper_max:
        upper -= incr
    
    return range(low, upper + incr, incr)

def identity(key, opt, pns):
    return opt[key]
