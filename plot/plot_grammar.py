#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 
# Author:  Mario S. Könz <mskoenz@gmx.net>
# Date:    23.03.2015 10:56:12 CET
# File:    plot_grammar.py

tokens = {"+": "ADD"
        , "-": "ADD"
        , "*": "MUL"
        , "@": "MMUL"
        , ",": "COM"
        , "/": "MUL"
        , "(": "LPAR"
        , ")": "RPAR"
        }
match_rest = "NUM"
match = "[\w.]+"
rules = {
      "param":    ["sums COM sum", "param COM sums"]
    , "sums":     ["sum"] #avoid index problem with sums COM sums
    , "sum" :     ["sum ADD products", "products"]
    , "products": ["products MUL mmuls", "mmuls"]
    , "mmuls":    ["atomic MMUL mmuls", "atomic"]
    , "atomic":   ["LPAR sums RPAR", "fct", "ADD sums", "MUL sums"]
    , "fct":      ["value LPAR param RPAR", "value LPAR sums RPAR", "value"]
    , "value":    [match_rest]
    }

functions = {
      "sums":     lambda *args: args[0] if len(args) == 1 else list(args)
    , "sum":      lambda *args: args[0] if len(args) == 1 else list(args)
    , "products": lambda *args: args[0] if len(args) == 1 else list(args)
    , "mmuls":    lambda *args: args[0] if len(args) == 1 else list(args)
    , "atomic":   lambda *args: args[0] if len(args) == 1 else list(args)
    , "param":    lambda *args: args[0] if len(args) == 1 else list(args)
    , "fct":      lambda *args: args[0] if len(args) == 1 else list(args)
    , "value":    lambda *args: args[0]
    }
