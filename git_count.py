#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 
# Author:  Mario S. Könz <mskoenz@gmx.net>
# Date:    27.01.2015 09:57:05 CET
# File:    git_count.py

# Thx @greschd for the original code

from .parameter import *
from .color import *

def git_count(path):
    if not readable(path + "/.git"):
        ERROR("no git repo found in {}".format(path))
        return None
    
    branches = list(filter(None, popen("git --git-dir {}/.git branch".format(path), silent = True).split("\n")))
    for i in range(len(branches)):
        branches[i] = branches[i].lstrip('* ')
    
    hashes = set()
    for branch in branches:
        tmp_hashes = filter(None, popen("git --git-dir {}/.git rev-list HEAD {}".format(path, branch), silent = True).split('\n'))
    hashes.update(set(tmp_hashes))
    chksum = 0
    for num in hashes:
        chksum += int(num, base=16)
    return len(hashes), chksum % (1<<64)
