#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 17:11:20 2021

@author: guterlj
"""

from Xolotl import *
X = pyXolotl() 
X.load_data('/global/u2/j/jguterl/simulations/Xolotl/He_loading/800K/runlong2_1')
ax_p=X.plot_profiles()
X.plot_retention()

path='/project/projectdirs/atom/users/a7l/ips-wrappers/ips-iterative-xolotlFT/cases/PISCES_final_simulations/PISCES_He_75eV_Mar2019/restart_t99/work/workers__xolotlWorker_3/'

Y = pyXolotl() 
Y.load_data(path)
ax_p=Y.plot_profiles()
Y.plot_retention()
