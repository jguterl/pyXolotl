#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 12 08:01:31 2022

@author: jguterl
"""
import itertools
import numpy as np
import os
from XolotlInput import check_input_params
from Xolotl import pyXolotl
import slurm_support  
from SimManager2 import SimManagerUtils
import subprocess
def chmodx_directory(directory):
    command = 'chmod -R u+x {}'.format(directory)
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    print(output,error)
def tot_sim(params):
    return np.prod([np.array(len(v)) for v in params.values()])

def gnu_parallel_command(runner_exec_file,runner_input):
    commands = ['module load parallel']
    commands += ['parallel {} {{}} < {}'.format(runner_exec_file,runner_input)]
    return commands

def xolotl_runner_command(xolotl_exec, header_xolotl, paramfilename, N = 1, n = 32):
    commands = ['{}\n'.format(h) for h in header_xolotl]
    commands += ['cd $1']
    commands += ['time srun -N {} -n {} {} {}'.format(N,n,xolotl_exec, paramfilename)]
    return commands
    
def write_runner_input(filename,parallel_runs):
    with open(filename,'w') as f:
        for v in parallel_runs['sims'].values():
            f.write(v['directory']+'\n')
            
def write_runner_script(filename,commands):
    with open(filename,'w') as f:
            f.write('\n'.join(commands))
            
def dump_log(filename,dic):
    np.save(filename,dic)
    
        
class XolotlParaLauncher():
    def __init__(self,directory):
        self.xolotl_runner = {}
        self.parallel_runs = {}
        self.xolotl_runner_inputfile = 'input_runner.txt'
        self.directory = directory
        SimManagerUtils.create_directory(self.directory)
    def setup_parallel_runs(self,params, basefolder, paramfile, tridynfile):
        self.parallel_runs = self._setup_parallel_runs(params, basefolder, paramfile, tridynfile)
    
    @staticmethod
    def _setup_parallel_runs(params, basefolder, paramfile, tridynfile):
        
        check_input_params(params)
        
        dic={}
        dic['paramfile'] = os.path.abspath(paramfile)
        dic['basefolder'] = os.path.abspath(basefolder)
        dic['trydinfile'] = os.path.abspath(tridynfile)
        dic['params'] = params
        dic['nsim'] = np.prod([np.array(len(v)) for v in params.values()])
        
        sims = {}
        sim_param_array = np.zeros((dic['nsim'],len([k for k in params.keys()])))  
            
        for i,val in enumerate(itertools.product(*(v for v in params.values()))):
            print('Setup simulation # {} with :'.format(i),';'.join(['{}={}'.format(k,val) for k,val in zip(params.keys(),val)]))
            sim = {}
            sim['params'] = dict((k,v) for k,v in  zip(params.keys(),val))
            sim['directory'] = '{}{}'.format(dic['basefolder'],i)
            sim_param_array[i,:] =  np.array([v for v in val])
            
            X = pyXolotl()
            X.verbose= True
            X.load_paramfile(dic['paramfile']) 
            X.load_tridyn_file(dic['trydinfile'] )
            X.set_directory(sim['directory'])
            for k,v in  zip(params.keys(),val): 
                X.set_input_param(k,v)
            X.setup_slurm_parallel()
            
            sim['simulation'] = X
            sims[i] = sim
        dic['sims_param_array'] = sim_param_array
        dic['sims'] = sims
        return dic
        
    def setup_xolotl_runner(self,xolotl_exec, header_xolotl, paramfilename, N = 1, n = 32, filename=None):
        if filename is None:
            self.xolotl_runner_script_filename = os.path.join(self.directory,'runner_xolotl.sh') 
        commands = xolotl_runner_command(xolotl_exec, header_xolotl, paramfilename, N, n)
        write_runner_script(self.xolotl_runner_script_filename,commands)
    
    def setup_slurm_parallel_runner(self,slurm_options):
        self.write_runner_input()
        commands = gnu_parallel_command(self.xolotl_runner_script_filename,self.xolotl_runner_inputfile_path)
        if slurm_options.get('D') is None:
            slurm_options['D'] = self.directory
        self.slurm_runner = slurm_support.SlurmSbatch(commands, **slurm_options, script_dir = self.directory, script_name = 'job_xolotl_gnu_parallel.sbatch', pyslurm=True)
        self.slurm_runner.write_job_file()
        
    def write_runner_input(self):
        self.xolotl_runner_inputfile_path = os.path.join(self.directory, self.xolotl_runner_inputfile)
        write_runner_input(self.xolotl_runner_inputfile_path,self.parallel_runs)
        
    def sbatch(self):
        chmodx_directory(self.directory)
        self.slurm_runner.submit_job()
        #job_id = 0
        job_id = self.slurm_runner.job_id
        self.saveas(os.path.join(self.directory,'{}_log.npy'.format(job_id)),self.parallel_runs)
        self.saveas(os.path.join(self.directory,"launcher_{}.npy".format(job_id)),self)
        
    def saveas(self,filename, obj):
        filename = os.path.join(filename)
        np.save(filename, obj)
        
        
         
   
         

            
    
            
           
        
        
    