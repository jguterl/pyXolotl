#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  8 15:10:50 2021

@author: guterlj
"""


def ELM_particle_flux(t,tau=0,felm=0, Gamma0=0,Gamma_max=0,tstart =0):
    assert tau>0.0
    assert Gamma0 > 0.0
    assert Gamma_max>0.0
    Gamma = 0*t
    if felm<1e-16: felm=1e-16
    nmax = int(max(1,int(max(t)*felm)))
    if nmax <1: nmax =1
    t[t<1e-16] = 1e-16
    for i in range(0,nmax):
        
        GammaELM = (tau/(t-tstart-float(i)/felm))**2*exp(1-(tau/(t-tstart-float(i)/felm))**2)
        GammaELM[t<tstart+float(i)/felm] = 0
        Gamma = Gamma0 + Gamma_max*GammaELM
    return Gamma            

from Xolotl import *
X = pyXolotl() 
X.verbose= True
X.load_paramfile('/home/guterlj/simulations/XOLOTL/onlyD/param_D.txt')
X.set_basefolder('/home/guterlj/simulations/XOLOTL/onlyDtest')
X.set_casename('supertest4')

X.load_tridyn_file('/home/guterlj/simulations/XOLOTL/onlyD/tridyn_D.dat')
X.input_tridyn['D']['fraction'] = 1
t = np.linspace(0,0.2,10000)
tau=2e-4
felm = 1e-3
Gamma0=1e23/1e18
Gamma_max = 1e24/1e18
tstart =1e-3
X.input_params['petscArgs']['ts_adapt_dt_max'] = tau/10.0
flux = ELM_particle_flux(t, tau, felm, Gamma0, Gamma_max,tstart)
X.set_particle_flux(flux,t)
X.set_xolotl_exec('/home/guterlj/boundary/xolotl-build/install/bin/xolotl')

X.add_env_variable('LD_LIBRARY_PATH', '/home/guterlj/boundary/xolotl_dependencies/kokkos-install/lib64')
X.add_env_variable('LD_LIBRARY_PATH', '/home/guterlj/boundary/xolotl_dependencies/petsc-install/lib')
X.setup()

X.start()
X.monitor()
#params_def = RunXolotl.read_paramdef('/fusion/projects/boundary/guterlj/parameters_def.txt')
#dic2 = RunXolotl._process_inputdic(dic)
X.load_data()