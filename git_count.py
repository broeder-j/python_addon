#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 
# Author:  Mario S. Könz <mskoenz@gmx.net>
# Date:    27.01.2015 09:57:05 CET
# File:    git_count.py

# Thx @greschd for the original code

from .parameter import *
from .color import *

def git_count(cwd):
    try:
        branches = list(filter(None, popen('git branch', silent = True, cwd = cwd).split('\n')))
    except subprocess.CalledProcessError:
        return None

    for i in range(len(branches)):
        branches[i] = branches[i].lstrip('* ')

    hashes = []
    chksum = 0

    if len(branches) > 0:
        hashes = list(filter(None, popen('git rev-list --all --pretty=format:%T', silent = True).split('\n')[1::2]))
        
        for num in hashes:
            chksum += int(num, base=16)

    return len(hashes), chksum

