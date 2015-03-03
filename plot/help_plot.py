#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 
# Author:  Mario S. Könz <mskoenz@gmx.net>
# Date:    11.02.2015 11:12:27 CET
# File:    help_plot.py

from ..helper import *
from . import valid_options as vo


def print_help(p):
    sd = {}
    # special
    sd["l"] =      "flag:  show all labels"
    sd["update"] = "flag:  reloads the txt file specified in 'source' into this xml"
    sd["conv"] =   "param: convert all .txt files in 'arg' to .xml files with same name but in folder 'conv'"
    sd["cp_opt"] = "param: [isel, osel], copy the plot_option::opt node 'isel' from the 'arg[0]' xml-file to each xml-file in 'arg[1:]' to position 'osel'"
    sd["isel"]   = "param: from plot_options use the opt node number 'isel'. Default is 0 if one file in 'arg', 1 otherwise"
    sd["osel"]   = "param: save the options to the opt node number 'osel' in plot_options. Will create new opt nodes is neccessary"
    sd["conf"]   = "flag/param: shows the selected ('isel') options. If used as parameter, it will only show the option for the 'conf', i.e. 'conf' = 'x'"
    sd["parallel"]= "flag: treat multiple files parallel as single files"
    sd["help"]= "flag/param: shows the entire help if flag, otherwise just help for the 'help'"
    
    # data
    sd["x"] =      "param: can be an index, text or list of those. If not a list, the same 'x' will be used for all 'y'"
    sd["y"] =      "param: can be an index, text of list of those. All 'y' lines will be plotted"
    sd["xerr"] =   "param: can be an index, text or list of those. If not a list, the same 'xerr' is used for all 'x'. Use p1 or m1 to select column relative to 'x'"
    sd["yerr"] =   "param: can be an index, text or list of those. If not a list, the same 'yerr' is used for all 'y'. Use p1 or m1 to select column relative to 'y'"
    # param
    sd["parameter"] =    "param: string with {p} where p has to be in 'param' attributes. Will be formated against this dict."
    sd["parameter_loc"] ="param: [x,y] between 0 and one, defines where the parameter table is"
    # manipulation
    sd["acc"] =    "param: can be in [0, 1] or a list of those. Specifies if the data and error of 'y' should be accumulated"
    sd["triconv"] ="param: N is an integer that specifies half of the triangle base length. Resamples with triangular weight distribution to smooth curves. Its a low-pass-ish filter."
    sd["dsel"] = "param: eighter [start, spacing], [start, end, spacing] or a list of those. Only data with index in 'select' are used further for manipulators"
    sd["psel"] = "param: eighter [start, spacing], [start, end, spacing] or a list of those. Only data with index in 'select' are plotted. Happens after the manipulators"
    sd["linreg"] = "param: [start, end] or a list of those. Performs a linear regression and plots in in range 'linreg'. Doesn't have a 'ylabel'"
    # destination
    sd["o"] =      "param: the plot will be saved in this location"
    # style
    sd["title"] =  "param: title of the plot, latex possible. One can use all parameter {key} in the xml-parameter"
    sd["fontsize"] =  "param: fontsize for parameter, legend, x/ylabel and title"
    sd["alpha"] =  "param: alpha (in [0, 1]) for parameter, legend"
    sd["size_inch"] = "param: [x, y], define dimensions of the figure in inches"
    sd["style"] =  "param: list for styling the curves, type -conf style to see options"
    sd["xticks"] = "param: [start, end, spacing] defined the ticks for 'x', end is included"
    sd["yticks"] = "param: [start, end, spacing] defined the ticks for 'y', end is included"
    sd["xlabel"] = "param: xlabel of the plot, can use {key} for key in major and minor dict and {#} for the filenumber and {l},{L} to get the native label"
    sd["ylabel"] = "param: string or list of strings. For multiple 'y' a legend will be created. Can use {key} for key in major and minor dict and {#} for the filenumber and {l},{L} to get the native label"
    sd["ylabel2"] ="param: string. In a plot with a legend, this will be used on the y-axis."
    sd["xlim"] =   "param: [start, end], plot window in x-direction, # is a placeholder for the automatic border."
    sd["ylim"] =   "param: [start, end], plot window in y-direction, # is a placeholder for the automatic border."
    sd["border"] = "param: number or [number, number]. Tells how many % border the framework should leave. 2% = 0.02"
    sd["markersize"] = "param: number or list of numbers. Specifies the size of the markers"
    sd["legend_loc"] = "param: number or text. Specifies where the legend will be. See -conf legend_loc for options"
    sd["ncol"]   = "param: number. Specifies how many columns the legend has, default is 1"
    
    pr = lambda cmd, desc: REDB("{:<10}{yellow}    {}".format(cmd, desc, **color))
    if "help" in p.flag:
        GREENB("valid Commands")
        for cmd in vo.valid_commands:
            pr(cmd, sd[cmd])
        GREENB("Valid Options")
        for cmd in vo.valid_options:
            pr(cmd, sd[cmd])
        return True
    elif "help" in p.keys():
        cmd = p["help"]
        pr(cmd, sd[cmd])
        return True
    return False
        
def print_conf(p, opt):
    if "conf" in p.flag:
        print(opt)
        return True
    elif "conf" in p.keys():
        if p.conf in opt.keys():
            print(opt.print_item(p.conf))
        else:
            YELLOW("{} is not set".format(p.conf))
        if p.conf == "style":
            YELLOW("possible colors:       b g r c m y k w")
            YELLOW("possible markers:      . , o v ^ < > 1 2 3 4 s p * h H + x D d | _")
            YELLOW("possible linestyles:   - -- -. :")
        if p.conf == "legend_loc":
            YELLOW("  ".join(sorted({"best": 0, "upper_right": 1, "upper_left": 2, "lower_left": 3, "lower_right": 4, "right": 5, "center_left": 6, "center_right": 7, "lower_center": 8, "upper_center": 9, "center": 10}.keys())))
        return True
    return False
