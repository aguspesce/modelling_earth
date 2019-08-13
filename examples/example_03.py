"""
Read MD3D output files and plot the velocity and the temperature data with
created functions in the repository.
"""
import os
import matplotlib.pyplot as plt
import modelling_earth as me

# Get path to the MD3D output directory
script_path = os.path.dirname(os.path.abspath(__file__))
md3d_output_path = os.path.join(script_path, "run")

# Read the MD3D output files
dataset = me.read_md3d_data(md3d_output_path)

# Create filter to get only the y=0 profile of the dataset
filter_profile = {"y": 0}

# Plot single frame (for t=0)
fig, ax = plt.subplots()
me.plot_scalar_2d(dataset.temperature.sel(time=0, **filter_profile), ax=ax)
me.plot_velocity_2d(dataset.sel(time=0, **filter_profile), ax=ax, slice_grid=(4, 3))
ax.ticklabel_format(axis='both', style='sci', scilimits=(0, 0))
ax.set_aspect("equal")
plt.show()

# Plot all temperatures and velocities for every time and save the figures
figs_dir = os.path.join(script_path, "_figures")
if not os.path.isdir(figs_dir):
    os.mkdir(figs_dir)
me.save_plots_2d(dataset.sel(**filter_profile), figs_dir, scalar_to_plot="temperature")
