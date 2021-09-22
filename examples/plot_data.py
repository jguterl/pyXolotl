#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 17:11:20 2021

@author: guterlj
"""

from Xolotl import *
X = pyXolotl() 
X.load_data('/home/guterlj/simulations/XOLOTL/He_loading/baseload_75eV_profile_irise_8')
X.plot_profiles()
X.plot_retention()