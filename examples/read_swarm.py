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

# Reduce the number of particles to take only 2 particle per cell
swarm = swarm[swarm.cc0 < 2]

# Take only the positions for the first step (step == 0)
swarm_0 = swarm.loc[10]

# Read the MD3D output files
dataset = me.read_md3d_data(md3d_output_path)

# Create filter to get only the y=0 profile of the dataset
filter_profile = {"y": 0}

## Plot the particle position over the temperature for step=0
fig, ax = plt.subplots()
me.plot_scalar_2d(dataset.temperature.sel(time=0, **filter_profile), ax=ax)
me.plot_swarm_2d(swarm_0, ax=ax)
plt.show()

# Plot all temperatures and particle position for every time and save the figures
figs_dir = os.path.join(script_path, "_figures")
if not os.path.isdir(figs_dir):
    os.mkdir(figs_dir)
me.save_plots_2d(
    dataset.sel(**filter_profile),
    figs_dir,
    filename="temper_particle",
    swarm=swarm,
    scalar_to_plot="temperature",
    plot_velocity=False,
)
