#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 
# Author:  Mario S. Könz <mskoenz@gmx.net>
# Date:    22.01.2015 16:20:40 CET
# File:    debug.py

import traceback

from .color import *

#------------------- debug -------------------
def DEBUG_VAR(expr):
    var = str(traceback.extract_stack()[-2][3][10:-1])
    print("  {red}DEBUG_VAR: {redb}{}{red} = {}{none}".format(var, expr, **color))
    
def DEBUG_MSG(msg):
    print("  {red}DEBUG_MSG: {redb}{}{none}".format(msg, **color))
    
#------------------- error / warning ------------------- 
def ERROR(text):
    """
    Raises an exception and outputs text in red color.
    """
    raise Exception("{redb}error: {red}{}{none}".format(text, **color))

def WARNING(text):
    """
    Just prints the text in yellow as a warning.
    """
    print("{yellowb}warning: {yellow}{}{none}".format(text, **color))

def ASSERT(cond, text = ""):
    """
    Will output the text in red color before calling pythons assert if the condition is not True.
    """
    if not cond:
        print("{redb}assert failed: {red}{}{none}".format(text, **color))
        assert(cond)
