#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 
# Author:  Mario S. Könz <mskoenz@gmx.net>
# Date:    12.06.2013 10:31:13 EDT
# File:    helper.py

import os
import re # for split_clean
import collections # for flatten
from functools import partial # for split_clean

from .debug import * 

#---------------------------- type checks ----------------------------------------------------------
def is_list(obj):
    """
    Checks if the obj is a list.
    """
    return isinstance(obj, list)
    
def is_dict(obj):
    """
    Checks if the obj is a dict.
    """
    return isinstance(obj, dict)
    
def is_int(obj):
    """
    Checks if the obj is an int.
    """
    return isinstance(obj, int)

def is_float(obj):
    """
    Checks if the obj is a float.
    """
    return isinstance(obj, float)

def is_number(obj):
    """
    Checks if the obj is an int or a float.
    """
    return is_int(obj) or is_float(obj)

def is_str(obj):
    """
    Checks if the obj is a string.
    """
    return isinstance(obj, str)

def is_bytes(obj):
    """
    Checks if the obj is a bytes array.
    """
    return isinstance(obj, bytes)

import types
def is_function(obj):
    """
    Checks if the obj is a python function.
    """
    return isinstance(obj, types.FunctionType)

#------------------------ file helper / os forwards ------------------------------------------------
def readable(file_):
    """
    Checks if a file_ is readable. Uses os.
    """
    return os.access(file_, os.R_OK)

def exists(file_):
    """
    Checks if a file_ exists. Uses os.
    """
    return os.path.isfile(file_)

def abspath(file_):
    return os.path.dirname(os.path.abspath(file_))

def cwd():
    return os.getcwd()

#--------------------------- zip with index --------------------------------------------------------
def zipi(l):
    """
    Shorthand for zip(list, range(len(list))), if one needs the index and the content of a list.
    """
    return zip(l, range(len(l)))

#----------------------------- converter -----------------------------------------------------------
def to_number(string, strip_quotes = True):
    """
    Tries to convert the input string into an int, if that doesn't work into a float and if that also fails, returns the string again.
    """
    if is_list(string):
        return list(map(lambda x: to_number(x, strip_quotes), string))
    
    elif is_dict(string):
        return dict([(k, to_number(v, strip_quotes)) for k, v in string.items()])
        
    try:
        res = int(string)
        return res
    except:
        pass
    try:
        res = float(string)
        return res
    except:
        pass
    
    test = string.strip()
    if test[0] == "[" and test[-1] == "]":
        #~ l = test[1:-1].split(",") #too easy, splits [[a, b], [c, d]] -> [[a<> b]<> [c<> d]]
        l = test[1:-1].split(",")
        l = re.split(",(?=(?:[^\\[\\]]*(?:\\[[^\\[\\]]*\\]))*[^\\[\\]]*$)", test[1:-1]) # splits only , outside of [] bc of recursive lists [[a, b], [c, d]]
        
        return to_number(l, strip_quotes)
    
    if strip_quotes == True:
        return re.sub('^[\s]*(["\'])([\s\S]*)(\\1)$', "\\2", string)
    return string

#------------------- make list if not already a list -------------------
def make_list(obj):
    if is_list(obj):
        return obj
    else:
        return [obj]

#------------------------ clean split for strings --------------------------------------------------
def split_clean(string, strip_quotes = False):
    if is_list(string):
        return list(map(partial(split_clean, strip_quotes = strip_quotes), string))
    
    string = re.sub("^[\\s]+|[\\s]+$", "", string) # remove front and back whitespace (strip would also work)
    not_in_quotes = '(?=(?:[^"\']*(?:"[^"]*"|\'[^\']*\'))*[^"\']*$)'
    e = '\\s+'+not_in_quotes # split on whitespace sections but not in "" or ''
    
    res = re.split(e, string)
    if strip_quotes:
        for i in range(len(res)):
            res[i] = re.sub('^(["\'])([\s\S]*)(\\1)$', "\\2", res[i]) #strips "" or '' if found at ^ and $
        return res
    else:
        return res

#------------------ namespace (satisfies mapping interface) :D -------------------------------------
# Namespaces are one honking great idea -- let's do more of those!
class namespace:
    def __init__(self, dict_ = None):
        if dict_ != None:
            self.update(dict_)
    def update(self, dict_):
        self.__dict__.update(dict_)
    def __getitem__(self, key):
        return self.__dict__[key]
    def __setitem__(self, key, val):
        self.__dict__[key] = val
    def __delitem__(self, key):
        del self.__dict__[key]
    def get(self, key, default = None):
        if key in self.keys():
            return self[key]
        else:
            return default
    def keys(self):
        return self.__dict__.keys()
    def items(self):
        return self.__dict__.items()
    
    def print_item(self, key):
        sv = str(self.__dict__[key])
        if len(sv) > 60: # shorten too long objects to size 60
            sv = sv[:30] + "{redb} ...{}... {green}".format(len(sv) - 60, **color) + sv[-30:]
        return "{greenb}{:<10}{none} = {green}{}{none}".format(key, sv, **color)
        
    def __str__(self):
        res = ""
        for k, v in sorted(self.__dict__.items()):
            res += self.print_item(k) + "\n"
        return res[:-1] # remove last "\n"

#------------------ read state file generated by progress.hpp --------------------------------------
def read_status(path_dir):
    m = {};
    if readable(path_dir + "/status.txt"):
        while True:
            f = open(path_dir + "/status.txt", "r")
            ll = f.readlines()
            f.close()
            try:
                data = [l.split() for l in ll]
                for d in data:
                    m[d[0]] = to_number(d[1])
                assert(set(m.keys()) == set(["p", "eta", "time", "launch"]))
                return m
            except:
                pass
    else:
        return "inexistent"

#------------------ style time from int to 00:00:00" and back --------------------------------------
def time_int(t_str):
    t_str = t_str.split(":")
    return 3600 * int(t_str[0]) + 60 * int(t_str[1]) + int(t_str[2])
    
def time_str(t_int):
    return "{:02d}:{:02d}:{:02d}".format(int(t_int / 3600), int(t_int / 60) % 60, int(t_int) % 60)

def dyn_time_str(t_int):
    y, d, h, m, s = [int(t_int / (60 * 60 * 24 * 365))
                   , int(t_int / (60 * 60 * 24)) % 365
                   , int(t_int / (60 * 60)) % 24
                   , int(t_int / (60)) % 60
                   , int(t_int) % 60]
    if d == 0:
        return "{:02d}:{:02d}:{:02d}".format(h, m, s)
    else:
        res = ""
        if y > 0:
            res += "{}y ".format(y)
        res += "{}d {:02d}h".format(d, h)
        return res

#----------------------------- dict support ----------------------------------------------------------
def merge_dict(*args):
    l = []
    for a in args:
        l += list(a.items())
    return dict(l)

def dict_select(dict_, keys):
    return dict([(k, v) for k, v in dict_.items() if k in keys])
    
#--------------------------- depth of a list -------------------------------------------------------
def depth(l):
    """
    Retruns the maximal depth of a nested list system. Is recursive and searches the whole "tree", might be slow.
    """
    if is_list(l):
        subdepth = [depth(item) for item in l]
        if subdepth == []:
            return 1
        else:
            return 1 + max(subdepth)
    else:
        return 0

#------------------- flatten a complicated list construction ---------------------------------------
def flatten(l):
    if isinstance(l, collections.Iterable):
        return [a for i in l for a in flatten(i)]
    else:
        return [l]

#------------------- return transpose of a list -------------------
def transpose(lis):
    return [list(x) for x in zip(*lis)]


#------------- computed len(flatten(list)) but without storing the list ----------------------------
def nested_len(l):
    if isinstance(l, collections.Iterable):
        return sum([nested_len(x) for x in l])
    else:
        return 1

#------------------------------ ranges -------------------------------------------------------------
def drange(start, end, step):
    """
    Returns a range of floating point numbers.
    """
    return [start + step * i for i in range(int(end / step))]

#---------------------------- string helper --------------------------------------------------------
def padding(s, modulo, char = " "):
    """
    Padding a string to a multiple length of modulo.
    """
    if is_bytes(s):
        char = b" "
        
    if len(s) % modulo != 0:
        return s.ljust(len(s) + modulo - len(s) % modulo, char)
    else:
        return s
