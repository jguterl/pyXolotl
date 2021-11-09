#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  5 12:16:59 2021

@author: jguterl
"""

import h5py, time, os
Dfile='/global/cscratch1/sd/jguterl/Xolotl/data/D_modif/ELM_p/ELM_1/xolotlStop.h5'
#src='/global/cscratch1/sd/jguterl/Xolotl/data/He_loading/600K/runlong2b_1/xolotlStop_refurbish.h5'

def copy_h5file(src,dest=None):
    src = os.path.expanduser(src)
    if dest is None:
        dest = os.path.join(os.path.dirname(src),'xolotlStop_refurbish.h5')
     
    print('copying {} into {}'.format(src,dest))
    os.popen('cp {} {}'.format(src,dest))
    time.sleep(3)
    return os.path.abspath(dest)
def get_grp_attrs(filename):
    if filename is not None:
        data = h5py.File(filename,'r')
        list_attrs = list(data['concentrationsGroup']['concentration_0'].attrs.keys())
        data.close()
        print('List of concentration group attributes',list_attrs)
        return list_attrs
    else:
        return []

def add_grp_attrs(filename,list_attrs):
    
    data = h5py.File(filename,'r+')
    
    for k,g in data['concentrationsGroup'].items():
        print(k,g)
        for a in list_attrs:
            if g is not None and g.attrs.get(a) is None:
                g.attrs[a] = 0
    data.close()
def upgrade_h5file(h5file,attrs_file=None,dest=None):
    

    dest = copy_h5file(h5file, dest)
    list_attrs = get_grp_attrs(attrs_file)
    if list_attrs != []:
        add_grp_attrs(dest,list_attrs)
    return dest
    
    
def reset_time(h5file, time=0.0, dt=1e-10):
    print('resetting {}'.format(h5file))
    data = h5py.File(h5file,'r+')
    lastTimeStep = data['concentrationsGroup'].attrs['lastTimeStep']
    print('Resetting timestep in concentration_{}'.format(lastTimeStep))
    data['concentrationsGroup']['concentration_{}'.format(lastTimeStep)].attrs['absoluteTime'] = time
    data['concentrationsGroup']['concentration_{}'.format(lastTimeStep)].attrs['deltaTime'] = dt
    data['concentrationsGroup']['concentration_{}'.format(lastTimeStep)].attrs['previousTime'] = max(0,time-dt)
    data.close()


src='/global/cscratch1/sd/jguterl/Xolotl/data/D_modif/ELM_p/ELM_1_test/xolotlStop.h5'
dest = copy_h5file(src)
#reset_time(dest)
h5file = dest
print('resetting {}'.format(h5file))
data = h5py.File(h5file,'r+',driver=None)
lastTimeStep = data['concentrationsGroup'].attrs['lastTimeStep']
time = 0.0
dt = 1e-10
print('Resetting timestep in concentration_{}'.format(lastTimeStep))
data['concentrationsGroup']['concentration_{}'.format(lastTimeStep)].attrs['absoluteTime'] = time
data['concentrationsGroup']['concentration_{}'.format(lastTimeStep)].attrs['deltaTime'] = dt
#data['concentrationsGroup']['concentration_{}'.format(lastTimeStep)].attrs['previousTime'] = max(0,time-dt)
data.close()




    
    