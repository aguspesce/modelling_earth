"""
Converte the output files of the MD3D in x-array to save the data in netcdf 
format

"""

import numpy as np
import xarray as xr
import pandas as pd
import os
import matplotlib.pyplot as plt
from modelling_earth import (coordinates, time_array, read_md3d_data,      
                     lagrangian_point)


script_path = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(script_path, 'run')

# Coordinates
coord, shape = coordinates(path)
print(shape)

# Generate the time steps file
tempo = time_array(path, number=50, step=10)
print('time in Ma:', tempo)


## Generate the lagrangian particle for the time step 0
#particle = lagrangian_point(path, step=0, rank=2)
##print(particle)

#Generate the 2D dataset for the time step 0
data = read_md3d_data(path, step=0)
# Plot temperature
temp = data.temperature
temp_2d = temp.sel(y=0)

plt.figure(figsize=(10 * 2, 2.5 * 2))
temp_2d.plot.contourf(levels=np.arange(0, 2000,10))
plt.title("run/Time: %8.2f Ma"%tempo[0])
plt.show()
