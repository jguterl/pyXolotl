#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 17 09:24:37 2021

@author: guterlj
"""


# import numpy as np
# import matplotlib.pyplot as plt

# t = np.linspace(0,0.2,10000)
# tau=2e-4
# felm = 1e-3
# Gamma0=1e22
# Gamma_max = 1e23
tstart=1e-3
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

def sin_particle_flux(t,omega, Gamma0, Gamma_max,tstart=0):
    assert Gamma_max<Gamma0
    Gamma = Gamma0+Gamma_max*np.sin(omega*(t-tstart))
    Gamma[t<tstart] = 0.0 
    return Gamma

def white_particle_flux(t,omega, Gamma0, Gamma_max,tstart=0):
    raise ValueError('not implemented')
    return Gamma



    
# flux = ELM_particle_flux(t, tau, felm, Gamma0, Gamma_max,tstart)
# fluxsin = sin_particle_flux(t, 1/tau, Gamma0, Gamma_max/20.0,0)
# fig,ax = plt.subplots(1)
# ax.semilogx(t,flux,label='$\Gamma_\text{in}$')
# ax.semilogx(t,fluxsin,label='$\Gamma_\text{in}$')