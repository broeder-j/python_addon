#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 
# Author:  Mario S. Könz <mskoenz@gmx.net>
# Date:    23.03.2015 21:39:03 CET
# File:    error_propagation.py

from . import plot_grammar as grammar
from . import matrix_generator as gen
from ..parser import *

import sympy as sy
import numpy as np

def math_parser(expr):
    p = parser(grammar)
    
    res = p.parse(expr)
    
    def join_list(list_):
        if is_list(list_):
            res = ""
            
            #------------------- handle @ -------------------
            if len(list_) > 2 and list_[1] == '@':
                if is_list(list_[0]):
                    res += "' + MPM('" + list_[0][0] + "', FCT('"
                    res += join_list(list_[2:])
                    res += "'), "+join_list(list_[0][2])+") + '"
                else:
                    res += "' + MPM('" + list_[0] + "', FCT('"
                    res += join_list(list_[2:])
                    res += "')) + '"
            else:
                for l in list_:
                    res += join_list(l)
        else:
            res = list_
        
        return res
    
    res = "FCT('"+join_list(res)+"')"

    return res
    
def identify_symbols(string):
    #------------------- get symbols -------------------
    sym = list(set(re.findall("[A-Za-z_][\d\w]*(?=[ ]*(?:[+\-*/\)]|$))", string)))
    
    #------------------- create symbols -------------------
    ns = namespace()
    for v in sym:
        ns[v] = sy.symbols(v, real=True)
        ns[v + "_err"] = sy.symbols(v + "_err", positive=True)
    
    expr = eval(string, merge_dict(sy.__dict__, globals()), ns)
    
    #------------------- get derivations for all symbols -------------------
    diff = []
    for s in sym:
        diff.append(sy.diff(expr, ns[s]))
    
    #------------------- calc gaussian error propagation -------------------
    res = 0
    for d, s in zip(diff, sym):
        res += d**2 * ns[s + "_err"]**2
    
    val = expr
    err = sy.sqrt(res)
    
    return ns, val, err

def calc_expr(label, data0, expr):
    temp_data = {}
    data = {}
    for l, d in zip(label, data0):
        data[l] = d
    
    N = len(data[list(data.keys())[0]])
    
    #------------------- add 0-colums to all labels that don't have an error -------------------
    zero = [0 for n in range(N)]
    add = []
    for l in data.keys():
        if "_err" not in l:
            if l + "_err" not in data.keys():
                add.append((l + "_err", zero))
    
    for k, v in add:
        data[k] = v
    
    
    def MPM(mat_name, symbol, *args):
        M = gen.matrix[mat_name](*args)
        
        def transform(lbl, error = False):
            d_all = merge_dict(data, temp_data)[lbl]
            if error:
                return np.sqrt(M(np.square(d_all)))
            else:
                return M(d_all)
        
        lbl = "__temp_{}".format(len(temp_data.keys()))
        temp_data[lbl] = transform(symbol)
        temp_data[lbl+"_err"] = transform(symbol + "_err", error = True)
        return lbl
    
    def FCT(instring):
        var, val, err = identify_symbols(instring)
        
        def transform(var, expr0):
            res = []
            for i in range(N):
                val = expr0
                for v in var.keys():
                    d = merge_dict(data, temp_data).get(v, None)
                    if d != None:
                        d = d[i]
                    val = val.subs(var[v], d)
                    
                res.append(float(val.evalf()))
            return res
        
        lbl = "__temp_{}".format(len(temp_data.keys()))
        temp_data[lbl] = transform(var, val)
        temp_data[lbl+"_err"] = transform(var, err)
        return lbl
    
    
    target = math_parser(expr)
    target = eval(target, globals(), locals())
    val = temp_data[target]
    err = temp_data[target+"_err"]
    
    #------------------- avoid error plotting if zero -------------------
    all_zero = True
    for e in err:
        if e != 0:
            all_zero = False
            break
    
    if all_zero:
        err = None
    
    return val, err
