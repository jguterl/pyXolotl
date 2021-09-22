#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 00:23:26 2021

@author: guterlj
"""
from SimManager2 import *
import re
param_def = {'dimensions': ' The number of dimensions for the simulation. Can be 0 (no dimension), 1, 2, 3. Note: 0 dimension cannot be run in parallel.',
 'gridType': ' Grid type to use along X. (default = uniform; available uniform,nonuniform,geometric,cheby,read.',
 'gridParam': ' At most six parameters for the grid. Alternatives: uniform -> nX hX; nonuniform -> nX; geometric -> nX ratio; cheby -> nX width. The four additional parameters are for a uniform grid in Y and Z -> nY hY nZ hZ.',
 'boundary': ' This option allows the user to choose the boundary conditions. The first one correspond to the left side (surface) and second one to the right (bulk), then two for Y and two for Z. 0 means mirror or periodic, 1 means free surface.',
 'xBCType': ' The boundary conditions to use in the X direction, mirror (default) or periodic.',
 'voidPortion': ' The value (in %) of the void portion at the start of the simulation.',
 'netParam': ' This option allows the user to define the boundaries of the network. To do so, simply write the values in order maxHe/Xe maxD maxT maxV maxI.',
 'networkFile': ' The HDF5 file to use for restart.',
 'process': ' List of all the processes to use in the simulation (reaction, diff, advec, modifiedTM, movingSurface, bursting, attenuation, resolution, heterogeneous, sink).',
 'burstingDepth': ' The depth (in nm) after which there is an exponential decrease in the probability of bursting (10.0 nm if nothing is specified).',
 'burstingFactor': ' This option allows the user to set the factor used in computing the likelihood of a bursting event.',
 'material': ' The material options are as follows: {W100, W110, W111, W211, Pulsed, Fuel, Fe, 800H}.',
 'grouping': ' The grouping parameters: the first integer is the size at which the grouping starts (HeV clusters in the PSI case, Xe in the NE case), the second is the first width of the groups (He for PSI, Xe for NE), and the third one in the second width of the groups (V for PSI).',
 'tempHandler': ' Temperature handler to use. (default = constant; available constant,gradient,heat,profile.',
 'tempParam': ' At most two parameters for temperature handler. Alternatives: constant -> temp; gradient -> surfaceTemp bulkTemp; heat -> heatFlux bulkTemp.',
 'tempProfileFilename': ' A temperature profile is given by the specified file, then linear interpolation is used to fit the data. NOTE: no need for tempParam here.',
 'flux': ' The value of the incoming flux in #/nm2/s. If the Fuel case is used it actually corresponds to the fission rate in #/nm3/s.',
 'fluxFile': ' A time profile for the flux is given by the specified file, then linear interpolation is used to fit the data. (NOTE: If a flux profile file is given, a constant helium flux should NOT be given).',
 'fluxDepthProfileFilePath': ' The path to the custom flux profile file; the default is an empty string that will use the default material associated flux handler.',
 'initialV': ' The initial concentration of vacancies in the material (in #/nm3).',
 'sputtering': ' The sputtering yield (in atoms/ion) that will be used.',
 'grain': ' This option allows the user to add GB in the X, Y, or Z directions. To do so, simply write the direction followed by the distance in nm, for instance: X 3.0 Z 2.5 Z 10.0 .',
 'zeta': ' The value of the electronic stopping power in the material (0.73 by default).',
 'density': ' Sets a density in nm-3 for the number of xenon per volume in a bubble for the NE case (default is 10.162795276841 nm-3 as before).',
 'radiusSize': ' This option allows the user to set a minimum size for the computation for the average radii, in the same order as the netParam option (default is 0).',
 'perfHandler': ' Which set of performance handlers to use. (default = os, available dummy,os,papi).',
 'vizHandler': ' Which set of handlers to use for the visualization. (default = dummy, available std,dummy).',
 'petscArgs': ' All the arguments that will be given to PETSc. See PETSc Options.',
 'rng': " Allows user to specify seed used to initialize random number generator (default = determined from current time) and whether each process should print the seed value it uses (default = don't print).",
 'pulse': ' The total length of the pulse (in s) if the Pulsed material is used, and the proportion of it that is ON.',
 'lattice': ' The length of the lattice side in nm.',
 'impurityRadius': ' The radius of the main impurity (He or Xe) in nm.',
 'biasFactor': ' This option allows the user to set the bias factor reflecting the fact that interstitial clusters have a larger surrounding strain field.',
 'hydrogenFactor': ' The factor between the size of He and H.',
 'xenonDiffusivity': ' The diffusion coefficient for xenon in nm2 s-1.',
 'fissionYield': ' The number of xenon created for each fission (default is 0.25).',
 'heVRatio': ' The number of He atoms allowed per V in a bubble.',
 'migrationThreshold': ' Set a limit on the migration energy above which the diffusion will be ignored.'}
class XolotlFlux():    
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
            
    @classinstancemethod
    def _write_flux_file(self,filename,time,flux):
        assert time.shape == flux.shape
        np.savetxt(filename,np.vstack((time,flux)).T)
        
    @classinstancemethod
    def set_flux_file(self,filename=None):
        if filename is None:
            filename = 'influx.txt'        
        self.input_files['fluxfile'] = os.path.join(self.tmp_folder,filename)
        self.input_params['fluxFile'] = os.path.basename(filename)

class XolotlTridyn():
    
    @classinstancemethod
    def set_tridyn(self, filename=None):
        assert hasattr(self,'input_tridyn')
        self.set_tridyn_file(filename)
        if self.input_files.get('tridynfile') is not None:
            self.write_tridyn_file(self.input_files['tridynfile'], self.input_tridyn)
            
    @classinstancemethod
    def set_tridyn_file(self,filename=None):
        if filename is None:
            if self.input_params.get('fluxDepthProfileFilePath') is None:
                filename = 'tridyn.txt' 
            elif self.input_params.get('fluxDepthProfileFilePath')=='':
                self.input_params.pop('fluxDepthProfileFilePath')
                self.input_files['tridynfile'] = None
                return
            else:
                filename = os.path.basename(self.input_params['fluxDepthProfileFilePath'])
        self.input_params['fluxDepthProfileFilePath'] = filename        
        self.input_files['tridynfile'] = os.path.join(self.tmp_folder,filename)
            
            
    @classinstancemethod
    def write_tridyn_file(self,filename, dic):
        f = open(filename,'w')
        for k,v in dic.items():
            f.write('{} {} {}\n'.format(k,v['charge'],v['fraction']))
            f.write('{} {}\n'.format(' '.join([str(c) for c in v['coeff']]),v['cutoff']))
        f.close()

    
    @classinstancemethod
    def read_tridyn_file(self,filename):
        lines = self._read_file(filename)
        nspecies = len(lines) //2
        print('tridyn file: {} nspecies:{}'.format(filename,nspecies))
        d = {}
        for i in range(nspecies):
          (s,q,f) = lines[2*(i+1)-2].split('#')[0].rstrip().split()
          coeffs = lines[2*(i+1)-1].split('#')[0].rstrip().split()
          cutoff = coeffs[-1]
          coeffs = coeffs[:-1]
          d[s] = {'charge':q,'fraction':f,'coeff':coeffs,'cutoff':cutoff}
        return d
    
    @classinstancemethod
    def load_tridyn_file(self,filename):
        self.input_tridyn = self.read_tridyn_file(filename)
        self.input_params['fluxDepthProfileFilePath'] = filename

class XolotlInput(XolotlFlux, XolotlTridyn):
    def __init__(self, paramdef_file='/fusion/projects/boundary/guterlj/parameters_def.txt'):
       super(XolotlInput, self).__init__()
       self.def_params = param_def #self.read_paramdef(paramdef_file)
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
            
    @classinstancemethod        
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
             L.append(k+'='+" ".join([str(vv) for vv in v]))
            elif type(v) == str:
                 L.append(k+'='+v)
            elif type(v) == dict:
                L.append(k+'='+" ".join(['-'+kk+" "+str(vv) for kk,vv in v.items()]))
            else:
                 L.append(k+'='+str(v))
            
        return L
    
    @classinstancemethod
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
         


    
    
    

        
        
        
            
    
            
            
            
    