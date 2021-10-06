#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 10 21:59:00 2021

@author: guterlj
"""
import glob
import os.path
import h5py
import numpy as np
from XolotlPlot import *
class classinstancemethod(classmethod):
    def __get__(self, instance, type_):
        descr_get = super().__get__ if instance is None else self.__func__.__get__
        return descr_get(instance, type_)

class XolotlOutput(XolotlPlot):
    data_files={'retention':'retentionOut.txt', 'surface':'surface.txt'}
    def __init__(self, *args, **kwargs):
        super(XolotlOutput, self).__init__(*args, **kwargs)
        self.data_files=self.__class__.data_files
        self.output = {}
        
    
    @staticmethod
    def read_header(filename):
        with open(filename,'r') as f:
            return f.readlines()[0]
        
    @staticmethod
    def process_header(header):
        header = header.strip('#').rstrip()
        return header.split(" ")
    
    @staticmethod
    def get_dict_data(fields, data):
        print(fields,data.shape)
        if len(data.shape)>1:
            return dict((f,data[:,i]) for i,f in  enumerate(fields))
        else:
            if data.shape[0] >0:
                return dict((f,data[i]) for i,f in  enumerate(fields))
            else:
                return {}
    @classinstancemethod
    def read_outputfile(self, filename):
        print('Reading output from {}'.format(filename))
        header = self.read_header(filename)
        fields = self.process_header(header)
        data = np.loadtxt(filename,skiprows=1)
        return self.get_dict_data(fields, data)
    
    @staticmethod 
    def read_profile_file(filename):
        print('Reading profiles from {}'.format(filename))
        f = h5py.File(filename)
        data={}
        concDset = f['concs']
        data['depth'] = []
        data['He'] = []
        data['D'] = []
        data['T'] = []
        data['V'] = []
        data['I'] = []
        ## Read the data and put it in lists
        for j in range(0, len(concDset)):
            data['depth'].append(concDset[j][0])
            data['He'].append(concDset[j][1]) ## 1 for He, 2 for D, 3 for T, 4 for V, 5 for I, depending on the network
            data['D'].append(concDset[j][2])
            data['T'].append(concDset[j][3])
            data['V'].append(concDset[j][4])
            data['I'].append(concDset[j][5])
        data['filename'] = filename
        return data
    @classinstancemethod
    def load_profiles(self, case_path=None, filename=None):
       
        if filename is None:
            file_type = ''
            files = glob.glob(os.path.join(case_path, 'TRIDYN_*'))
            latest_file = max(files, key=os.path.getctime)
            filename=latest_file
        else:
            filename = os.path.join(case_path,filename)
        self.output['profile'] = self.read_profile_file(filename)
        
   

    @classinstancemethod
    def load_outputfile(self,case_path):
        if not hasattr(self,'output'):
            self.output = {}
        for k,v in self.data_files.items():
            self.output[k] = self.read_outputfile(os.path.join(case_path,v)) 
    @classinstancemethod
    def load_data(self,case_path=None):
        if case_path is None:
            case_path = os.path.join(self.basefolder,self.casename)
        assert os.path.exists(case_path)
        print('Loading case {} '.format(case_path))
        self.case_path = case_path
        self.load_outputfile(case_path)
        self.load_profiles(case_path)
        self.get_flux()
        self.get_influx(casepath=case_path)
        
     
        
    @classinstancemethod     
    def get_flux(self):
        species = ['Helium', 'Deuterium', 'Vacancy', 'Interstitial']
        for s in species:
            try:
                self.output['retention']['{}_fluxb'.format(s)] = np.gradient(self.output['retention']['{}_bulk'.format(s)],self.output['retention']['time'])
            except:
                pass
            try:
                self.output['retention']['{}_fluxs'.format(s)] = np.gradient(self.output['retention']['{}_surface'.format(s)],self.output['retention']['time'])
            except:
                pass
            
    @classinstancemethod     
    def get_influx(self, filename='influx.txt', casepath=None):
            if casepath is None:
                casepath = os.path.join(self.basefolder,self.casename)
            try :
                filepath = os.path.join(casepath,filename)
                self.output['influx'] = np.loadtxt(filepath)
                print('Influx data read from {}'.format(filepath))
           
            except:
                self.output['influx'] = None
                print('Cannot read influx data from {}'.format(filepath))
            
                
            

        
def load_h5(filename):
    h5py.File(filename, 'r')
    return readh5data(f)
 
def readh5data(data):
    if hasattr(data,'keys'):
            return dict((k,readh5data(data[k])) for k in data.keys())
    else:
        return data[...]
    
    


