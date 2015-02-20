#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# 
# Author:  Mario S. Könz <mskoenz@gmx.net>
# Date:    26.01.2015 15:28:42 CET
# File:    import_pyplot.py

import matplotlib
matplotlib.use("agg") #only save / no show / must happen before pyplot / "pdf" also possible
from matplotlib import pyplot
from matplotlib.pyplot import rc
from matplotlib.font_manager import FontProperties
background_color = "#DDDDDD"
grid_color = "white"
rc("axes", facecolor = background_color)
rc("axes", edgecolor = grid_color)
rc("axes", linewidth = 1.2)
rc("axes", grid = True )
rc("axes", axisbelow = True)
rc("grid",color = grid_color)
rc("grid",linestyle="-" )
rc("grid",linewidth=0.7 )
rc("xtick.major",size =0 )
rc("xtick.minor",size =0 )
rc("ytick.major",size =0 )
rc("ytick.minor",size =0 )

def usetex():
    rc("text", usetex=True)
    rc("font",**{"family":"sans-serif", "sans-serif":["Gill Sans MT"]})
    rc("mathtext", fontset="stixsans")

#~ rc("text.latex", preamble=r"\usepackage{cmbright}")

import numpy as np
