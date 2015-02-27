#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 
# Author:  Mario S. Könz <mskoenz@gmx.net>
# Date:    06.06.2013 20:49:45 EDT
# File:    parameter.py

import os
import re
import sys
import subprocess

from .color import * 
from .helper import * 

#--------------------------- parameter class -------------------------------------------------------
class parameter_class(namespace):
    """
    An useful class to parse argv. Is derived from dict.
    """
    def __init__(self):
        """
        Initializes the class. Do not used self.res_names_ as keys for the dict. It will raise an error.
        """
        super(parameter_class, self).__init__()
        self.clear()
        
    def clear(self):
        namespace.clear(self)
        # if a key has an "_" at the end it is treated as "hidden" in the sense that it isn't printed
        self.res_names_ = ["arg", "flag", "res_names_"]
        self.print_ = False
        self.warn_ = True
    
    def __str__(self):
        """
        String conversion for printing. If they key "print_" is set to True all keys with an trailing underscore will be printed as well. Good for hiding technical/private keys.
        """
        out = ""
        for key in sorted(namespace.keys(self)):
            if not self.print_:
                if key[-1] == "_":
                    continue
            out += "{greenb}{:<11}{green} {}{none}\n".format(key + ":", self[key], **color)
            
        return out[:-1] # kill last "\n"
    
    def warn(self, text):
        """
        If the key "warn_" is True, the user will be warned if a key is overwritten or a flag set a second time.
        """
        if self.warn_:
            WARNING(text)
    
    def read(self, argv):
        """
        The passed argv is parsed and stored in the right places. Legal notation is:\n 
        - -flag
        - -param value
        - param = value
        - arg
        """
        self.clear()
        pas = False
        
        #----------------------- regex for = notation ----------------------------------------------
        # "p = 1" is the only valid notation, since I cannot distinguish -u "a=1" from -u a=1
        # but -u "a = 1" can be distinguished from -u a = 1
        
        #------------------------ some nice errors -------------------------------------------------
        last = len(argv) - 1
        for w, i_w in zipi(argv):
            if w[0] == "-" and i_w != last and argv[i_w + 1] == "=":
                ERROR("flags cannot be assigned with a equal sign: {} =".format(w))
            if w == "=" and i_w == last:
                ERROR("no assignment after equal sign")
            if w[0] == "-" and len(w) == 1:
                ERROR("single '-', syntax not correct")
                
        
        #------------- start parsing --------------------------
        self.arg = []
        self.flag = []
        
        i = 0
        while i < last:
            i += 1 # first argument isn't needed since it is the prog-name
            w = argv[i]
            w1 = "-" if i >= last else argv[i+1]
            w2 = " " if i >= last - 1 else argv[i+2]
            
            # checking if = sign
            if w1 == "=":
                key, val = w, argv[i + 2]
                if self.has_param(key):
                    self.warn("parameter {0} already set to {1} -> overwrite to {2}".format(key, self[key], val))
                self[key] = to_number(val)
                i += 2
                continue
                
            if w[0] == "-":
                w = w[1:]
                if w1[0] != "-" and w2 != "=": # parameter
                    
                    #---------------- just checking for false input --------------------------------
                    if w in self.param:
                        self.warn("parameter {0} already set to {1} -> overwrite to {2}".format(w, self[w], w1))
                    #------------------ setting the parameter --------------------------------------
                    self[w] = to_number(w1)
                    i += 1
                else: # flag
                    #---------------- just checking for false input --------------------------------
                    if w in self.flag:
                        self.warn("flag {0} was already set".format(w))
                    else:
                        #------------------- setting the flag --------------------------------------
                        self.flag.append(w)
            else:
                if pas:
                    pas = False
                else: # arg
                    #---------------- just checking for false input --------------------------------
                    if w in self.arg:
                        self.warn("arg {0} was already set".format(w))
                    else:
                        #------------------- adding the arg ----------------------------------------
                        self.arg.append(w)
    
    def __setitem__(self, key, val):
        """
        Forwards to the namespace.__setitem__ but makes sure that the res_names_ aren't used
        """
        if key in self.res_names_: # guard reserved names
            ERROR("do not use the following names: {0}".format(self.res_names_))
        else:
            namespace.__setitem__(self, key, val)
    
    @property
    def param(self):
        return [k for k in namespace.keys(self) if k not in self.res_names_]
    
    def keys(self):
        return self.param + self.flag + self.arg
    
    def get(self, key, default = None):
        if key in self.keys() + ["flag", "arg"]:
            return self[key]
        else:
            return default
    
    def get_namespace(self):
        res = namespace(self.__dict__)
        del res.warn_
        del res.print_
        del res.res_names_
        return res
    
parameter = parameter_class()

#--------------------------- parameter action ------------------------------------------------------
def bash_if(flag, action, silent = False):
    """
    If the flag is in the parameter instance of parameter_class, the action will be executed by as a bash command if it is a string and be called otherwise (assumption action == python function with no args)
    """
    if flag in parameter.flag:
        if is_str(action): # normal bash cmd
            bash(action, silent)
        elif is_function(action): # fct call
            if not silent:
                CYAN("called function: ")
            action()
        else:
            ERROR("invalid action input in bash_if")
    return 0

def bash(cmd, silent = False, **kwargs):
    """
    Just calls os.system and outputs the command.
    """
    if not silent:
        CYAN(cmd)
    subprocess.call(cmd, shell = True, **kwargs)

def popen(cmd, silent = False, **kwargs):
    """
    If one needs the output of the bash-command, this function can provide it. Works exactly like bash(cmd) but returns the output as a string.
    """
    if not silent:
        CYAN(cmd)
    return subprocess.check_output(cmd, shell = True, **kwargs).decode("utf-8")[:-1] #shell = True not safe!, [:-1]
