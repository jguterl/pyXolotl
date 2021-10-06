#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 13:40:23 2021

@author: jguterl
"""
from Xolotl import *
if '__file__' in dir():
    pathdir = os.path.dirname(os.path.abspath(__file__))
else:
    pathdir = os.getcwd()
    
for ncore in [8]:
    X = pyXolotl() 
    X.verbose= True
    
    X.load_paramfile(pathdir+'param.txt')
    X.set_basefolder('/global/homes/j/jguterl/xolotl_test/')
    X.set_casename('test_{}'.format(ncore))
    
    #X.load_tridyn_file(pathdir+'/templates/tridyn_He.txt')
    #X.input_tridyn['He']['fraction'] = 0.5
    #t = np.linspace(0,0.2,10000)
    #tau=2e-4
    #felm = 1e-3
    #Gamma0=1e23/1e18
    #Gamma_max = 1e24/1e18
    #tstart =1e-3
    X.input_params['petscArgs']['ts_max_steps'] = 20
    X.input_params['gridType'] = 'nonuniform'
    X.input_params['gridParam'] = [256,50000]
    X.input_params['voidPortion'] = 0
    X.input_params['fluxDepthProfileFilePath'] = ''
    #flux = ELM_particle_flux(t, tau, felm, Gamma0, Gamma_max,tstart)
    X.set_particle_flux(1e4)
    print(X.input_params)
    N = int(max(1,int(ncore/16)))
    #ncore = 16
    X.setup_slurm(command_slurm = ['module load /global/homes/j/jguterl/xolotl_cori.mod','time mpiexec -n {} xolotl {}'.format(ncore,X.param_filename)])

    
    X.sbatch(qos='debug',constraint='haswell',n=ncore,t='00-00:20:00',N=N,log_dir=X.get_directory(),  D=X.get_directory(),script_dir=X.get_directory(),script_name='job_xolotl.batch')
