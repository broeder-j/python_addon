#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 
# Author:  Mario S. Könz <mskoenz@gmx.net>
# Date:    23.03.2015 21:54:17 CET
# File:    matrix_generator.py

import numpy as np
from ..helper import *

def triangular_convolution(values, N):
    res = []
    weight = [min(i+1, 2*N+1-i) for i in range(2*N+1)] #triangular shape [1,2,3,2,1]
    weight = weight[N:]+weight[:N] #shift it [3,2,1,1,2]
    for v, v_i in zipi(values):
        lower = max(0, v_i - N)
        upper = min(len(values) - 1, v_i + N)
        n = sum(weight[v_i-i] for i in range(lower, upper + 1))
        s = sum(values[i]*weight[v_i-i] for i in range(lower, upper+1))
        s /= n
        res.append(s)
        
    return res

matrix = namespace()
matrix.acc = lambda *args: np.add.accumulate
matrix.trig_conv = lambda *args: lambda x: triangular_convolution(x, args[0])
    
