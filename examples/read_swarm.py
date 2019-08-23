"""
Read MD3D output files and plot temperature and position of the particle.
"""
import os
import modelling_earth as me
import matplotlib.pyplot as plt

# Get path to the MD3D output directory
script_path = os.path.dirname(os.path.abspath(__file__))
md3d_output_path = os.path.join(script_path, "run")

# Read the particles position
swarm = me.read_md3d_swarm(md3d_output_path)

# Take only the positions for the first step (step == 0)
swarm = swarm.loc[0]

# Reduce the number of particles to take only 2 particle per cell
swarm = swarm[swarm.cc0 < 2]

# Read the MD3D output files
data = me.read_md3d_data(md3d_output_path)

# Plot the particle position over the temperature for step=0
fig, ax = plt.subplots()
me.plot_scalar_2d(data.temperature.sel(time=0, y=0), ax=ax)
plt.scatter(swarm.x, swarm.z, s=0.1, c="black")
plt.show()
