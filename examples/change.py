"""
Converte the output files of the MD3D in x-array to save the data in netcdf 
format

"""

import numpy as np
import xarray as xr
import pandas as pd
import os
from funtions import time, dataset_2d, lagrangian_point_2d


script_path = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(script_path, 'run')
netcdf_dir = os.path.join(script_path, 'netcdf')

if not os.path.isdir(netcdf_dir):
    os.makedirs(netcdf_dir)

number = 50
step = 10    

# Generate the time steps
time = time(path, number, step)
# Save
filename = "time-steps.txt"
np.save(os.path.join(netcdf_dir, filename), time)

print(time)

# Generate the dataset for each time step
dataset_list = []
for cont in range(0, number + step, step):
    dataset = dataset_2d(path, 'param_1.5.3.txt', cont)
    dataset_list = np.append(dataset_list, dataset)
    # Save the xarray as netcdf
    filename = 'time_' + str(cont) + '.nc'
    dataset.to_netcdf(os.path.join(netcdf_dir, filename))


dataset_lagrange = lagrangian_point_2d(path, number, step, rank=3)
print(dataset_lagrange)
    
