#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 
# Author:  Mario S. Könz <mskoenz@gmx.net>
# Date:    10.02.2015 10:40:02 CET
# File:    xml_helper.py

def prettify(node, indent = "    ", level = 0):
    node.tail = "\n" + indent * level
    if len(node) != 0:
        node.text = "\n" + indent * (level + 1)
        for c in node:
            prettify(c, indent, level + 1)
            if c == node[-1]:
                c.tail = "\n" + indent * level
    else:
        if node.text:
            node.text = node.text.strip()
        node.tail = "\n" + indent * level
