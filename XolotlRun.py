#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 00:40:50 2021

@author: guterlj
"""
import shutil
from XolotlSim import *
from SimManager2 import SimMonitoring
class XolotlRun(SimMonitoring):
        def __init__(self):
            super(XolotlRun, self).__init__()
            self.xolotl_exec = None
            self.basefolder = None
            self.casename = None
            self.env_list = []
            self.setup_monitoring()
            self.verbose = False
          
              #self.base_folder = 
        def add_env_variable(self,varname,varvalue):
            self.env_list.append((varname, varvalue))
            
        def check_xolotl_exec(self):
            if shutil.which(self.xolotl_exec) is None:
                raise ValueError('The xolotl executable {} was not found... use set_xolotl_exec to set it.')
                
        def set_xolotl_exec(self, exec_path='xolotl'):
         if shutil.which(exec_path) is None:
                print('The xolotl executable {} was not found... Looking for XOLOTL_EXEC'.format(exec_path))
                if os.environ.get('XOLOTL_EXEC') is None:
                    print('XOLOTL_EXEC not defined. Not xolotl executable is currently set')    
         else:
            print('The xolotl executable "{}" is valid'.format(exec_path))
            self.xolotl_exec = exec_path
        
        def set_basefolder(self, basefolder:str):
            self.basefolder = basefolder
            
        def set_casename(self, casename:str):
            self.casename = casename
            
        def set_directory(self):
            assert self.casename is not None
            if self.basefolder is not None:
                self.directory = os.path.join(self.basefolder,self.casename)
            else:
                self.directory = os.path.abspath(self.casename)
            if self.verbose: print('directory:',self.directory)
            
        def get_directory(self):
            if not hasattr(self,'directory') or self.directory is None:
                self.set_directory()
            return self.directory
            
        @staticmethod    
        def get_list_scan(param_scan:dict)->list:
            assert type(param_scan) == dict
            def enumerated_product(*args):
                yield from zip(itertools.product(*(range(len(x)) for x in args)), itertools.product(*args))
            if not param_scan:
                return []
            list_params = [[(k,vv) for vv in v] for k,v in param_scan.items()]
            return [dict((pp[0],pp[1]) for pp in p) for i,(idx, p) in enumerate(enumerated_product(*list_params))]
        
        def setup_slurm(self,command_slurm, **kwargs):
            self.setup(runner='slurm', list_commands = command_slurm, **kwargs)
    
        def setup(self, runner='process',name_suffix='id', **kwargs):
            if runner == 'process':
                self.check_xolotl_exec()
            self.set_directory()
            self.set_tridyn()
            self.list_scan = self.get_list_scan(self.param_scan)
            
            self.create_sim(name_suffix, **kwargs)
            self.set_sim_runner(runner, **kwargs)
            
        def create_sim(self, name_suffix, **kwargs):
            if len(self.list_scan) ==0:
                self.simulations = [XolotlSim(self,**kwargs)]
            else:
                self.simulations = []
                for i,p in enumerate(self.list_scan): 
                    if name_suffix == 'id':
                       suf = i
                    else:
                        suf = "_".join(['{}_{}'.format(k,v) for k,v in p.items()])
                    name = '{}_{}'.format(i,"_".join(['{}_{}'.format(k,v) for k,v in p.items()]))
                    self.simulations.append(XololtSim(self, directory=self.directory+'_{}'.format(suf), name=name, modif_params=p,**kwargs))
            if self.verbose: print('Set up {} simulations'.format(len(self.simulations)))
            [s.setup(**kwargs) for s in self.simulations]
        
        def set_sim_runner(self,runner='process', **kwargs):
            self.runner = runner
            [s.set_runner(runner, env_list = self.env_list, **kwargs) for s in self.simulations]
            

        def start(self, **kwargs):
            assert self.runner == 'process' ,'use sbatch to launch simulations with slurm'
            self.tstart = time.time()
            if all([s.runner_ok for s in self.simulations]):
                [s.runner.start() for s in self.simulations]
            else:
                raise ValueError('runner not ok for simulations {}'.format(s.name))
        def sbatch(self, **kwargs):
            assert self.runner == 'slurm' ,'use start to launch simulations through  shell process'
            self.tstart = time.time()
            if all([s.runner_ok for s in self.simulations]):
                [s.runner.start(**kwargs) for s in self.simulations]
            else:
                raise ValueError('runner not ok for simulations {}'.format(s.name))        
        def stop(self):
            [s.runner.stop() for s in self.simulations]
            
        

            
    