#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  5 12:16:59 2021

@author: jguterl
"""

import h5py, time
Dfile='/global/u2/j/jguterl/simulations/Xolotl/D_modif/ELM_p/ELM_1/xolotlStop.h5'
src='/global/cscratch1/sd/jguterl/Xolotl/data/He_loading/600K/runlong2b_1/xolotlStop_refurbish.h5'

def upgrade_h5file(h5file,attrs_file,dest=None):
    
    def copy_h5file(src,dest=None):
        if dest is None:
            dest = os.path.join(os.path.dirname(src),'xolotlStop_refurbish.h5')
        print('copying {} into {}'.format(src,dest))
        os.popen('cp {} {}'.format(src,dest))
        time.sleep(3)
        return os.path.abspath(dest)
    def get_grp_attrs(filename):
        data = h5py.File(filename,'r')
        list_attrs = list(data['concentrationsGroup']['concentration_0'].attrs.keys())
        data.close()
        print('List of concentration group attributes',list_attrs)
        return list_attrs
    
    def add_grp_attrs(filename,list_attrs):
        
        data = h5py.File(filename,'r+')
        
        for k,g in data['concentrationsGroup'].items():
            print(k,g)
            for a in list_attrs:
                if g is not None and g.attrs.get(a) is None:
                    g.attrs[a] = 0
        data.close()
    dest = copy_h5file(h5file, dest)
    list_attrs = get_grp_attrs(attrs_file)
    add_grp_attrs(dest,list_attrs)
    
    
def reset_time(h5file, time=0.0, dt=1e-10):
    data = h5py.File(h5file,'r+')
    lastTimeStep = data['concentrationsGroup'].attrs['lastTimeStep']
    print('Resetting timestep in concentration_{}'.format(lastTimeStep))
    data['concentrationsGroup']['concentration_{}'.format(lastTimeStep)].attrs['absoluteTime'] = time
    data['concentrationsGroup']['concentration_{}'.format(lastTimeStep)].attrs['deltaTime'] = dt
    data['concentrationsGroup']['concentration_{}'.format(lastTimeStep)].attrs['previousTime'] = time-dt
    data.close()


src='/global/cscratch1/sd/jguterl/Xolotl/data/He_loading/600K/runlong2b_1/xolotlStop_refurbish.h5'
reset_time(src)



    
    