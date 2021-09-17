#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 00:23:26 2021

@author: guterlj
"""
from SimManager2 import *
import re
class XolotlInput():
    def __init__(self, paramdef_file='/fusion/projects/boundary/guterlj/parameters_def.txt'):
       super(XolotlInput, self).__init__()
       self.def_params = self.read_paramdef(paramdef_file)
       print('hello')
       self.input_files = {}
       self.input_params = {}
       self.param_scan = {}
       self.param_filename = 'default.txt'
       self.param_filepath = 'default.txt'
       self.inputpflux = {}
       self.tmp_folder = '.'
    
    def help(self,kw:str=None)->None:
        gen = ((k,v) for k,v in self.def_params.items() if (kw is None or kw in k))
        for k,v in gen:
            print('{} : {}'.format(k,v))
            
    def get_input_params(self,inputdata:dict or str)-> None:
        if type(inputdata==dict):
           self.input_params = inputdata
        else:
            self.input_params = self.read_param_file(inputdata)
    
    @staticmethod
    def _reformat_input_params(inputdata:dict):
        assert type(inputdata) == dict
        L = []
        for k,v in inputdata.items() :
            if k=='filename': continue
            if type(v) == list :
             L.append(k+'='+" ".join(v))
            elif type(v) == str:
                 L.append(k+'='+v)
            elif type(v) == dict:
                L.append(k+'='+" ".join(['-'+kk+" "+vv for kk,vv in v.items()]))
        return L
    
    def write_input_params(self, filename:str, input_params:dict or None=None)->None:
        assert input_params is None or type(input_params) == dict
        if input_params is None:
            input_params = self.input_params
        if self.verbose: print('filename in_write_input_params:',filename)
        self._write_file(filename, self._reformat_input_params(input_params))
            
    @staticmethod
    def _read_file(filename:str)->list:
        try:
            f = open(filename,'r')
            lines = f.readlines()
            f.close()
        except:
            print("Cannot read the file {}".format(filename))
            raise
        return lines
    
    def add_file(self, filename, name=None):
        if name is None:
            i = 1
            while 'file{}'.format(i) in list(self.input_files.keys()):
                i = i + 1
            self.input_files['file{}'.format(i)] = filename
        else:
            self.input_files[name] = filename
            
    def add_param_scan(param, values):
            self.param_scan[param] = values
                    
    def update_params(self, modif_params):
        for k,v in modif_params.items():
            if self.input_params.get(k) is not None:
                self.input_params[p] = v
            elif self.input_files.get(k) is not None:
                self.input_files[p] = v
            else:
                raise ValueError('parameter {} cannot be found in params:{} and files:{}'.format(k,self.input_names,self.input_files))
        
    def _make_log(self):
        info = self.get_platform()
        log = {}
        log['user'] = getpass.getuser()
        log['platform'] = info['plaform']
        log['time'] = self.get_time()
        for k,v in self.input_files.items():
            log[k] = v
        return log
        #for for k,v in self.param_scan.items():
            #log['scan'] = v
        
    @staticmethod
    def write_log(self,filename:str, ext='log')->None:
        log = ['{} : {}'.format(k,v) for k,v in self.input_files.items()]
        self._write_file(log, filename)
         
    @staticmethod   
    def get_time()->str:
        today = date.today()
        now = datetime.now()
        return "{}_{}".format(today.strftime('%d%m%y'),now.strftime("%H%M%S"))
        
    @staticmethod
    def _write_file(filename:str,lines:list, ext='txt')->None:
        try:
            if os.path.splitext(filename)[-1] == '':
                filename = filename + '.' + ext
                
            with open(filename,'w') as f:
                for l in lines:
                    f.write(l+'\n')
        except:
            print("Cannot write the file {}".format(filename))
            raise

    @staticmethod
    def _parse_input_params(lines:list,separator = '=')->dict:
        inputdic = {}
        for l in lines:
            l  = " ".join(l.lstrip().rstrip().split())
            lsplit = l.split(separator,1)
            if len(lsplit)>1 and not l.startswith('#'):
                inputdic[lsplit[0]] =  lsplit[1]
            else:
                inputdic[lsplit[0]] = '' 
        return inputdic
    
    @classinstancemethod
    def read_paramdef(self,filename:str)->dict:
        print('Input Xolotl parameters definition loaded from {}'.format(filename))
        filename = os.path.expanduser(filename)
        lines = self._read_file(filename)
        return self._parse_input_params(lines, ":")
    
    @classinstancemethod
    def read_paramfile(self,filename:str)->dict:
        filename = os.path.expanduser(filename)
        lines = self._read_file(filename)
        self.param_filepath = os.path.abspath(filename)
        self.param_filename = os.path.basename(filename)
        return self._process_input_params(self._parse_input_params(lines))
    
    @classinstancemethod
    def load_paramfile(self,filename:str)->None:
        self.input_params = self.read_paramfile(filename)
    
    @classinstancemethod
    def _process_input_params(self,inputdict:dict)->dict:
        assert type(inputdict) == dict, print(type(inputdict))
        def _parse_arg(arg):
            arg  = " ".join( arg.lstrip().rstrip().split())
            if arg.count(' -')>0:
                args = re.split('-(?!\d)',arg)
                return dict((a.split(" ")[0]," ".join(a.split(" ")[1:])) if len(a.split(" "))>0 else (a.split(" ")[0],[]) for a in args[1:] ) 
 
                    
                    
            else:
                return [a for a in arg.split(" ") if a!='']
        
        return dict((k,_parse_arg(v)) for k,v in inputdict.items())

    def check_input_params(self):
        if not self.input_params:
            raise ValueError('input_params is empty!')
        print(self.input_params)
        for k in self.input_params.keys():
            if k not in list(self.def_params.keys()) and k!='':
                raise ValueError('keyword {} as input parameter is unknown. Known params: {}'.format(k, list(self.def_params.keys())))
                
    def _set_paramdef(self,filename='/fusion/projects/boundary/guterlj/parameters_def.txt'):
        self.def_params = self.read_paramdef(filename)
    @staticmethod    
    def get_platform():
        PF={}
        AllFunctions = inspect.getmembers(platform, inspect.isfunction)
        for (n,f) in AllFunctions:
            if not n.startswith('_') and n!='dist' and n!='linux_distribution':
                try:
                    PF[n]=f()
                except:
                    pass
        return PF
    

        
            
    @classinstancemethod
    def set_flux_file(self,filename=None):
        if filename is None:
            filename = 'influx.txt'        
            self.input_files['fluxfile'] = os.path.join(self.tmp_folder,filename)
            self.input_params['fluxFile'] = os.path.basename(filename)
            
    @classinstancemethod
    def _write_flux_file(self,filename,time,flux):
        assert time.shape == flux.shape
        np.savetxt(filename,np.vstack((time,flux)).T)
        
    @classinstancemethod
    def generate_particle_flux(self,time, func, **kwargs):
        if type(func) == np.ndarray:
            return func
        else:
            return func(time,**kwargs)
    
    @classinstancemethod
    def set_particle_flux(self, flux, t=None, filename=None,**kwargs):
        if t is None:
            assert flux > 0.0
            self.input_params['flux'] = flux
        else:
            if self.input_params.get('flux') is not None:
                self.input_params.pop('flux')
            self.inputpflux['time'] =  t
            self.inputpflux['flux'] =  self.generate_particle_flux(t, flux, **kwargs)
            self.set_flux_file(filename)
            self._write_flux_file(self.input_files['fluxfile'],self.inputpflux['time'],self.inputpflux['flux'])
        
    
    
    

        
        
        
            
    
            
            
            
    