#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 
# Author:  Mario S. Könz <mskoenz@gmx.net>
# Date:    23.03.2015 10:56:23 CET
# File:    parser.py

from .parameter import *

class parser():
    def __init__(self, grammar = None):
        self.core = namespace()
        if grammar:
            self.set_grammar(grammar)
    
    def set_grammar(self, grammar):
        self.core.tokens = grammar.tokens
        self.core.rules = grammar.rules
        self.core.functions = grammar.functions
        self.core.match = grammar.match
        self.core.match_rest = grammar.match_rest


    def escape_regex(self, list_):
        escape = ["-", "\\", "]", "["]
        back = []
        for l in list_:
            if l in escape:
                back.append("\{}".format(l))
            else:
                back.append(l)
        return back
    
    def tokenize(self, expr):
        split = re.findall((self.core.match + "|[{0}]").format("".join(self.escape_regex(self.core.tokens))), expr)
        token = [namespace({"token": self.core.tokens.get(x, self.core.match_rest), "value": x}) for x in split]
        return token

    def matches(self, stack, rule):
        if len(stack) == 0:
            return False
        
        #find last token
        if stack[-1].token in rule.pattern:
            idx = rule.pattern.index(stack[-1].token) #not sure if index is best policy: sums COM sums problem, first sums gets matched
            
            if len(stack) > idx:
                for i in range(1, idx+1):
                    if stack[-1-i].token != rule.pattern[idx-i]:
                        return False
                return rule, idx
                
            
        return False

    def parse(self, istring):
        token = self.tokenize(istring)
        stack = []
        
        rule = []
        for k, val in self.core.rules.items():
            for v in val:
                rule.append(namespace({"pattern": v.split(" "), "token": k}))

        token.append(namespace({"token": None, "value": None}))
        lookahead = token[0]

        while True:
            #~ MAGENTAB(" ".join([x.token for x in stack]))
            
            #------------------- find candidates -------------------
            candidates = []
            for r in rule:
                m = self.matches(stack, r)
                if m:
                    candidates.append(m)
            
            #------------------- reduce -------------------
            if len(candidates) != 0:
                #------------------- select correct rule -------------------
                if len(candidates) > 1:
                    c2 = []
                    for r, idx in candidates:
                        if idx + 1 != len(r.pattern): # prefer rules that match lookahead
                            #~ GREEN("compare lookahead:", lookahead.token, r.pattern[idx + 1])
                            if lookahead.token == r.pattern[idx + 1]:
                                #~ YELLOW("matched lookahead:", r.pattern)
                                c2.append([r, idx])
                    #~ CYAN("lenght of lookahead matched list:", len(c2))
                    if len(c2) == 0: # if none found use fully matched rules on stack
                        for r, idx in candidates:
                            if idx + 1 == len(r.pattern):
                                c2.append([r, idx])
                    #~ RED("potential candidates: ", [x[0].pattern for x in candidates])
                    #~ RED("potential c2 candidates: ", [x[0].pattern for x in c2])
                    if c2:
                        candidates = [sorted(c2, key = lambda x: len(x[0].pattern))[-1]] #select longest rule
                        #~ REDB("chosen candidate: ", [x[0].pattern for x in candidates])
                    else:
                        candidates = []
                
                #------------------- apply rule if possible -------------------
                if len(candidates) == 1: #not else since len can change above
                    r, idx = candidates[0]
                    if idx + 1 == len(r.pattern):
                        args = [x.value for x in stack[-len(r.pattern):]]
                        val = self.core.functions[r.token](*args)
                        del stack[-len(r.pattern):]
                        stack.append(namespace({"token": r.token, "value": val}))
                        continue
            
            #------------------- accept -------------------
            if len(token) == 1 and len(stack) == 1:
                #~ GREEN("successful parse")
                break
            #------------------- error -------------------
            if len(token) == 1 and len(stack) != 1:
                ERROR("parse failed, this remained on the stack: {}".format(" ".join([x.token for x in stack])))
                break
            
            #------------------- shift -------------------
            stack.append(token[0])
            del token[0]
            lookahead = token[0]
            
        return stack[0].value
