#!/usr/bin/python3
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
        super(namespace, self).__init__()
        self.res_names_ = ["arg", "flag", "res_names_"]
        
        # if a key has an "_" at the end it is treated as "hidden" in the sense that it isn't printed
        self.print_ = False
        self.warn_ = True
    
    def __str__(self):
        """
        String conversion for printing. If they key "print_" is set to True all keys with an trailing underscore will be printed as well. Good for hiding technical/private keys.
        """
        out = ""
        for key in sorted(self.keys()):
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
            w1 = argv[[i+1, i][i == last]]
            # checking if = sign
            if w1 == "=":
                key, val = w, argv[i + 2]
                if self.has_param(key):
                    self.warn("parameter {0} already set to {1} -> overwrite to {2}".format(key, self[key], val))
                self[key] = to_number(val)
                i += 2
                continue
                
            if w[0] == "-":
                if w1[0] != "-": # parameter
                    
                    #---------------- just checking for false input --------------------------------
                    if self.has_param(w[1:]):
                        self.warn("parameter {0} already set to {1} -> overwrite to {2}".format(w[1:], self[w[1:]], w1))
                    #------------------ setting the parameter --------------------------------------
                    self[w[1:]] = to_number(w1)
                    i += 1
                else: # flag
                    #---------------- just checking for false input --------------------------------
                    if self.has_flag(w[1:]):
                        self.warn("flag {0} was already set".format(w[1:]))
                    else:
                        #------------------- setting the flag --------------------------------------
                        self.flag.append(w[1:])
            else:
                if pas:
                    pas = False
                else: # arg
                    #---------------- just checking for false input --------------------------------
                    if self.has_arg(w):
                        self.warn("arg {0} was already set".format(w))
                    else:
                        #------------------- adding the arg ----------------------------------------
                        self.arg.append(w)
                    
    def has_arg(self, arg):
        """
        Checks if arg is in the parameter_class. An arg is an entry without a value, like a filename.
        """
        return arg in self.arg
        
    def has_flag(self, flag):
        """
        Checks if flag is set. A flag does not have a value. It is eighter on (has_flag -> True) or off (has_flag -> False)
        """
        if flag[0] == "-":
            flag = flag[1:]
        return flag in self.flag
    
    def has_param(self, param):
        """
        Checks if the key param is set. A param is a key with a value.
        """
        return param in self.keys()
    
    def has_key(self, key):
        """
        Checks if key is a parameter, flag or arg. It does not the same as the dict.has_key function, since flags and args aren't technically stored as keys.
        """
        return self.has_arg(key) or self.has_flag(key) or self.has_param(key)
    
    def __setitem__(self, key, val):
        """
        Forwards to the namespace.__setitem__ but makes sure that the res_names_ aren't used
        """
        if key in self.res_names_: # guard reserved names
            ERROR("do not use the following names: {0}".format(self.res_names_))
        else:
            namespace.__setitem__(self, key, val)
    
parameter = parameter_class()

#--------------------------- parameter action ------------------------------------------------------
def bash_if(flag, action, silent = False):
    """
    If the flag is in the parameter instance of parameter_class, the action will be executed by as a bash command if it is a string and be called otherwise (assumption action == python function with no args)
    """
    if parameter.has_flag(flag):
        if is_str(action): # normal bash cmd
            bash(action, silent)
        elif is_function(action): # fct call
            if not silent:
                CYAN("called function: ")
            action()
        else:
            ERROR("invalid action input in bash_if")
    return 0

def bash(cmd, silent = False):
    """
    Just calls os.system and outputs the command.
    """
    if not silent:
        CYAN(cmd)
    os.system(cmd)

def popen(cmd, silent = False):
    """
    If one needs the output of the bash-command, this function can provide it. Works exactly like bash(cmd) but returns the output as a string.
    """
    if not silent:
        CYAN(cmd)
    return subprocess.check_output(cmd, shell = True).decode("utf-8") # not safe!
