"""
Read MD3D output files and plot temperature and position of the particle.
"""
import os
import modelling_earth as me
import matplotlib.pyplot as plt

# Get path to the MD3D output directory
script_path = os.path.dirname(os.path.abspath(__file__))
md3d_output_path = os.path.join(script_path, "run")
output_path = os.path.join(script_path, "output")

# Read and save the particles position
position, time = me.read_swarm(path=md3d_output_path, save=True, save_path=output_path)
# Take the particle position for time=0 linked to index 0
position_0 = position[0]
# Filter the number of particles
position_fil = position_0[position_0.cc0 % 10 == 0]


# Read the MD3D output files
data = me.read_md3d_data(md3d_output_path)

# Plot the particle position over the temperature for step=0
fig, ax = plt.subplots()
me.plot_scalar_2d(data.temperature.sel(time=0, y=0), ax=ax)
plt.plot(position_fil.x, position_fil.z, "c.", color="black", markersize=0.3)
plt.show()
