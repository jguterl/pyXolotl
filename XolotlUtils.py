#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11 08:19:47 2022

@author: jguterl
"""
import numpy as np
def read_simlog(filename:str):
    with open(filename,'r') as f : 
        header  = f.readline().rstrip().lstrip('#').strip().split(' ')

    data = np.loadtxt(filename)
    assert len(header) == data.shape[1]
    return  dict((h,data[:,i]) for i,h  in enumerate(header))
