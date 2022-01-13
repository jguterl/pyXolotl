#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  9 22:13:45 2021

@author: guterlj
"""
from XolotlInput import *
from XolotlRun import *
from XolotlOutput import *
from XolotlUtils import *

class pyXolotl(XolotlInput,XolotlRun, XolotlOutput):
    
    def __init__(self, *args, **kwargs):
        super(pyXolotl,self).__init__(*args, **kwargs)
        if kwargs.get('verbose') is not None:
            self.verbose = kwargs.get('verbose')
