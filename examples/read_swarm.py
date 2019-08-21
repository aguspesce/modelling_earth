"""
Read MD3D output files and plot temperature and position of the particle.
"""
import os
import modelling_earth as me
import matplotlib.pyplot as plt

# Get path to the MD3D output directory
script_path = os.path.dirname(os.path.abspath(__file__))
md3d_output_path = os.path.join(script_path, "run")
output_path = os.path.join(script_path, "_output")

# Read the particles position
swarm = me.read_swarm(path=md3d_output_path)
# Save the particle position
me.save_swarm(swarm, 'particle', output_path)

# Take the particle position for time=0 linked to index 0
positions = swarm["positions"]
positions = positions[0]

# Filter the number of particles to take only 2 particle per cell
positions = positions[positions.cc0 < 2]

# Read the MD3D output files
data = me.read_md3d_data(md3d_output_path)

# Plot the particle position over the temperature for step=0
fig, ax = plt.subplots()
me.plot_scalar_2d(data.temperature.sel(time=0, y=0), ax=ax)
plt.scatter(positions.x, positions.z, s=0.2, color='black', alpha=0.3)
plt.show()
