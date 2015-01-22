#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 
# Author:  Mario S. Könz <mskoenz@gmx.net>
# Date:    22.01.2015 15:15:46 CET
# File:    html_parser.py

#!/apps/monch/python/3.4.1/gcc/4.8.1/bin/python
# -*- coding: utf-8 -*-
# 
# Author:  Mario S. Könz <mskoenz@gmx.net>
# Date:    21.01.2015 16:46:14 CET
# File:    imp.py

from html.parser import HTMLParser
from collections import OrderedDict
import re

from ..helper import *

class MyHTMLParser(HTMLParser):
    def __init__(self):
        super(MyHTMLParser, self).__init__()
        self.dom = OrderedDict()
        self.curr = [self.dom]
        
    def handle_starttag(self, tag, attrs):
        if tag in list(self.curr[-1].keys()):
            self.curr[-1][tag].append(OrderedDict())
        else:
            self.curr[-1][tag] = [OrderedDict()]
            
        self.curr.append(self.curr[-1][tag][-1])
        
    def handle_endtag(self, tag):
        self.curr.pop()
    def handle_data(self, data):
        if data == " ":
            return
        self.curr[-1]["__data"] = data

def parse_plot_html(name):
    parser = MyHTMLParser()
    data = open(name, "r").read()
    data = re.sub('\\s+(?=(?:[^"]*"[^"]*")*[^"]*$)', " ", data)
    parser.feed(data)
    
    dom = parser.dom
    
    param = [l["__data"] for l in dom["plot"][0]["param"][0]["l"]]
    head = dom["plot"][0]["head"][0]["__data"]
    data = [l["__data"] for l in dom["plot"][0]["data"][0]["l"]]
    
    param = [split_clean(x) for x in param]
    param = dict([(a, to_number(b)) for a, b in param])
        
    head = split_clean(head)
    data = [[to_number(x) for x in split_clean(l)] for l in data]
    
    return namespace({"head": head, "data": data, "param": param})
