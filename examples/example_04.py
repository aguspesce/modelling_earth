import os
import numpy as np
import xarray as xr
import modelling_earth as me
import matplotlib.pyplot as plt

# Get path to the MD3D output directory
script_path = os.path.dirname(os.path.abspath(__file__))
md3d_output_path = os.path.join(script_path, 'run')

# Read the particles
list_frame = me.read_swarm(md3d_output_path)
# Take the particle position for step=0
frame_0 = list_frame[0]

# Read the MD3D output files
data = me.read_md3d_data(md3d_output_path)

# Plot the particle position over the temperature for step=0
plt.figure(figsize=(10 * 2, 2.5 * 2))
plot_args = {"x": "x", "y": "z"}
data.temperature.sel(time=0, y=0).plot.pcolormesh(**plot_args)
plt.plot(frame_0.x[frame_0.cc0%10==0],
         frame_0.z[frame_0.cc0%10==0],"c.",
         color="black", markersize=0.3
         ) # With [frame_0.cc0%10==0] filter the number of particles to plot
plt.show()
