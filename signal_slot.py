#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 
# Author:  Mario S. Könz <mskoenz@gmx.net>
# Date:    28.01.2015 00:42:44 CET
# File:    signal_slot.py

import copy
from functools import wraps

signals = {}
slots = {}

def create_slot(cls, name, fct):
    @wraps(fct)
    def wrap(self, *args, **kwargs):
        #~ print("Slot {} activated: ".format(name), *args)
        fct(self, *args, **kwargs)
    return wrap
    
class signal_class():
    def __init__(self, instance, signame, fctname, fct):
        self.slotl = []
        self.signame = signame
        if fctname == signame:
            self.inst = instance
            self.fct = fct
        else:
            self.inst = None
            self.fct = None
        
    def connect(self, slot):
        self.slotl.append(slot)
    
    def disconnect(self, slot):
        if slot in self.slotl:
            self.slotl.remove(slot)
    
    def emit(self, *argv, **kwargs):
        #~ print("Signal {} activated {}: ".format(self.signame, len(self.slotl)), *argv)
        for slot in self.slotl:
            slot(*argv, **kwargs)
    
    def __call__(self, *argv, **kwargs):
        if self.inst:
            self.fct(self.inst, *argv, **kwargs)
        #~ elif self.fct:
            #~ self.fct(*argv, **kwargs)
            #~ self.emit(*argv, **kwargs)
        else:
            ERROR("signal_class should not be called")
__all__ = ["signal_slot", "signal", "slot"]

def signal(name = None, unbound = False):
    #~ if unbound:
        #~ return lambda x: signal_class(None, name, x.__name__, x)
    def inner(f):
        @wraps(f)
        def wrap_f(self, *args, **kwargs):
            res = f(self, *args, **kwargs)
            getattr(self, name).emit(*args, **kwargs)
            return res
        
        wrap_f.signal = name
        signals[name] = [f.__name__, wrap_f]
        if hasattr(f, "slot"): # forward wrap_f to slot if there (since slot triggers signal if same method)
            slots[f.slot] = [wrap_f.__name__, wrap_f] # new global method
        return wrap_f
    
    if isinstance(name, str):
        return inner
    else: # no name was given, name is the function
        f = name
        name = f.__name__
        return inner(f)
    

def slot(name = None, unbound = False):
    #~ if unbound:
        #~ return lambda x: create_slot(None, name, x)
    
    def inner(f):
        f.slot = name
        slots[name] = [f.__name__, f]
        return f
    
    if isinstance(name, str):
        return inner
    else: # no name was given, name is the function
        f = name
        name = f.__name__
        return inner(f)

    
    
def signal_slot(cls):
    #------------------- copy from global, this works since signal_slot parses one class after another -------------------
    cls.signals = copy.deepcopy(signals)
    cls.slots = copy.deepcopy(slots)
    signals.clear()
    slots.clear()
    
    
    for key, val in cls.slots.items():
        setattr(cls, key, create_slot(cls, val[0], val[1]))
        if key in cls.signals.keys():
            cls.signals[key] = [cls.signals[key][0], getattr(cls, key)]
            
        
    #------------------- save current class constructor  -------------------
    old_init = cls.__init__
    
    @wraps(cls.__init__)
    def init(self, *args, **kwargs):
        for name, val in cls.signals.items():
            setattr(self, name, signal_class(self, name, val[0], val[1]))
        old_init(self, *args, **kwargs)
    
    #------------------- set new ctor-------------------
    cls.__init__ = init
    return cls
