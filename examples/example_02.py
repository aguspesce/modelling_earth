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


#Generate the 2D dataset for the time step 0
data = read_md3d_data(path, step=0)

## Generate the lagrangian particle for the time step 0
particle = lagrangian_point(path, step=0, rank=3)
# Extract the position of the particles
x_particle = particle.x_position.values
z_particle = particle.z_position.values


# Plot temperature and the particles
plt.figure(figsize=(10 * 2, 2.5 * 2))
data.temperature.sel(y=0).plot.contourf(levels=np.arange(0, 2000,10))
plt.plot(x_particle, z_particle, "c.", color="black", markersize=0.3)
plt.title("run/Time: %8.2f Ma"%tempo[0])
plt.show()

# Plot the temperature and velocity with arrows

# One way to do it
# Extract the velocity data
x = data.x.values
z = data.z.values
v_x = data.velocity_x.sel(y=0).values
v_z = data.velocity_z.sel(y=0).values
xx, zz = np.meshgrid(x,z)
xx_n = xx[::4, ::4]   
zz_n = zz[::4, ::4]   
v_x_n = v_x[::4, ::4]   
v_z_n = v_z[::4, ::4]
# Plot
plt.figure(figsize=(10 * 2, 2.5 * 2))
data.temperature.sel(y=0).plot.contourf(levels=np.arange(0, 2000,10))
plt.quiver(xx[::4, ::4], zz[::4, ::4], v_x[::4, ::4], v_z[::4, ::4])
plt.title("run/Time: %8.2f Ma"%tempo[0])
plt.show()

# Other way to do it
plt.figure(figsize=(10 * 2, 2.5 * 2))
data.temperature.sel(y=0).plot.contourf(levels=np.arange(0, 2000,10))
plot_quiver_2d(dataset, filter=4)
plt.title("run/Time: %8.2f Ma"%tempo[0])
plt.show()
