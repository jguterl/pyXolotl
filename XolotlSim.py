#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 00:25:36 2021

@author: guterlj
"""
from XolotlInput import *
class XolotlSim(XolotlInput, SimManagerUtils):
    def __init__(self, parent, modif_params:dict={}, list_commands= [], **kwargs):
        self.name = 'unknown'
        [setattr(self,k,v) for k,v in parent.__dict__.items()]
        self.update_params(modif_params)
        self.setup_ok = False
        self.runner_ok = False
        self.list_commands = list_commands
        for k,v in kwargs:
            if hasattr(self,k):
                setattr(self,k,v)
                
                
    def check_xolotl_exec(self):
            if shutil.which(self.xolotl_exec) is None:
                raise ValueError('The xolotl executable {} was not found... use set_xolotl_exec to set it.')
                
    
    def setup(self, overwrite=False, **kwargs):
        self.check_input_params()
        self.create_directory(self.directory,overwrite)
        for v in self.input_files.values():
            if v is not None:
                self.copy_files(v,self.directory)
        self.write_input_params(os.path.join(self.directory,self.param_filename))
        self.set_command()
        self.setup_ok = True
        
    def set_command(self):
        if self.list_commands == []:
            self.check_xolotl_exec()
            self.command = [self.xolotl_exec, self.param_filename]
        else:
            self.command = self.list_commands
    
    def set_runner(self,runner='process', **kwargs):
        if self.setup_ok is False:
            raise ValueError('runner cannot be set before running setup')
        if runner == 'process':
            self.runner = SimProcRunner(self.command, self.directory, **kwargs)
        elif runner == 'slurm':
            self.runner = SimSlurmRunner(self.command, self.directory, **kwargs)
        else:
            raise ValueError('runner must be either "process" or "slurm"')
            
        self.runner_ok = True
    
    
    
    